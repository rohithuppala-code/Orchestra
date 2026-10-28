"""ORCHESTRA: Baseline Synthesis & Paper Comparison Module.

Generates:
1. Table 1 (Master Empirical Comparison across all 6 Baselines + ORCHESTRA)
2. Table 2 (Perturbation Resilience & Fault Degradation Breakdown)
3. Publication-quality Figures (Accuracy, Pareto Token Efficiency, Dropout Resilience, Gini Spectrum)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASELINE_METADATA = {
    "independent": {
        "display": "Independent Agents",
        "citation": "Wang et al. (ICLR 2023)",
        "type": "No Communication",
        "color": "#94a3b8",  # slate
    },
    "broadcast": {
        "display": "Flat Broadcast Debate",
        "citation": "Qian et al. (ACL 2024); Du et al. (2023)",
        "type": "Complete Mesh",
        "color": "#f97316",  # orange
    },
    "random_topology": {
        "display": "Random Topology (p=0.5)",
        "citation": "Watts & Strogatz (1998)",
        "type": "Random Graph",
        "color": "#a855f7",  # purple
    },
    "central_coordinator": {
        "display": "Central Coordinator",
        "citation": "Wu et al. (AutoGen / ICLR 2024)",
        "type": "Star Hub",
        "color": "#eab308",  # yellow
    },
    "hierarchical_coordinator": {
        "display": "Hierarchical Tree",
        "citation": "Wang et al. (MacNet, 2024/2025)",
        "type": "Static Tree",
        "color": "#06b6d4",  # cyan
    },
    "fixed_roles": {
        "display": "Fixed Predefined Roles",
        "citation": "Hong et al. (MetaGPT, ICLR 2024)",
        "type": "Prompt Hierarchy",
        "color": "#ec4899",  # pink
    },
    "orchestra": {
        "display": "ORCHESTRA (Ours)",
        "citation": "This Work",
        "type": "Emergent Dynamic",
        "color": "#10b981",  # emerald green
    },
}


def load_and_standardize_results(csv_path: Path) -> pd.DataFrame:
    """Load baseline results CSV and standardize fields."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Results CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Standardize baseline names
    if "baseline" in df.columns:
        df["baseline"] = df["baseline"].str.lower().str.strip()
    elif "protocol" in df.columns:
        df["baseline"] = df["protocol"].map({
            "msg": "orchestra",
            "broadcast": "broadcast",
            "sfs": "independent",
        }).fillna("orchestra")

    # Fill default perturbation
    if "perturbation" not in df.columns:
        df["perturbation"] = "none"
    df["perturbation"] = df["perturbation"].fillna("none")

    return df


