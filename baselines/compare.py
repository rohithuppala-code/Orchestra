"""ORCHESTRA: Baseline Synthesis & Paper Comparison Module.

Generates:
1. Table 1 (Master Empirical Comparison across all 6 Baselines + ORCHESTRA)
2. Table 2 (Perturbation Resilience & Fault Degradation Breakdown)
3. Publication-quality Figures (Accuracy, Pareto Token Efficiency, Dropout Resilience, Gini Spectrum)
"""

from __future__ import annotations

import argparse
from pathlib import Path

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


def load_and_standardize_results(csv_input: list[Path] | Path) -> pd.DataFrame:
    """Load one or multiple baseline results CSVs and standardize fields."""
    paths: list[Path] = [csv_input] if isinstance(csv_input, Path) else csv_input
    dfs: list[pd.DataFrame] = []

    for p in paths:
        if p.is_dir():
            candidates = list(p.glob("*.csv"))
            for c in candidates:
                try:
                    dfs.append(pd.read_csv(c))
                except Exception:
                    pass
        elif p.exists():
            try:
                dfs.append(pd.read_csv(p))
            except Exception:
                pass

    if not dfs:
        raise FileNotFoundError(f"No valid results CSVs found in input: {csv_input}")

    df = pd.concat(dfs, ignore_index=True)

    # Standardize baseline column
    if "baseline" not in df.columns:
        df["baseline"] = np.nan

    # For any row where baseline is null/nan/empty or literal "nan", infer from protocol
    mask_missing = (
        df["baseline"].isna()
        | df["baseline"].astype(str).str.lower().isin(["nan", "none", "", "null"])
    )
    if mask_missing.any():
        if "protocol" in df.columns:
            proto_s = df.loc[mask_missing, "protocol"].astype(str).str.lower().str.strip()
            df.loc[mask_missing & (proto_s == "msg"), "baseline"] = "orchestra"
            df.loc[mask_missing & (proto_s == "broadcast"), "baseline"] = "broadcast"
            df.loc[mask_missing & (proto_s == "sfs"), "baseline"] = "orchestra_sfs"
        df.loc[mask_missing & df["baseline"].isna(), "baseline"] = "orchestra"

    df["baseline"] = df["baseline"].fillna("orchestra").astype(str).str.lower().str.strip()
    df.loc[df["baseline"].isin(["nan", "none", "", "null"]), "baseline"] = "orchestra"

    # Standardize perturbation column
    if "perturbation" not in df.columns:
        df["perturbation"] = np.nan
    if "perturbation_applied" in df.columns:
        df["perturbation"] = df["perturbation"].fillna(df["perturbation_applied"])
    if "case_id" in df.columns:
        is_drop = df["case_id"].astype(str).str.contains("agent_dropout|dropout", case=False, na=False)
        df.loc[is_drop, "perturbation"] = "agent_dropout"

    df["perturbation"] = df["perturbation"].fillna("none").astype(str).str.lower().str.strip()
    df.loc[df["perturbation"].isin(["null", "", "nan"]), "perturbation"] = "none"

    return df


