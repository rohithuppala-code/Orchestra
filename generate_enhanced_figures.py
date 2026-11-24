# -*- coding: utf-8 -*-
"""
Generate 5 publication-grade, high-clarity plots for IEEE Access paper.
Fonts and line widths are specifically scaled to be large, crisp, and fully legible
when scaled down to a single column (3.5 inches) in IEEE two-column format.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

out_dir = Path(r"c:\Users\sairo\OneDrive\Documents\UROP\IEEE_Access_journal")
out_dir.mkdir(parents=True, exist_ok=True)

# Common styling parameters optimized for IEEE Access single-column width (3.5 in)
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 13,
    "font.weight": "bold",
    "axes.labelsize": 14,
    "axes.labelweight": "bold",
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "xtick.labelsize": 12.5,
    "ytick.labelsize": 12.5,
    "legend.fontsize": 11.5,
    "figure.titlesize": 16,
    "figure.titleweight": "bold",
    "lines.linewidth": 2.6,
    "lines.markersize": 9,
    "axes.linewidth": 1.4,
})

# Harmonious, high-contrast publication palette
C_ORCHESTRA = "#059669" # Emerald green
C_AUTOGEN = "#d97706"   # Amber/Brown
C_MACNET = "#0284c7"    # Ocean Blue
C_BROADCAST = "#ea580c" # Rust Orange
C_INDEP = "#64748b"     # Slate gray

# ==============================================================================
# 1. Figure 5: Baseline Accuracy Comparison (N=2 vs N=5)
# ==============================================================================
def plot_baseline_accuracy():
    fig, ax = plt.subplots(figsize=(6.8, 4.4), dpi=300)
    
    baselines = ["Indep.", "Broadcast\n(ChatDev)", "Coord.\n(AutoGen)", "Hierarchy\n(MacNet)", "ORCHESTRA\n(Ours)"]
    acc_n2 = [13.3, 46.7, 30.0, 50.0, 40.0]
    acc_n5 = [10.7, 28.0, 28.0, 18.7, 26.7]
    
    x = np.arange(len(baselines))
    width = 0.36
    
    rects1 = ax.bar(x - width/2, acc_n2, width, label=r"Scale $N = 2$", color="#2563eb", edgecolor="black", linewidth=1.2, alpha=0.92)
    rects2 = ax.bar(x + width/2, acc_n5, width, label=r"Scale $N = 5$", color="#10b981", edgecolor="black", linewidth=1.2, alpha=0.92)
    
    # Add values on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=11.5, fontweight="bold")
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=11.5, fontweight="bold")
        
    ax.set_ylabel("Task Success Rate (%)", fontweight="bold", fontsize=14)
    ax.set_title("Multi-Agent Algorithmic Success Across Scales", pad=10, fontsize=14.5, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(baselines, fontweight="bold", fontsize=11.5)
    ax.set_ylim(0, 62)
    ax.grid(axis="y", linestyle="--", alpha=0.6, linewidth=1.0)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="upper right", fontsize=12)
    
    plt.tight_layout()
    p = out_dir / "figure_baseline_accuracy_comparison.png"
    plt.savefig(p, bbox_inches="tight")
    plt.close()
    print(f"Generated: {p}")

# ==============================================================================
# 2. Figure 6: Fault Tolerance & Perturbation Resilience (at N=5)
# ==============================================================================
def plot_perturbation_resilience():
    fig, ax = plt.subplots(figsize=(6.8, 4.4), dpi=300)
    
    baselines = ["Indep.", "Broadcast\n(ChatDev)", "Coord.\n(AutoGen)", "Hierarchy\n(MacNet)", "ORCHESTRA\n(Ours)"]
    ctrl_acc = [10.7, 28.0, 28.0, 18.7, 26.7]
    drop_acc = [6.7, 12.0, 10.7, 0.0, 6.7]
    
    x = np.arange(len(baselines))
    width = 0.36
    
    rects1 = ax.bar(x - width/2, ctrl_acc, width, label="Healthy (Nominal)", color="#2563eb", edgecolor="black", linewidth=1.2, alpha=0.92)
    rects2 = ax.bar(x + width/2, drop_acc, width, label="Node Crash (Dropout)", color="#dc2626", edgecolor="black", linewidth=1.2, alpha=0.92)
    
    # Add values on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=11.5, fontweight="bold")
    for rect in rects2:
        h = rect.get_height()
        color = "#dc2626" if h == 0.0 else "black"
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=11.5, fontweight="bold", color=color)
        
    # Prominent callout for MacNet 0.0% collapse
    ax.annotate("100% Collapse\n(0.0% Survival)", xy=(3 + width/2, 1.0), xytext=(3 + width/2, 13.5),
                arrowprops=dict(facecolor="#dc2626", shrink=0.08, width=2.2, headwidth=7),
                fontsize=11.5, fontweight="bold", color="#b91c1c", ha="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#fee2e2", edgecolor="#ef4444", lw=1.2))
    
    ax.set_ylabel("Task Success Rate (%)", fontweight="bold", fontsize=14)
    ax.set_title(r"Perturbation Resilience Under Node Crash ($N = 5$)", pad=10, fontsize=14.5, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(baselines, fontweight="bold", fontsize=11.5)
    ax.set_ylim(0, 37)
    ax.grid(axis="y", linestyle="--", alpha=0.6, linewidth=1.0)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="upper right", fontsize=12)
    
    plt.tight_layout()
    p = out_dir / "figure_perturbation_resilience.png"
    plt.savefig(p, bbox_inches="tight")
    plt.close()
    print(f"Generated: {p}")

# ==============================================================================
# 3. Figure 7: Token Consumption vs Accuracy (Pareto Frontier at N=5)
# ==============================================================================
def plot_pareto_frontier():
    fig, ax = plt.subplots(figsize=(6.8, 4.5), dpi=300)
    
    data = [
        {"name": "Independent", "tokens": 11113, "acc": 10.7, "color": C_INDEP, "shape": "o", "size": 170},
        {"name": "Hierarchy (MacNet)", "tokens": 13918, "acc": 18.7, "color": C_MACNET, "shape": "s", "size": 170},
        {"name": "ORCHESTRA (Ours)", "tokens": 17802, "acc": 26.7, "color": C_ORCHESTRA, "shape": "*", "size": 380},
        {"name": "Broadcast (ChatDev)", "tokens": 19927, "acc": 28.0, "color": C_BROADCAST, "shape": "^", "size": 190},
        {"name": "Coordinator (AutoGen)", "tokens": 26186, "acc": 28.0, "color": C_AUTOGEN, "shape": "D", "size": 170},
    ]
    
    # Pareto frontier line connecting (11113, 10.7) -> (13918, 18.7) -> (17802, 26.7) -> (19927, 28.0)
    p_tokens = [11113, 13918, 17802, 19927]
    p_acc = [10.7, 18.7, 26.7, 28.0]
    ax.plot(p_tokens, p_acc, linestyle="--", color="#059669", linewidth=2.8, alpha=0.75, zorder=2, label="Pareto Frontier")
    ax.fill_between(p_tokens, p_acc, 0, color="#d1fae5", alpha=0.35, zorder=1)
    
    for d in data:
        ax.scatter(d["tokens"], d["acc"], color=d["color"], marker=d["shape"], s=d["size"],
                   edgecolors="black", linewidths=1.6, zorder=5)
        
        # Position annotations cleanly with large readable text
        offset_x = 10
        offset_y = 5
        if "Broadcast" in d["name"]:
            offset_x = -135
            offset_y = 9
        elif "ORCHESTRA" in d["name"]:
            offset_x = -120
            offset_y = -22
        elif "Coordinator" in d["name"]:
            offset_x = -140
            offset_y = -22
        elif "Hierarchy" in d["name"]:
            offset_x = 10
            offset_y = -10
            
        fontweight = "bold"
        color = "#047857" if "ORCHESTRA" in d["name"] else "#1e293b"
        ax.annotate(f"{d['name']}\n({d['tokens']:,} tok, {d['acc']}%)",
                    xy=(d["tokens"], d["acc"]),
                    xytext=(offset_x, offset_y), textcoords="offset points",
                    fontsize=11.5, fontweight=fontweight, color=color,
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#94a3b8", alpha=0.92, lw=1.0))
        
    ax.set_xlabel("Mean Token Consumption per Task", fontweight="bold", fontsize=13.5)
    ax.set_ylabel("Task Success Rate (%)", fontweight="bold", fontsize=13.5)
    ax.set_title(r"Pareto Efficiency: Accuracy vs. Tokens ($N = 5$)", pad=10, fontsize=14.5, fontweight="bold")
    ax.set_xlim(8500, 28500)
    ax.set_ylim(5, 34)
    ax.grid(True, linestyle="--", alpha=0.55, linewidth=1.0)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="lower right", fontsize=12)
    
    plt.tight_layout()
    p = out_dir / "figure_token_accuracy_pareto.png"
    plt.savefig(p, bbox_inches="tight")
    plt.close()
    print(f"Generated: {p}")

# ==============================================================================
# 4. Figure 8 (NEW): Algorithmic Complexity Tier Breakdown (Table VIII)
# ==============================================================================
def plot_complexity_tiers():
    fig, ax = plt.subplots(figsize=(7.0, 4.4), dpi=300)
    
    tiers = ["Level I: Aggregation\n(Scalar Reductions)", "Level II: Spatial Mesh\n(Topological Routing)", "Level III: Global Shuffle\n(Distributed Kernels)"]
    
    # Accuracy for each method across the 3 tiers (from Table VIII)
    indep = [18.0, 18.0, 0.0]
    broadcast = [57.0, 45.0, 10.0]
    autogen = [40.0, 30.0, 17.0]
    macnet = [54.0, 29.0, 20.0]
    orchestra = [54.0, 24.0, 22.0] # Rank 1 on Level III
    
    x = np.arange(len(tiers))
    width = 0.16
    
    r1 = ax.bar(x - 2*width, indep, width, label="Independent", color=C_INDEP, edgecolor="black", linewidth=1.1)
    r2 = ax.bar(x - width, broadcast, width, label="Broadcast (ChatDev)", color=C_BROADCAST, edgecolor="black", linewidth=1.1)
    r3 = ax.bar(x, autogen, width, label="Coordinator (AutoGen)", color=C_AUTOGEN, edgecolor="black", linewidth=1.1)
    r4 = ax.bar(x + width, macnet, width, label="Hierarchy (MacNet)", color=C_MACNET, edgecolor="black", linewidth=1.1)
    r5 = ax.bar(x + 2*width, orchestra, width, label="ORCHESTRA (Ours)", color=C_ORCHESTRA, edgecolor="black", linewidth=1.3)
    
    # Highlight Rank #1 on Level III
    ax.annotate("Rank #1 (22.0%)\nBest on Shuffle", xy=(2 + 2*width, 22.0), xytext=(2 + width*0.5, 39),
                arrowprops=dict(facecolor=C_ORCHESTRA, shrink=0.08, width=2.2, headwidth=7),
                fontsize=11.5, fontweight="bold", color="#065f46", ha="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#d1fae5", edgecolor="#10b981", lw=1.2))
    
    # Value annotations on Level III bars
    for rect in [r1[2], r2[2], r3[2], r4[2], r5[2]]:
        h = rect.get_height()
        ax.annotate(f"{h:.0f}%", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 2.5), textcoords="offset points", ha="center", va="bottom",
                    fontsize=11, fontweight="bold")
        
    ax.set_ylabel("Task Success Rate (%)", fontweight="bold", fontsize=14)
    ax.set_title("Performance Across Algorithmic Complexity Tiers", pad=10, fontsize=14.5, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(tiers, fontweight="bold", fontsize=11.5)
    ax.set_ylim(0, 70)
    ax.grid(axis="y", linestyle="--", alpha=0.6, linewidth=1.0)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="upper right", ncol=2, fontsize=10.5)
    
    plt.tight_layout()
    p = out_dir / "figure_complexity_tiers.png"
    plt.savefig(p, bbox_inches="tight")
    plt.close()
    print(f"Generated: {p}")

# ==============================================================================
# 5. Figure 9 (NEW): The Emergence Curve (Table IX)
# ==============================================================================
def plot_emergence_curve():
    fig, ax = plt.subplots(figsize=(7.0, 4.4), dpi=300)
    
    conditions = ["Level I\nAggregation", "Level II\nSpatial Mesh", "Level III\nGlobal Shuffle", "Node Crash\nPerturbation"]
    x = np.arange(len(conditions))
    
    # Data from Table IX:
    gini = [0.266, 0.334, 0.401, 0.600]
    jaccard = [0.482, 0.365, 0.248, 0.584]
    reciprocity = [0.724, 0.612, 0.548, 0.380]
    betweenness = [0.142, 0.228, 0.315, 0.486]
    
    # Plot lines with distinct styles, thick strokes, and clear markers
    ax.plot(x, gini, marker="o", markersize=10, linewidth=3.2, color="#059669", label="Gini Specialization (G) [Leadership]", zorder=4)
    ax.plot(x, jaccard, marker="s", markersize=9, linewidth=2.6, linestyle="--", color="#ea580c", label="Jaccard Graph Drift (J) [Churn]", zorder=3)
    ax.plot(x, reciprocity, marker="D", markersize=8, linewidth=2.6, linestyle="-.", color="#8b5cf6", label="Reciprocity (R) [Mutual Debate]", zorder=3)
    ax.plot(x, betweenness, marker="^", markersize=9, linewidth=2.6, linestyle=":", color="#0284c7", label="Betweenness Centrality (C_B) [Hubs]", zorder=3)
    
    # Value labels for Gini Specialization
    for idx, (xi, yi) in enumerate(zip(x, gini)):
        ax.annotate(f"G = {yi:.3f}", xy=(xi, yi), xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=11.5, fontweight="bold", color="#065f46",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#d1fae5", edgecolor="#059669", alpha=0.92))
        
    # Annotate phases
    ax.axvspan(-0.4, 0.5, color="#f1f5f9", alpha=0.5, zorder=0)
    ax.text(0, 0.05, "Flat Democracy", ha="center", fontsize=11, fontweight="bold", color="#64748b")
    
    ax.axvspan(0.5, 2.4, color="#f0fdf4", alpha=0.5, zorder=0)
    ax.text(1.5, 0.05, "Adaptive Hub Election", ha="center", fontsize=11, fontweight="bold", color="#059669")
    
    ax.axvspan(2.4, 3.4, color="#fef2f2", alpha=0.5, zorder=0)
    ax.text(3, 0.05, "Consolidation", ha="center", fontsize=11, fontweight="bold", color="#dc2626")
    
    ax.set_ylabel("Network Metric Value [0, 1]", fontweight="bold", fontsize=13.5)
    ax.set_title("The Emergence Curve: Network Dynamics Across Stress", pad=10, fontsize=14.5, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontweight="bold", fontsize=11.5)
    ax.set_ylim(0, 0.85)
    ax.grid(True, linestyle="--", alpha=0.55, linewidth=1.0)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="upper left", ncol=1, fontsize=10.5)
    
    plt.tight_layout()
    p = out_dir / "figure_emergence_curve.png"
    plt.savefig(p, bbox_inches="tight")
    plt.close()
    print(f"Generated: {p}")

if __name__ == "__main__":
    plot_baseline_accuracy()
    plot_perturbation_resilience()
    plot_pareto_frontier()
    plot_complexity_tiers()
    plot_emergence_curve()
    print("All 5 enhanced figures successfully generated!")
