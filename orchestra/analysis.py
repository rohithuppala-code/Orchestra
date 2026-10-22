"""ORCHESTRA: Comparative Organizational Analysis & Visualization Module.

Aggregates profiles across experimental runs, generates statistical comparison
tables, computes structure-performance correlations, and produces publication-ready
visualizations of network topologies, longitudinal structural drift, and behavioral specialization.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


def load_case_profile(case_dir: str | Path) -> Dict[str, Any]:
    """Load the orchestra_profile.json from a case directory."""
    prof_file = Path(case_dir) / "orchestra_profile.json"
    if not prof_file.exists():
        raise FileNotFoundError(f"orchestra_profile.json not found in {case_dir}")
    with open(prof_file, "r", encoding="utf-8") as f:
        return json.load(f)


def build_comparison_dataframe(case_dirs: List[str | Path]) -> pd.DataFrame:
    """Build a comparative DataFrame across multiple experiment runs."""
    rows = []
    for cdir in case_dirs:
        try:
            p = load_case_profile(cdir)
            rows.append({
                "case_id": p.get("case_id"),
                "task_id": p.get("task_id"),
                "protocol": p.get("protocol"),
                "num_agents": p.get("num_agents"),
                "total_rounds": p.get("total_rounds"),
                "success": p.get("success"),
                "success_rate": p.get("success_rate", 0.0),
                "partial_correctness": p.get("partial_correctness", 0.0),
                "token_consumption": p.get("token_consumption", 0.0),
                "communication_density": p.get("communication_density", 0.0),
                "gini_out_degree": p.get("gini_out_degree", 0.0),
                "gini_in_degree": p.get("gini_in_degree", 0.0),
                "mean_structural_drift": p.get("mean_structural_drift", 0.0),
                "final_network_entropy": p.get("final_network_entropy", 0.0),
                "network_diameter": p.get("network_diameter"),
                "is_connected": p.get("is_connected", False),
            })
        except Exception as e:
            print(f"Warning: could not load profile from {cdir}: {e}")
            
    return pd.DataFrame(rows)


def compute_summary_statistics(df: pd.DataFrame, group_by: Optional[List[str]] = None) -> pd.DataFrame:
    """Compute aggregate mean and standard deviation across experimental conditions."""
    if df.empty:
        return pd.DataFrame()
        
    group_cols = group_by or ["task_id", "protocol", "num_agents"]
    metric_cols = [
        "total_rounds", "success_rate", "partial_correctness",
        "token_consumption", "communication_density",
        "gini_out_degree", "gini_in_degree", "mean_structural_drift"
    ]
    # Filter to existing columns
    available_metrics = [c for c in metric_cols if c in df.columns]
    
    grouped = df.groupby(group_cols)[available_metrics].agg(["mean", "std", "count"]).reset_index()
    return grouped


def compute_structural_performance_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlation matrix between organizational metrics and task outcomes."""
    if len(df) < 3:
        return pd.DataFrame()  # Insufficient samples for meaningful correlation
        
    org_metrics = ["gini_out_degree", "gini_in_degree", "mean_structural_drift", "communication_density"]
    perf_metrics = ["success_rate", "partial_correctness", "token_consumption", "total_rounds"]
    
    available_org = [c for c in org_metrics if c in df.columns]
    available_perf = [c for c in perf_metrics if c in df.columns]
    
    corr_matrix = pd.DataFrame(index=available_org, columns=available_perf, dtype=float)
    for org in available_org:
        for perf in available_perf:
            corr_matrix.loc[org, perf] = df[org].corr(df[perf])
            
    return corr_matrix


# Backward-compatible alias
compute_structure_performance_correlations = compute_structural_performance_correlations