def generate_paper_comparison_table(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """Generate Table 1: Master Empirical Comparison Table for the paper."""
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    unique_baselines = set(df["baseline"].astype(str).tolist())
    baselines_present = [b for b in BASELINE_METADATA if b in unique_baselines]
    if not baselines_present:
        baselines_present = list(unique_baselines)

    for bname in baselines_present:
        meta = BASELINE_METADATA.get(bname, {
            "display": bname.title(),
            "citation": "Prior Art",
            "type": "Standard",
        })
        b_df = df[df["baseline"] == bname]

        # Control condition metrics
        ctrl_df = b_df[b_df["perturbation"] == "none"]
        if len(ctrl_df) == 0:
            ctrl_df = b_df

        # Scales breakdown
        agents_list = ctrl_df["num_agents"].tolist()
        n2_acc = float(ctrl_df[ctrl_df["num_agents"] == 2]["success_rate"].mean()) if 2 in agents_list else np.nan
        n5_acc = float(ctrl_df[ctrl_df["num_agents"] == 5]["success_rate"].mean()) if 5 in agents_list else np.nan
        n10_acc = float(ctrl_df[ctrl_df["num_agents"] == 10]["success_rate"].mean()) if 10 in agents_list else np.nan

        overall_acc = float(ctrl_df["success_rate"].mean())
        mean_tokens = float(ctrl_df["token_consumption"].mean())
        mean_rounds = float(ctrl_df["total_rounds"].mean())
        mean_gini = float(ctrl_df["gini_out_degree"].mean()) if "gini_out_degree" in ctrl_df else 0.0

        # Dropout degradation
        drop_df = b_df[b_df["perturbation"] == "agent_dropout"]
        if len(drop_df) > 0:
            drop_acc = float(drop_df["success_rate"].mean())
            delta_drop = drop_acc - overall_acc
        else:
            drop_acc = np.nan
            delta_drop = np.nan

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
        f.write(str(table_df.to_markdown(index=False)))
        f.write("\n\n*Note: N=2, 5, 10 evaluated on SILO-BENCH. Resilience Delta denotes accuracy change under agent dropout failure.*\n")
    print(f"[COMPARE] Saved Table 1 Markdown to: {md_file}")

    return table_df


def generate_scale_breakdown_table(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """Generate Table 2: Detailed Evaluation Metrics by Agent Scale (N=2, 5, 10)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ctrl_df = df[df["perturbation"] == "none"]
    if len(ctrl_df) == 0:
        ctrl_df = df

    records = []
    unique_baselines = set(df["baseline"].astype(str).tolist())
    baselines = [b for b in BASELINE_METADATA if b in unique_baselines] or list(unique_baselines)
    
    unique_scales = sorted([int(n) for n in df["num_agents"].unique() if n in [2, 5, 10]])
    if not unique_scales:
        unique_scales = sorted([int(n) for n in df["num_agents"].unique()])

    for bname in baselines:
        meta = BASELINE_METADATA.get(bname, {"display": bname.title()})
        b_df = ctrl_df[ctrl_df["baseline"] == bname]
        for n in unique_scales:
            sub = b_df[b_df["num_agents"] == n]
            if len(sub) == 0:
                continue
            records.append({
                "Baseline": meta["display"],
                "Scale_N": n,
                "Runs": len(sub),
                "Success_Rate": f"{float(sub['success_rate'].mean()):.1%}",
                "Partial_Correctness": f"{float(sub['partial_correctness'].mean()):.3f}" if "partial_correctness" in sub else "-",
                "Avg_Tokens": f"{float(sub['token_consumption'].mean()):,.0f}",
                "Avg_Rounds": f"{float(sub['total_rounds'].mean()):.2f}",
                "Gini_Hierarchy": f"{float(sub['gini_out_degree'].mean()):.3f}" if "gini_out_degree" in sub else "-",
                "Comm_Density": f"{float(sub['communication_density'].mean()):.3f}" if "communication_density" in sub else "-",
                "Avg_Latency_s": f"{float(sub['total_time_seconds'].mean()):.1f}" if "total_time_seconds" in sub else "-",
            })

    table_df = pd.DataFrame(records)
    csv_file = output_dir / "table2_metrics_by_agent_scale.csv"
    table_df.to_csv(csv_file, index=False)
    md_file = output_dir / "table2_metrics_by_agent_scale.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# Table 2: Detailed Evaluation Metrics Across Agent Scales (N=2, 5, 10)\n\n")
        f.write(str(table_df.to_markdown(index=False)))
        f.write("\n\n*Evaluated under healthy conditions (perturbation=none).*\n")
    print(f"[COMPARE] Saved Table 2 to: {csv_file}")
    return table_df


def generate_complexity_tier_table(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """Generate Table 3: Performance Across Algorithmic Hardness Tiers (Level I, II, III)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ctrl_df = df[df["perturbation"] == "none"].copy()
    if len(ctrl_df) == 0:
        ctrl_df = df.copy()

    def get_tier(t: str) -> str:
        t = str(t)
        if t.startswith("I-"):
            return "Level I (Aggregation)"
        elif t.startswith("II-"):
            return "Level II (Mesh Routing)"
        elif t.startswith("III-"):
            return "Level III (Global Shuffle)"
        return "Unknown"

    ctrl_df["complexity_tier"] = [get_tier(t) for t in ctrl_df["task_id"].tolist()]
    tiers = ["Level I (Aggregation)", "Level II (Mesh Routing)", "Level III (Global Shuffle)"]

    records = []
    unique_baselines = set(df["baseline"].astype(str).tolist())
    baselines = [b for b in BASELINE_METADATA if b in unique_baselines] or list(unique_baselines)

    for bname in baselines:
        meta = BASELINE_METADATA.get(bname, {"display": bname.title()})
        b_df = ctrl_df[ctrl_df["baseline"] == bname]
        for tier in tiers:
            sub = b_df[b_df["complexity_tier"] == tier]
            if len(sub) == 0:
                continue
            records.append({
                "Baseline": meta["display"],
                "Complexity_Tier": tier,
                "Runs": len(sub),
                "Success_Rate": f"{float(sub['success_rate'].mean()):.1%}",
                "Partial_Correctness": f"{float(sub['partial_correctness'].mean()):.3f}" if "partial_correctness" in sub else "-",
                "Avg_Tokens": f"{float(sub['token_consumption'].mean()):,.0f}",
                "Avg_Rounds": f"{float(sub['total_rounds'].mean()):.2f}",
                "Gini_Hierarchy": f"{float(sub['gini_out_degree'].mean()):.3f}" if "gini_out_degree" in sub else "-",
            })

    table_df = pd.DataFrame(records)
    csv_file = output_dir / "table3_task_complexity_breakdown.csv"
    table_df.to_csv(csv_file, index=False)
    md_file = output_dir / "table3_task_complexity_breakdown.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# Table 3: Performance Breakdown by Algorithmic Complexity Tier\n\n")
        f.write(str(table_df.to_markdown(index=False)))
        f.write("\n\n*Task Tiers: Level I (1-10), Level II (11-20), Level III (21-30).*\n")
    print(f"[COMPARE] Saved Table 3 to: {csv_file}")
    return table_df


def generate_perturbation_resilience_table(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """Generate Table 4: Fault-Tolerance & Perturbation Resilience Breakdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    unique_baselines = set(df["baseline"].astype(str).tolist())
    baselines = [b for b in BASELINE_METADATA if b in unique_baselines] or list(unique_baselines)

    for bname in baselines:
        meta = BASELINE_METADATA.get(bname, {"display": bname.title()})
        b_ctrl = df[(df["baseline"] == bname) & (df["perturbation"] == "none")]
        b_drop = df[(df["baseline"] == bname) & (df["perturbation"] == "agent_dropout")]

        ctrl_acc = float(b_ctrl["success_rate"].mean()) if len(b_ctrl) > 0 else np.nan
        drop_acc = float(b_drop["success_rate"].mean()) if len(b_drop) > 0 else np.nan
        delta = drop_acc - ctrl_acc if not np.isnan(ctrl_acc) and not np.isnan(drop_acc) else np.nan

        ctrl_tok = float(b_ctrl["token_consumption"].mean()) if len(b_ctrl) > 0 else np.nan
        drop_tok = float(b_drop["token_consumption"].mean()) if len(b_drop) > 0 else np.nan
        delta_tok = ((drop_tok - ctrl_tok) / ctrl_tok) if not np.isnan(ctrl_tok) and ctrl_tok > 0 and not np.isnan(drop_tok) else np.nan

        records.append({
            "Baseline": meta["display"],
            "Healthy_Accuracy": f"{ctrl_acc:.1%}" if not np.isnan(ctrl_acc) else "-",
            "Dropout_Accuracy": f"{drop_acc:.1%}" if not np.isnan(drop_acc) else "-",
            "Accuracy_Delta": f"{delta:+.1%}" if not np.isnan(delta) else "-",
            "Healthy_Tokens": f"{ctrl_tok:,.0f}" if not np.isnan(ctrl_tok) else "-",
            "Dropout_Tokens": f"{drop_tok:,.0f}" if not np.isnan(drop_tok) else "-",
            "Token_Delta": f"{delta_tok:+.1%}" if not np.isnan(delta_tok) else "-",
        })

    table_df = pd.DataFrame(records)
    csv_file = output_dir / "table4_perturbation_resilience_breakdown.csv"
    table_df.to_csv(csv_file, index=False)
    md_file = output_dir / "table4_perturbation_resilience_breakdown.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# Table 4: Fault Tolerance and Agent Dropout Degradation Breakdown\n\n")
        f.write(str(table_df.to_markdown(index=False)))
        f.write("\n\n*Agent Dropout: Node dropped at Round 2 during active coordination.*\n")
    print(f"[COMPARE] Saved Table 4 to: {csv_file}")
    return table_df


def plot_baseline_figures(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate high-resolution publication charts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Figure 1: Success Rate by Scale (Grouped Bar Chart)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    unique_baselines = set(df["baseline"].astype(str).tolist())
    baselines = [b for b in BASELINE_METADATA if b in unique_baselines]
    if not baselines:
        baselines = list(unique_baselines)

    scales = sorted([n for n in df["num_agents"].unique() if n in [2, 5, 10]])
    if not scales:
        scales = sorted([int(x) for x in df["num_agents"].unique()])

    x = np.arange(len(baselines))
    width = 0.8 / max(1, len(scales))

    ctrl_df = df[df["perturbation"] == "none"]
    if len(ctrl_df) == 0:
        ctrl_df = df

    for i, n in enumerate(scales):
        sub_df = ctrl_df[ctrl_df["num_agents"] == n]
        sub_baselines = sub_df["baseline"].tolist()
        accs = [
            float(sub_df[sub_df["baseline"] == b]["success_rate"].mean() * 100.0) if b in sub_baselines else 0.0
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
    plt.close(fig)
    print(f"[COMPARE] Saved Figure 1 to: {fig1_path}")

    # 2. Figure 2: Fault Tolerance & Resilience Under Dropout
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    drop_df = df[df["perturbation"] == "agent_dropout"]
    if len(drop_df) > 0:
        ctrl_accs = []
        drop_accs = []
        labels = []

        for b in baselines:
            b_ctrl = float(df[(df["baseline"] == b) & (df["perturbation"] == "none")]["success_rate"].mean() * 100.0)
            b_drop = float(df[(df["baseline"] == b) & (df["perturbation"] == "agent_dropout")]["success_rate"].mean() * 100.0)
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
            plt.close(fig)
            print(f"[COMPARE] Saved Figure 2 to: {fig2_path}")

    # 3. Figure 3: Token Cost vs Success Rate (Pareto Frontier)
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    for b in baselines:
        b_df = ctrl_df[ctrl_df["baseline"] == b]
        if len(b_df) > 0:
            mean_tok = float(b_df["token_consumption"].mean())
            mean_acc = float(b_df["success_rate"].mean() * 100.0)
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
    plt.close(fig)
    print(f"[COMPARE] Saved Figure 3 to: {fig3_path}")


def main() -> None:
    """CLI entry point for synthesizing baseline comparison tables and plots."""
    parser = argparse.ArgumentParser(description="ORCHESTRA Baseline Comparison Synthesizer")
    parser.add_argument("--input-csv", nargs="+", default=["workspace_baselines/baseline_comparison_results.csv"], help="One or more input results CSVs or folders")
    parser.add_argument("--output-dir", default="paper_results/baselines", help="Output directory for tables and plots")
    args = parser.parse_args()

    input_paths = [Path(p) for p in args.input_csv]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[COMPARE] Loading baseline results from: {[str(p) for p in input_paths]}")
    df = load_and_standardize_results(input_paths)

    # Save combined master CSV of all runs across all scales
    master_csv = out_dir / "master_baseline_results.csv"
    df.to_csv(master_csv, index=False)
    print(f"[COMPARE] Saved combined multi-scale results CSV to: {master_csv}")

    generate_paper_comparison_table(df, out_dir)
    generate_scale_breakdown_table(df, out_dir)
    generate_complexity_tier_table(df, out_dir)
    generate_perturbation_resilience_table(df, out_dir)
    plot_baseline_figures(df, out_dir)
    print("\n[COMPARE COMPLETE] All 4 paper tables and 3 figures successfully generated!")


if __name__ == "__main__":
    main()
