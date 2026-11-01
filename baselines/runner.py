"""ORCHESTRA: Dedicated Multi-Agent Baseline Experiment Runner.

Executes controlled baseline experiments (Independent, Broadcast, Random,
Central Coordinator, Hierarchical Tree, Fixed Roles, and ORCHESTRA)
across configurable agent scales (2, 5, 10), recording full telemetry,
token consumption, structural Gini, and disruption resilience.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SILO_BENCH_ROOT = WORKSPACE_ROOT / "silo-bench"
if str(SILO_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(SILO_BENCH_ROOT))
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from src.engine import evaluate, init_case, run_round  # type: ignore[import-not-found]
from orchestra.config import ExperimentConfig
from orchestra.instrumentation import (
    extract_case_instrumentation,
    extract_round_snapshot,
    save_orchestra_instrumentation,
)
from orchestra.perturbations import create_perturbation
from baselines.topologies import (
    SUPPORTED_BASELINES,
    BaseTopologyEnforcer,
    create_baseline_topology,
)


@dataclass
class BaselineRunSummary:
    """Complete summary of a single baseline experimental run."""
    case_id: str
    baseline: str
    citation: str
    task_id: str
    num_agents: int
    protocol: str
    model: str
    total_time_seconds: float
    total_rounds: int
    status: str
    success: bool
    success_rate: float
    partial_correctness: float
    token_consumption: float
    communication_density: float
    gini_out_degree: float
    gini_in_degree: float
    mean_structural_drift: float
    perturbation: Optional[str] = None
    seed: Optional[int] = None
    error_message: Optional[str] = None


def run_baseline_experiment(
    baseline_name: str,
    task_id: str,
    num_agents: int,
    model: Optional[str] = None,
    api_base: Optional[str] = None,
    api_key: Optional[str] = None,
    max_rounds: int = 15,
    workspace: str = "workspace_baselines",
    perturbation: Optional[str] = None,
    drop_round: int = 2,
    drop_agent: int = 1,
    seed: int = 42,
) -> BaselineRunSummary:
    """Execute a single baseline run and record organizational & performance metrics."""
    start_time = time.time()
    bname = baseline_name.lower().strip()

    # Determine protocol: broadcast baseline uses 'broadcast', others use 'msg' (P2P routing)
    protocol = "broadcast" if bname == "broadcast" else "msg"

    # Configure experiment
    pert_type = perturbation if perturbation and perturbation != "none" else None
    pert_params = {"round": drop_round, "agent_id": drop_agent} if pert_type == "agent_dropout" else None

    cfg = ExperimentConfig(
        task_id=task_id,
        agent_count=num_agents,
        protocol=protocol,
        model=model,
        api_base=api_base,
        api_key=api_key,
        max_rounds=max_rounds,
        workspace=workspace,
        seed=seed,
        perturbation_type=pert_type,
        perturbation_params=pert_params,
    )
    cfg.validate()

    task_file_path = cfg.resolve_task_file()
    model_cfg = cfg.resolve_model_config()

    # Initialize case
    case_dir = init_case(
        task_file=str(task_file_path),
        protocol=protocol,
        model=model_cfg["model"],
        api_base=model_cfg["api_base"],
        api_key=model_cfg["api_key"],
        max_rounds=max_rounds,
        workspace=workspace,
    )
    case_path = Path(case_dir)

    print(f"\n[BASELINE RUNNER] Case: {case_path.name}")
    print(f"  Baseline: {bname.upper()} | Agents: {num_agents} | Task: {task_id} | Perturbation: {pert_type}")

    # Instantiate topology enforcer and perturbation hook
    topology_enforcer: BaseTopologyEnforcer = create_baseline_topology(bname, seed=seed)
    init_res = topology_enforcer.apply_initialization(case_path, num_agents)
    if init_res.get("applied"):
        print(f"  Topology initialized: {init_res}")

    perturbation_hook = create_perturbation(pert_type, pert_params)

    completed_rounds = 0
    done = False
    exec_status = "completed"
    error_msg: Optional[str] = None

    try:
        for r in range(1, max_rounds + 1):
            # Pre-round hooks
            if perturbation_hook:
                perturbation_hook.apply_pre_round(case_path, r, num_agents)
            topology_enforcer.apply_pre_round(case_path, r, num_agents)

            # Execute round
            done = run_round(str(case_path))
            completed_rounds = r

            # Post-round hooks
            if perturbation_hook:
                perturbation_hook.apply_post_round(case_path, r, num_agents)
            top_post = topology_enforcer.apply_post_round(case_path, r, num_agents)
            if top_post.get("dropped_messages", 0) > 0:
                print(f"  Round {r}: Topology filtered {top_post['dropped_messages']} message(s).")

            # Extract instantaneous round snapshot
            try:
                extract_round_snapshot(
                    case_dir=case_path,
                    round_num=r,
                    num_agents=num_agents,
                    protocol=protocol,
                )
            except Exception:
                pass

            if done:
                print(f"  Converged / terminated at Round {r}.")
                break

    except Exception as e:
        exec_status = "failed"
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"[ERROR] Baseline run failed: {error_msg}")
        traceback.print_exc()

    total_time = time.time() - start_time

    # Evaluate benchmark outcomes
    results_file = case_path / "results.json"
    if not results_file.exists() and exec_status != "failed":
        try:
            evaluate(str(case_path))
        except Exception as e:
            print(f"  Warning: evaluate() raised: {e}")

    # Extract comprehensive Organizational Instrumentation
    try:
        profile = extract_case_instrumentation(case_path)
        save_orchestra_instrumentation(profile, case_path / "orchestra_profile.json")
    except Exception as e:
        print(f"  Warning: could not extract full profile: {e}")
        from orchestra.instrumentation import OrganizationalProfile
        profile = OrganizationalProfile(
            case_id=case_path.name,
            task_id=task_id,
            protocol=protocol,
            num_agents=num_agents,
            total_rounds=completed_rounds,
        )

    summary = BaselineRunSummary(
        case_id=case_path.name,
        baseline=bname,
        citation=topology_enforcer.citation,
        task_id=task_id,
        num_agents=num_agents,
        protocol=protocol,
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
        perturbation=pert_type,
        seed=seed,
        error_message=error_msg,
    )

    with open(case_path / "baseline_summary.json", "w", encoding="utf-8") as sf:
        json.dump(asdict(summary), sf, indent=2)

    print(f"  Result: Success={summary.success} (Rate: {summary.success_rate:.0%}) | Rounds={summary.total_rounds} | Tokens={summary.token_consumption:.0f} | Gini={summary.gini_out_degree:.3f}")
    return summary


def main() -> None:
    """CLI entry point for running a single baseline experiment."""
    parser = argparse.ArgumentParser(description="ORCHESTRA Baseline Experiment Runner")
    parser.add_argument("--baseline", default="central_coordinator", choices=list(SUPPORTED_BASELINES.keys()))
    parser.add_argument("--task-id", default="I-01", help="Task ID (e.g. I-01, II-11, III-21)")
    parser.add_argument("--agent-count", type=int, default=5, choices=[2, 5, 10, 20])
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--max-rounds", type=int, default=15)
    parser.add_argument("--workspace", default="workspace_baselines")
    parser.add_argument("--perturbation", default="none", choices=["none", "agent_dropout"])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_baseline_experiment(
        baseline_name=args.baseline,
        task_id=args.task_id,
        num_agents=args.agent_count,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        max_rounds=args.max_rounds,
        workspace=args.workspace,
        perturbation=args.perturbation,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