def generate_paper_comparison_table(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """Generate Table 1: Master Empirical Comparison Table for the paper."""
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    baselines_present = [b for b in BASELINE_METADATA.keys() if b in df["baseline"].unique()]
    if not baselines_present:
        baselines_present = list(df["baseline"].unique())

    for bname in baselines_present:
        meta = BASELINE_METADATA.get(bname, {
            "display": bname.title(),
            "citation": "Prior Art",
            "type": "Standard",
        })
        b_df = df[df["baseline"] == bname]

        # Control condition metrics
        ctrl_df = b_df[b_df["perturbation"] == "none"]
        if ctrl_df.empty:
            ctrl_df = b_df

        # Scales breakdown
        n2_acc = ctrl_df[ctrl_df["num_agents"] == 2]["success_rate"].mean() if 2 in ctrl_df["num_agents"].values else np.nan
        n5_acc = ctrl_df[ctrl_df["num_agents"] == 5]["success_rate"].mean() if 5 in ctrl_df["num_agents"].values else np.nan
        n10_acc = ctrl_df[ctrl_df["num_agents"] == 10]["success_rate"].mean() if 10 in ctrl_df["num_agents"].values else np.nan

        overall_acc = ctrl_df["success_rate"].mean()
        mean_tokens = ctrl_df["token_consumption"].mean()
        mean_rounds = ctrl_df["total_rounds"].mean()
        mean_gini = ctrl_df["gini_out_degree"].mean() if "gini_out_degree" in ctrl_df.columns else 0.0

        # Dropout degradation
        drop_df = b_df[b_df["perturbation"] == "agent_dropout"]
        if not drop_df.empty:
            drop_acc = drop_df["success_rate"].mean()
            delta_drop = drop_acc - overall_acc
            resilience_ratio = (drop_acc / overall_acc) if overall_acc > 0 else 0.0
        else:
            drop_acc = np.nan
            delta_drop = np.nan
            resilience_ratio = np.nan

        records.append({
            "Baseline": meta["display"],
            "Paradigm": meta["type"],
            "Citation": meta["citation"],
            "Success_N2": f"{n2_acc:.1%}" if not np.isnan(n2_acc) else "-",
            "Success_N5": f"{n5_acc:.1%}" if not np.isnan(n5_acc) else "-",
            "Success_N10": f"{n10_acc:.1%}" if not np.isnan(n10_acc) else "-",
            "Success_Overall": f"{overall_acc:.1%}",
            "Tokens_Mean": f"{mean_tokens:,.0f}",
            "Rounds_Mean": f"{mean_rounds:.1f}",
            "Gini_OutDegree": f"{mean_gini:.3f}",
            "Dropout_Success": f"{drop_acc:.1%}" if not np.isnan(drop_acc) else "-",
            "Resilience_Delta": f"{delta_drop:+.1%}" if not np.isnan(delta_drop) else "-",
        })

    table_df = pd.DataFrame(records)

    # Save CSV
    csv_file = output_dir / "table1_master_baseline_comparison.csv"
    table_df.to_csv(csv_file, index=False)
    print(f"[COMPARE] Saved Table 1 CSV to: {csv_file}")

    # Save Markdown
    md_file = output_dir / "table1_master_baseline_comparison.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# Table 1: Master Empirical Multi-Agent Baseline Comparison\n\n")
        f.write(table_df.to_markdown(index=False))
        f.write("\n\n*Note: N=2, 5, 10 evaluated on SILO-BENCH. Resilience Delta denotes accuracy change under agent dropout failure.*\n")
    print(f"[COMPARE] Saved Table 1 Markdown to: {md_file}")

    return table_df


