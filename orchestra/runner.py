"""ORCHESTRA Experiment Runner & Execution Controller.

Integrates with SILO-BENCH execution engine to execute experiments, apply
pluggable perturbations, monitor HITL intervention boundaries in real-time,
and automatically capture round-by-round organizational instrumentation.
Supports configurable agent populations, models, and protocols.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Ensure workspace root and silo-bench root are in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SILO_BENCH_ROOT = WORKSPACE_ROOT / "silo-bench"
if str(SILO_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(SILO_BENCH_ROOT))
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from src.engine import evaluate, init_case, run_round
from orchestra.config import ExperimentConfig
from orchestra.hitl import HITLMode, HITLSupervisor
from orchestra.instrumentation import (
    OrganizationalProfile,
    extract_case_instrumentation,
    extract_round_snapshot,
    save_orchestra_instrumentation,
)
from orchestra.perturbations import BasePerturbation, create_perturbation


@dataclass
class ExperimentSummary:
    """Complete summary of an ORCHESTRA experimental run."""
    experiment_id: str
    case_dir: str
    task_id: str
    num_agents: int
    protocol: str
    model: str
    total_time_seconds: float
    total_rounds: int
    status: str  # 'completed', 'terminated_early', 'failed'
    success: bool
    success_rate: float
    partial_correctness: float
    token_consumption: float
    communication_density: float
    
    # Organizational metrics summary
    gini_out_degree: float
    gini_in_degree: float
    mean_structural_drift: float
    agent_roles: Dict[int, str]
    
    # Perturbation / Intervention summary
    perturbation_applied: Optional[str] = None
    hitl_violations_count: int = 0
    hitl_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    seed: Optional[int] = None


def run_orchestra_experiment(
    config: ExperimentConfig,
    on_round_complete: Optional[Callable[[int, str], None]] = None,
) -> ExperimentSummary:
    """Execute an end-to-end ORCHESTRA experiment with automated instrumentation."""
    start_time = time.time()
    config.validate()
    
    # 1. Resolve task file and model configuration
    task_file_path = config.resolve_task_file()
    model_cfg = config.resolve_model_config()
    
    # 2. Initialize case via SILO-BENCH engine
    case_dir = init_case(
        task_file=str(task_file_path),
        protocol=config.protocol,
        model=model_cfg["model"],
        api_base=model_cfg["api_base"],
        api_key=model_cfg["api_key"],
        max_rounds=config.max_rounds,
        workspace=config.workspace,
    )
    
    case_path = Path(case_dir)
    print(f"[ORCHESTRA] Initialized case: {case_path.name}")
    print(f"[ORCHESTRA] Task: {task_file_path.name} | Protocol: {config.protocol} | Model: {model_cfg['model']}")
    
    # Read metadata to get task specifics
    with open(case_path / "metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    num_agents = meta["config"]["agent_count"]
    task_id = meta["task"]["case_id"]
    
    # 3. Instantiate Perturbation and HITL hooks
    perturbation = create_perturbation(config.perturbation_type, config.perturbation_params)
    if perturbation:
        print(f"[ORCHESTRA] Configured perturbation: {perturbation.name()}")
        
    hitl_supervisor: Optional[HITLSupervisor] = None
    if config.hitl_enabled:
        hitl_params = config.hitl_params or {}
        hitl_supervisor = HITLSupervisor(
            mode=config.hitl_mode,
            monopolization_threshold=float(hitl_params.get("monopolization_threshold", 0.85)),
            max_isolated_rounds=int(hitl_params.get("max_isolated_rounds", 2)),
            stagnation_threshold_rounds=int(hitl_params.get("stagnation_threshold_rounds", 3)),
        )
        print(f"[ORCHESTRA] Configured HITL Supervisor (mode: {config.hitl_mode})")
        
    completed_rounds = 0
    done = False
    exec_status = "completed"
    error_msg: Optional[str] = None
    
    # 4. Round execution loop with error handling
    try:
        for r in range(1, config.max_rounds + 1):
            round_start = time.time()
            print(f"[ORCHESTRA] Executing Round {r}/{config.max_rounds} (agents={num_agents})...")
            
            # Pre-round perturbation hook
            if perturbation:
                pre_res = perturbation.apply_pre_round(case_path, r, num_agents)
                if pre_res.get("applied"):
                    print(f"[ORCHESTRA] Pre-round perturbation applied at round {r}: {pre_res}")
                    
            # Run benchmark round
            done = run_round(str(case_path))
            completed_rounds = r
            
            # Post-round perturbation hook
            if perturbation:
                post_res = perturbation.apply_post_round(case_path, r, num_agents)
                if post_res.get("applied"):
                    print(f"[ORCHESTRA] Post-round perturbation applied at round {r}: {post_res}")
                    
            # Extract instantaneous round snapshot for real-time monitoring
            try:
                snapshot = extract_round_snapshot(
                    case_dir=case_path,
                    round_num=r,
                    num_agents=num_agents,
                    protocol=config.protocol,
                )
                if hitl_supervisor:
                    violations = hitl_supervisor.inspect_round(case_path, snapshot)
                    if violations:
                        print(f"[ORCHESTRA HITL] Detected {len(violations)} boundary violation(s) at round {r}")
            except Exception as e:
                print(f"[ORCHESTRA] Warning: could not extract real-time snapshot at round {r}: {e}")
                
            round_duration = time.time() - round_start
            print(f"[ORCHESTRA] Round {r} finished in {round_duration:.1f}s.")
            
            if on_round_complete:
                on_round_complete(r, str(case_path))
                
            if done:
                print(f"[ORCHESTRA] Convergence/termination condition reached at Round {r}.")
                break
                
    except Exception as e:
        exec_status = "failed"
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"[ORCHESTRA ERROR] Run failed during round execution: {error_msg}")
        traceback.print_exc()
        
    total_time = time.time() - start_time
    
    # 5. Evaluate benchmark outcomes if completed
    results_file = case_path / "results.json"
    if not results_file.exists() and exec_status != "failed":
        try:
            evaluate(str(case_path))
        except Exception as e:
            print(f"[ORCHESTRA] Warning: evaluate() raised exception: {e}")
            
    # 6. Extract comprehensive Organizational Instrumentation
    try:
        profile = extract_case_instrumentation(case_path)
        save_orchestra_instrumentation(profile, case_path / "orchestra_profile.json")
        print(f"[ORCHESTRA] Saved organizational profile to {case_path / 'orchestra_profile.json'}")
    except Exception as e:
        print(f"[ORCHESTRA] Warning: could not extract full profile: {e}")
        profile = OrganizationalProfile(
            case_id=case_path.name,
            task_id=task_id,
            protocol=config.protocol,
            num_agents=num_agents,
            total_rounds=completed_rounds,
        )
        
    hitl_summary = hitl_supervisor.get_summary() if hitl_supervisor else None
    
    summary = ExperimentSummary(
        experiment_id=config.experiment_id or case_path.name,
        case_dir=str(case_path),
        task_id=task_id,
        num_agents=num_agents,
        protocol=config.protocol,
        model=model_cfg["model"],
        total_time_seconds=total_time,
        total_rounds=completed_rounds,
        status=exec_status,
        success=profile.success,
        success_rate=profile.success_rate,
        partial_correctness=profile.partial_correctness,
        token_consumption=profile.token_consumption,
        communication_density=profile.communication_density,
        gini_out_degree=profile.gini_out_degree,
        gini_in_degree=profile.gini_in_degree,
        mean_structural_drift=profile.mean_structural_drift,
        agent_roles=profile.agent_roles,
        perturbation_applied=config.perturbation_type,
        hitl_violations_count=hitl_summary["total_violations"] if hitl_summary else 0,
        hitl_summary=hitl_summary,
        error_message=error_msg,
        seed=config.seed,
    )
    
    with open(case_path / "orchestra_summary.json", "w", encoding="utf-8") as sf:
        json.dump(asdict(summary), sf, indent=2)
        
    print(f"[ORCHESTRA] Experiment Summary saved to {case_path / 'orchestra_summary.json'}")
    print(f"  Status: {summary.status} | Success: {summary.success} (Rate: {summary.success_rate:.0%})")
    print(f"  Duration: {summary.total_time_seconds:.1f}s across {summary.total_rounds} rounds")
    print(f"  Gini Out-Degree: {summary.gini_out_degree:.3f} | Roles: {summary.agent_roles}")
    if hitl_summary:
        print(f"  HITL Violations: {hitl_summary['total_violations']}")
        
    return summary


def main() -> None:
    """CLI entry point for running ORCHESTRA experiments."""
    parser = argparse.ArgumentParser(description="ORCHESTRA Experiment Runner")
    parser.add_argument("--task-file", default=None, help="Path to benchmark task JSON file")
    parser.add_argument("--task-id", default=None, help="Benchmark task ID (e.g., I-01, II-11, III-21)")
    parser.add_argument("--agent-count", type=int, default=None, help="Number of agents (2, 5, 10, 20, 50, 100)")
    parser.add_argument("--protocol", default="msg", choices=["msg", "broadcast", "sfs"], help="Communication protocol")
    parser.add_argument("--model", default=None, help="Model identifier (defaults to env or config)")
    parser.add_argument("--api-base", default=None, help="Model inference API base URL")
    parser.add_argument("--api-key", default=None, help="Model inference API key")
    parser.add_argument("--max-rounds", type=int, default=15, help="Maximum rounds to execute")
    parser.add_argument("--workspace", default="workspace", help="Workspace output directory")
    parser.add_argument("--perturbation", default=None, choices=["agent_dropout", "communication_partition", "message_corruption", "none"])
    parser.add_argument("--drop-round", type=int, default=2, help="Round to trigger agent dropout")
    parser.add_argument("--drop-agent", type=int, default=1, help="Agent ID to drop")
    parser.add_argument("--hitl", action="store_true", help="Enable HITL oversight monitoring")
    parser.add_argument("--hitl-mode", default="audit_only", choices=["audit_only", "active_intervention"])
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()
    
    perturbation_params = None
    if args.perturbation == "agent_dropout":
        perturbation_params = {"round": args.drop_round, "agent_id": args.drop_agent}
        
    cfg = ExperimentConfig(
        task_file=args.task_file,
        task_id=args.task_id,
        agent_count=args.agent_count,
        protocol=args.protocol,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        max_rounds=args.max_rounds,
        workspace=args.workspace,
        seed=args.seed,
        perturbation_type=args.perturbation if args.perturbation != "none" else None,
        perturbation_params=perturbation_params,
        hitl_enabled=args.hitl,
        hitl_mode=args.hitl_mode,
    )
    
    run_orchestra_experiment(cfg)


if __name__ == "__main__":
    main()
