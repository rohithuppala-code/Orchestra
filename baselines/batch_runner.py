"""ORCHESTRA: Multi-Baseline Batch Matrix Runner.

Executes controlled multi-agent experimental matrices across:
- 6 Baselines + ORCHESTRA
- Agent scales: 2, 5, 10
- Tasks: Level I, Level II, Level III
- Control vs. Agent Dropout perturbation

Automatically aggregates all runs into a master CSV table for paper synthesis.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from baselines.runner import run_baseline_experiment
from baselines.topologies import EXTERNAL_BASELINES, SUPPORTED_BASELINES

ALL_30_TASKS = [
    f"I-{i:02d}" for i in range(1, 11)
] + [
    f"II-{i:02d}" for i in range(11, 21)
] + [
    f"III-{i:02d}" for i in range(21, 31)
]


@dataclass
class BaselineMatrixConfig:
    """Configuration for a multi-baseline experimental batch run."""
    baselines: List[str] = field(default_factory=lambda: list(EXTERNAL_BASELINES))
    task_ids: List[str] = field(default_factory=lambda: list(ALL_30_TASKS))
    agent_counts: List[int] = field(default_factory=lambda: [2, 5, 10])
    perturbations: List[Optional[str]] = field(default_factory=lambda: [None, "agent_dropout"])
    model: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    max_rounds: int = 15
    workspace: str = "workspace_baselines"
    repetitions: int = 1
    base_seed: int = 42


def run_baseline_batch(matrix: BaselineMatrixConfig) -> pd.DataFrame:
    """Execute a batch of baseline experiments across conditions."""
    ws_path = Path(matrix.workspace)
    ws_path.mkdir(parents=True, exist_ok=True)

    total_runs = (
        len(matrix.baselines)
        * len(matrix.task_ids)
        * len(matrix.agent_counts)
        * len(matrix.perturbations)
        * matrix.repetitions
    )

    print("=" * 75)
    print("  ORCHESTRA MULTI-BASELINE BENCHMARK MATRIX")
    print(f"  Baselines:    {matrix.baselines}")
    print(f"  Agent Scales: {matrix.agent_counts}")
    print(f"  Tasks:        {matrix.task_ids}")
    print(f"  Perturbations:{matrix.perturbations}")
    print(f"  Total Runs:   {total_runs}")
    print(f"  Workspace:    {matrix.workspace}")
    print("=" * 75)

    rows: List[Dict[str, Any]] = []
    run_idx = 0
    start_time = time.time()

    for task_id in matrix.task_ids:
        for n in matrix.agent_counts:
            for bname in matrix.baselines:
                for pert in matrix.perturbations:
                    for rep in range(1, matrix.repetitions + 1):
                        run_idx += 1
                        seed = matrix.base_seed + rep if matrix.base_seed else 42
                        print(f"\n[{run_idx}/{total_runs}] Running {bname.upper()} on {task_id} (N={n}, pert={pert})...")

                        try:
                            summary = run_baseline_experiment(
                                baseline_name=bname,
                                task_id=task_id,
                                num_agents=n,
                                model=matrix.model,
                                api_base=matrix.api_base,
                                api_key=matrix.api_key,
                                max_rounds=matrix.max_rounds,
                                workspace=matrix.workspace,
                                perturbation=pert,
                                seed=seed,
                            )
                            rows.append(asdict(summary))

                            # Incrementally save cumulative results CSV
                            df_interim = pd.DataFrame(rows)
                            csv_file = ws_path / "baseline_comparison_results.csv"
                            df_interim.to_csv(csv_file, index=False)

                        except Exception as e:
                            print(f"[ERROR] Failed run for {bname} on {task_id} (N={n}): {e}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"  BATCH COMPLETE: {len(rows)}/{total_runs} runs executed in {elapsed:.1f}s")
    print(f"  Master results saved to: {ws_path / 'baseline_comparison_results.csv'}")
    print("=" * 75)

    df_final = pd.DataFrame(rows)
    return df_final


def main() -> None:
    """CLI for running multi-baseline matrices."""
    parser = argparse.ArgumentParser(description="ORCHESTRA Multi-Baseline Batch Matrix Runner")
    parser.add_argument("--baselines", nargs="+", default=["all"], help="Baselines to run ('all', 'external', or list)")
    parser.add_argument("--task-ids", nargs="+", default=["all"], help="Task IDs (e.g. I-01, II-11, III-21 or 'all')")
    parser.add_argument("--agent-counts", nargs="+", type=int, default=[2, 5, 10], help="Agent population sizes")
    parser.add_argument("--perturbations", nargs="+", default=["none", "agent_dropout"], choices=["none", "agent_dropout"])
    parser.add_argument("--model", default=None, help="Model identifier")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--max-rounds", type=int, default=15)
    parser.add_argument("--workspace", default="workspace_baselines")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--base-seed", type=int, default=42)
    args = parser.parse_args()

    # Expand baselines
    b_args = [b.lower() for b in args.baselines]
    if "all" in b_args or "external" in b_args:
        baselines = list(EXTERNAL_BASELINES)
    elif "all_with_orchestra" in b_args:
        baselines = list(SUPPORTED_BASELINES.keys())
    else:
        baselines = b_args

    # Expand task IDs
    task_ids = args.task_ids
    if any(t.lower() == "all" for t in task_ids):
        task_ids = list(ALL_30_TASKS)

    perts = [None if p == "none" else p for p in args.perturbations]

    cfg = BaselineMatrixConfig(
        baselines=baselines,
        task_ids=task_ids,
        agent_counts=args.agent_counts,
        perturbations=perts,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        max_rounds=args.max_rounds,
        workspace=args.workspace,
        repetitions=args.repetitions,
        base_seed=args.base_seed,
    )

    run_baseline_batch(cfg)


if __name__ == "__main__":
    main()