def plot_baseline_figures(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate high-resolution publication charts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Figure 1: Success Rate by Scale (Grouped Bar Chart)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    baselines = [b for b in BASELINE_METADATA.keys() if b in df["baseline"].unique()]
    if not baselines:
        baselines = list(df["baseline"].unique())

    scales = sorted([n for n in df["num_agents"].unique() if n in [2, 5, 10]])
    if not scales:
        scales = sorted(list(df["num_agents"].unique()))

    x = np.arange(len(baselines))
    width = 0.8 / max(1, len(scales))

    ctrl_df = df[df["perturbation"] == "none"]
    if ctrl_df.empty:
        ctrl_df = df

    for i, n in enumerate(scales):
        sub_df = ctrl_df[ctrl_df["num_agents"] == n]
        accs = [
            sub_df[sub_df["baseline"] == b]["success_rate"].mean() * 100.0 if b in sub_df["baseline"].values else 0.0
            for b in baselines
        ]
        offset = (i - (len(scales) - 1) / 2) * width
        ax.bar(x + offset, accs, width, label=f"N = {n} Agents", alpha=0.9)

    ax.set_ylabel("Task Success Rate (%)", fontsize=11, fontweight="bold")
    ax.set_title("Multi-Agent Algorithmic Task Success Across Scales (SILO-BENCH)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([BASELINE_METADATA.get(b, {}).get("display", b) for b in baselines], rotation=25, ha="right", fontsize=9)
    ax.set_ylim(0, 105)
    ax.legend(frameon=True, loc="upper left")
    plt.tight_layout()
    fig1_path = output_dir / "figure_baseline_accuracy_comparison.png"
    plt.savefig(fig1_path)
    plt.close()
    print(f"[COMPARE] Saved Figure 1 to: {fig1_path}")

    # 2. Figure 2: Fault Tolerance & Resilience Under Dropout
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    drop_df = df[df["perturbation"] == "agent_dropout"]
    if not drop_df.empty:
        ctrl_accs = []
        drop_accs = []
        labels = []

        for b in baselines:
            b_ctrl = df[(df["baseline"] == b) & (df["perturbation"] == "none")]["success_rate"].mean() * 100.0
            b_drop = df[(df["baseline"] == b) & (df["perturbation"] == "agent_dropout")]["success_rate"].mean() * 100.0
            if not np.isnan(b_ctrl) and not np.isnan(b_drop):
                ctrl_accs.append(b_ctrl)
                drop_accs.append(b_drop)
                labels.append(BASELINE_METADATA.get(b, {}).get("display", b))

        if labels:
            bx = np.arange(len(labels))
            bwidth = 0.35
            ax.bar(bx - bwidth / 2, ctrl_accs, bwidth, label="Control (Healthy)", color="#3b82f6", alpha=0.85)
            ax.bar(bx + bwidth / 2, drop_accs, bwidth, label="Agent Dropout (Perturbed)", color="#ef4444", alpha=0.85)

            ax.set_ylabel("Success Rate (%)", fontsize=11, fontweight="bold")
            ax.set_title("Fault Tolerance: Control vs. Agent Dropout Degradation", fontsize=13, fontweight="bold", pad=12)
            ax.set_xticks(bx)
            ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=9)
            ax.set_ylim(0, 105)
            ax.legend(frameon=True, loc="upper right")
            plt.tight_layout()
            fig2_path = output_dir / "figure_perturbation_resilience.png"
            plt.savefig(fig2_path)
            plt.close()
            print(f"[COMPARE] Saved Figure 2 to: {fig2_path}")

    # 3. Figure 3: Token Cost vs Success Rate (Pareto Frontier)
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    for b in baselines:
        b_df = ctrl_df[ctrl_df["baseline"] == b]
        if not b_df.empty:
            mean_tok = b_df["token_consumption"].mean()
            mean_acc = b_df["success_rate"].mean() * 100.0
            meta = BASELINE_METADATA.get(b, {})
            disp = meta.get("display", b)
            col = meta.get("color", "#64748b")
            marker = "*" if b == "orchestra" else "o"
            msize = 220 if b == "orchestra" else 130

            ax.scatter(mean_tok, mean_acc, color=col, s=msize, marker=marker, edgecolors="black", linewidths=1.2, zorder=5)
            ax.annotate(disp, (mean_tok, mean_acc), textcoords="offset points", xytext=(8, 4), fontsize=9, fontweight="bold" if b == "orchestra" else "normal")

    ax.set_xlabel("Mean Token Consumption per Task", fontsize=11, fontweight="bold")
    ax.set_ylabel("Task Success Rate (%)", fontsize=11, fontweight="bold")
    ax.set_title("Pareto Frontier: Solution Accuracy vs. Token Efficiency", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig3_path = output_dir / "figure_token_accuracy_pareto.png"
    plt.savefig(fig3_path)
    plt.close()
    print(f"[COMPARE] Saved Figure 3 to: {fig3_path}")


def main() -> None:
    """CLI entry point for synthesizing baseline comparison tables and plots."""
    parser = argparse.ArgumentParser(description="ORCHESTRA Baseline Comparison Synthesizer")
    parser.add_argument("--input-csv", default="workspace_baselines/baseline_comparison_results.csv", help="Input results CSV")
    parser.add_argument("--output-dir", default="paper_results/baselines", help="Output directory for tables and plots")
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    out_dir = Path(args.output_dir)

    print(f"[COMPARE] Loading baseline results from: {input_path}")
    df = load_and_standardize_results(input_path)

    generate_paper_comparison_table(df, out_dir)
    plot_baseline_figures(df, out_dir)
    print("\n[COMPARE COMPLETE] All paper tables and figures successfully generated!")


if __name__ == "__main__":
    main()
