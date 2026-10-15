"""ORCHESTRA: Automated Batch Matrix Runner.

Executes experimental matrices across tasks, scalable agent populations (2, 5, 10, ...),
communication protocols, repetitions with controlled seeds, perturbations, and HITL oversight.
Automatically aggregates profiles into comparative statistical tables and figures.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from orchestra.analysis import (
    build_comparison_dataframe,
    compute_summary_statistics,
    generate_markdown_summary_table,
    plot_longitudinal_evolution,
)
from orchestra.config import ExperimentConfig
from orchestra.runner import ExperimentSummary, run_orchestra_experiment


@dataclass
class MatrixConfig:
    """Configuration for an automated multi-condition experimental matrix."""
    task_ids: List[str] = field(default_factory=lambda: ["I-01"])
    agent_counts: List[int] = field(default_factory=lambda: [2, 5])
    protocols: List[str] = field(default_factory=lambda: ["msg", "broadcast"])
    repetitions: int = 1
    base_seed: int = 42
    model: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    max_rounds: int = 15
    workspace: str = "workspace"
    perturbations: List[Optional[str]] = field(default_factory=lambda: [None])
    hitl_enabled: bool = False
    hitl_mode: str = "audit_only"


def run_batch_matrix(matrix: MatrixConfig) -> List[ExperimentSummary]:
    """Execute a full experimental matrix across conditions and repetitions."""
    print("=" * 70)
    print("ORCHESTRA BATCH EXPERIMENT MATRIX")
    print(f"Tasks: {matrix.task_ids}")
    print(f"Agent Scales: {matrix.agent_counts}")
    print(f"Protocols: {matrix.protocols}")
    print(f"Repetitions per condition: {matrix.repetitions}")
    print(f"Perturbations: {matrix.perturbations}")
    print(f"HITL Enabled: {matrix.hitl_enabled}")
    print("=" * 70)
    
    summaries: List[ExperimentSummary] = []
    case_dirs: List[Path] = []
    start_time = time.time()
    
    total_runs = (
        len(matrix.task_ids)
        * len(matrix.agent_counts)
        * len(matrix.protocols)
        * len(matrix.perturbations)
        * matrix.repetitions
    )
    run_idx = 0
    
    for task_id in matrix.task_ids:
        for n in matrix.agent_counts:
            for proto in matrix.protocols:
                for pert in matrix.perturbations:
                    for rep in range(1, matrix.repetitions + 1):
                        run_idx += 1
                        seed = matrix.base_seed + rep if matrix.base_seed else None
                        exp_id = f"{task_id}_n{n}_{proto}_rep{rep}"
                        if pert:
                            exp_id += f"_{pert}"
                            
                        print(f"\n[{run_idx}/{total_runs}] Starting: {exp_id} (seed={seed})")
                        
                        pert_params = None
                        if pert == "agent_dropout":
                            pert_params = {"round": 2, "agent_id": 1}
                            
                        cfg = ExperimentConfig(
                            task_id=task_id,
                            agent_count=n,
                            protocol=proto,
                            model=matrix.model,
                            api_base=matrix.api_base,
                            api_key=matrix.api_key,
                            max_rounds=matrix.max_rounds,
                            workspace=matrix.workspace,
                            experiment_id=exp_id,
                            seed=seed,
                            perturbation_type=pert,
                            perturbation_params=pert_params,
                            hitl_enabled=matrix.hitl_enabled,
                            hitl_mode=matrix.hitl_mode,
                        )
                        
                        try:
                            summary = run_orchestra_experiment(cfg)
                            summaries.append(summary)
                            case_dirs.append(Path(summary.case_dir))
                        except Exception as e:
                            print(f"[ORCHESTRA ERROR] Run {exp_id} failed: {e}")
                            
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"BATCH COMPLETE: {len(summaries)}/{total_runs} runs executed in {elapsed:.1f}s")
    print("=" * 70)
    
    # Aggregate and print comparative table
    if case_dirs:
        df = build_comparison_dataframe(case_dirs)
        print("\n=== Experimental Comparison Summary ===")
        print(generate_markdown_summary_table(df))
        
        # Save batch summary table
        ws_path = Path(matrix.workspace)
        ws_path.mkdir(parents=True, exist_ok=True)
        csv_file = ws_path / "batch_comparison_results.csv"
        df.to_csv(csv_file, index=False)
        print(f"\n[ORCHESTRA] Saved batch comparison CSV to {csv_file}")
        
    return summaries


def main() -> None:
    """CLI for running batch experimental matrices."""
    parser = argparse.ArgumentParser(description="ORCHESTRA Batch Matrix Runner")
    parser.add_argument("--task-ids", nargs="+", default=["I-01"], help="List of benchmark task IDs")
    parser.add_argument("--agent-counts", nargs="+", type=int, default=[2, 5], help="List of agent population sizes")
    parser.add_argument("--protocols", nargs="+", default=["msg", "broadcast"], choices=["msg", "broadcast", "sfs"])
    parser.add_argument("--repetitions", type=int, default=1, help="Repetitions per condition")
    parser.add_argument("--base-seed", type=int, default=42, help="Base random seed")
    parser.add_argument("--model", default=None, help="Model identifier")
    parser.add_argument("--api-base", default=None, help="API base URL")
    parser.add_argument("--api-key", default=None, help="API key")
    parser.add_argument("--max-rounds", type=int, default=15, help="Max rounds")
    parser.add_argument("--workspace", default="workspace", help="Workspace output dir")
    parser.add_argument("--perturbations", nargs="+", default=["none"], choices=["none", "agent_dropout", "communication_partition"])
    parser.add_argument("--hitl", action="store_true", help="Enable HITL oversight")
    parser.add_argument("--hitl-mode", default="audit_only", choices=["audit_only", "active_intervention"])
    args = parser.parse_args()
    
    perts = [None if p == "none" else p for p in args.perturbations]
    
    matrix = MatrixConfig(
        task_ids=args.task_ids,
        agent_counts=args.agent_counts,
        protocols=args.protocols,
        repetitions=args.repetitions,
        base_seed=args.base_seed,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        max_rounds=args.max_rounds,
        workspace=args.workspace,
        perturbations=perts,
        hitl_enabled=args.hitl,
        hitl_mode=args.hitl_mode,
    )
    
    run_batch_matrix(matrix)


if __name__ == "__main__":
    main()
