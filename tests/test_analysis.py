"""Tests for ORCHESTRA comparative organizational analysis and visualization."""

import json
import pandas as pd
import pytest
from pathlib import Path

from orchestra.analysis import (
    build_comparison_dataframe,
    compute_structural_performance_correlations,
    compute_summary_statistics,
    generate_markdown_summary_table,
    load_case_profile,
    plot_communication_topology,
    plot_longitudinal_evolution,
)


def create_dummy_profile(case_dir: Path, case_id: str, success: bool = True, drift: float = 0.3) -> None:
    """Helper to write synthetic orchestra_profile.json."""
    case_dir.mkdir(parents=True, exist_ok=True)
    profile_data = {
        "case_id": case_id,
        "task_id": "I-01",
        "protocol": "msg",
        "num_agents": 2,
        "total_rounds": 3,
        "snapshots": [
            {"round_num": 1, "cumulative_density": 0.5, "jaccard_distance_from_prev": 0.0, "edges": [{"from": 0, "to": 1, "weight": 1}]},
            {"round_num": 2, "cumulative_density": 1.0, "jaccard_distance_from_prev": drift, "edges": [{"from": 1, "to": 0, "weight": 1}]},
        ],
        "gini_out_degree": 0.1,
        "gini_in_degree": 0.1,
        "gini_tool_usage": {},
        "agent_roles": {"0": "Peer_Collaborator", "1": "Peer_Collaborator"},
        "mean_structural_drift": drift,
        "final_network_entropy": 1.0,
        "network_diameter": 1,
        "is_connected": True,
        "success": success,
        "success_rate": 1.0 if success else 0.0,
        "partial_correctness": 1.0 if success else 0.5,
        "token_consumption": 2000.0,
        "communication_density": 1.0,
    }
    with open(case_dir / "orchestra_profile.json", "w", encoding="utf-8") as f:
        json.dump(profile_data, f)


def test_build_comparison_dataframe(tmp_path):
    """Test building comparative DataFrame from case directories."""
    dir1 = tmp_path / "case1"
    dir2 = tmp_path / "case2"
    create_dummy_profile(dir1, "case1", success=True, drift=0.2)
    create_dummy_profile(dir2, "case2", success=False, drift=0.5)
    
    df = build_comparison_dataframe([dir1, dir2])
    assert len(df) == 2
    assert "case_id" in df.columns
    assert "gini_out_degree" in df.columns
    assert "success_rate" in df.columns


def test_markdown_summary_table(tmp_path):
    """Test generating Markdown table from DataFrame."""
    dir1 = tmp_path / "case1"
    create_dummy_profile(dir1, "case1")
    df = build_comparison_dataframe([dir1])
    md = generate_markdown_summary_table(df)
    assert "task_id" in md and "protocol" in md and "num_agents" in md
    assert "I-01" in md


def test_plots_generation(tmp_path):
    """Test generating publication figures."""
    dir1 = tmp_path / "case1"
    dir2 = tmp_path / "case2"
    create_dummy_profile(dir1, "case1")
    create_dummy_profile(dir2, "case2")
    
    long_plot = tmp_path / "longitudinal.png"
    topo_plot = tmp_path / "topology.png"
    
    plot_longitudinal_evolution([dir1, dir2], long_plot)
    assert long_plot.exists()
    assert long_plot.stat().st_size > 1000
    
    plot_communication_topology(dir1, topo_plot)
    assert topo_plot.exists()
    assert topo_plot.stat().st_size > 1000