def generate_markdown_summary_table(df: pd.DataFrame) -> str:
    """Format comparison DataFrame into GitHub markdown table."""
    if df.empty:
        return "*No experimental profiles found.*"
        
    cols = [
        "task_id", "protocol", "num_agents", "total_rounds",
        "success_rate", "gini_out_degree", "mean_structural_drift",
        "token_consumption", "communication_density"
    ]
    available_cols = [c for c in cols if c in df.columns]
    sub_df = df[available_cols].copy()
    
    if "success_rate" in sub_df.columns:
        sub_df["success_rate"] = sub_df["success_rate"].apply(lambda x: f"{x:.0%}" if pd.notnull(x) else "N/A")
    if "gini_out_degree" in sub_df.columns:
        sub_df["gini_out_degree"] = sub_df["gini_out_degree"].apply(lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A")
    if "mean_structural_drift" in sub_df.columns:
        sub_df["mean_structural_drift"] = sub_df["mean_structural_drift"].apply(lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A")
    if "token_consumption" in sub_df.columns:
        sub_df["token_consumption"] = sub_df["token_consumption"].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A")
    if "communication_density" in sub_df.columns:
        sub_df["communication_density"] = sub_df["communication_density"].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
        
    return sub_df.to_markdown(index=False)


def plot_longitudinal_evolution(case_dirs: List[str | Path], output_png: str | Path) -> None:
    """Plot round-by-round cumulative density and structural drift across cases."""
    valid_profiles = []
    for cdir in case_dirs:
        try:
            valid_profiles.append(load_case_profile(cdir))
        except Exception:
            pass
            
    if not valid_profiles:
        print("[ORCHESTRA] No valid case profiles for longitudinal plotting.")
        return
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    for p in valid_profiles:
        label = f"{p['task_id']} ({p['protocol']}, n={p['num_agents']})"
        snapshots = p.get("snapshots", [])
        rounds = [s["round_num"] for s in snapshots]
        densities = [s["cumulative_density"] for s in snapshots]
        drifts = [s["jaccard_distance_from_prev"] for s in snapshots]
        
        ax1.plot(rounds, densities, marker="o", label=label, linewidth=2)
        ax2.plot(rounds, drifts, marker="s", label=label, linewidth=2)
        
    ax1.set_title("Cumulative Network Density Evolution", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Round Number", fontsize=11)
    ax1.set_ylabel("Density (0 to 1)", fontsize=11)
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="best", fontsize=10)
    
    ax2.set_title("Round-over-Round Structural Drift (Jaccard)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Round Number", fontsize=11)
    ax2.set_ylabel("Jaccard Distance from Prev Round", fontsize=11)
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="best", fontsize=10)
    
    plt.tight_layout()
    out_path = Path(output_png)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[ORCHESTRA] Saved longitudinal plot to {out_path}")


def plot_communication_topology(case_dir: str | Path, output_png: str | Path) -> None:
    """Draw the cumulative directed communication topology graph for a case."""
    p = load_case_profile(case_dir)
    n = p["num_agents"]
    
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    
    for s in p.get("snapshots", []):
        for edge in s.get("edges", []):
            u, v, w = edge["from"], edge["to"], edge.get("weight", 1)
            if G.has_edge(u, v):
                G[u][v]["weight"] += w
            else:
                G.add_edge(u, v, weight=w)
                
    plt.figure(figsize=(8, 7))
    pos = nx.circular_layout(G)
    
    role_colors = {
        "Hub_Coordinator": "#e74c3c",       # Red
        "Broadcaster_Disseminator": "#e67e22", # Orange
        "Aggregator_Collector": "#9b59b6",  # Purple
        "Peer_Collaborator": "#2ecc71",    # Green
        "Isolated": "#95a5a6",             # Gray
    }
    
    roles = p.get("agent_roles", {})
    node_colors = [role_colors.get(roles.get(str(i), roles.get(i, "Peer_Collaborator")), "#3498db") for i in range(n)]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors="black", linewidths=2)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold", font_color="white")
    
    weights = [G[u][v].get("weight", 1) * 2 for u, v in G.edges()]
    nx.draw_networkx_edges(
        G,
        pos,
        width=weights if weights else 1.5,
        edge_color="#34495e",
        arrows=True,
        arrowsize=20,
        connectionstyle="arc3,rad=0.15",
    )
    
    title = f"Emergent Topology: {p['case_id']}\nProtocol: {p['protocol']} | Agents: {n} | Success: {p['success']}"
    plt.title(title, fontsize=12, fontweight="bold")
    plt.axis("off")
    
    out_path = Path(output_png)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[ORCHESTRA] Saved topology plot to {out_path}")


def main() -> None:
    """CLI for analyzing completed ORCHESTRA cases in a workspace."""
    parser = argparse.ArgumentParser(description="ORCHESTRA Comparative Analysis")
    parser.add_argument("--workspace", default=None, help="Path to workspace directory containing case folders")
    parser.add_argument("--case-dirs", nargs="+", default=[], help="Specific case directories to analyze")
    parser.add_argument("--output-dir", default="orchestra/figures", help="Directory to save figures and tables")
    args = parser.parse_args()
    
    case_paths: List[Path] = []
    if args.case_dirs:
        case_paths.extend([Path(d) for d in args.case_dirs])
        
    if args.workspace:
        wpath = Path(args.workspace)
        if wpath.exists():
            for child in wpath.iterdir():
                if child.is_dir() and (child / "orchestra_profile.json").exists():
                    case_paths.append(child)
                    
    if not case_paths:
        print("[ORCHESTRA] No case directories with orchestra_profile.json found.")
        return
        
    df = build_comparison_dataframe(case_paths)
    print("\n=== ORCHESTRA Comparative Summary Table ===")
    print(generate_markdown_summary_table(df))
    print()
    
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save CSV
    csv_file = out_dir / "comparison_results.csv"
    df.to_csv(csv_file, index=False)
    print(f"[ORCHESTRA] Saved comparative CSV to {csv_file}")
    
    # Save structure-performance correlations
    corr = compute_structural_performance_correlations(df)
    if not corr.empty:
        corr_file = out_dir / "structure_performance_correlations.csv"
        corr.to_csv(corr_file)
        print(f"[ORCHESTRA] Saved correlations to {corr_file}")
        
    # Generate longitudinal plot
    plot_longitudinal_evolution(case_paths, out_dir / "longitudinal_comparison.png")


if __name__ == "__main__":
    main()
