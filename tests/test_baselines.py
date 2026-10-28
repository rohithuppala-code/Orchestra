"""Unit tests for the 6 Multi-Agent Baselines and Topology Enforcers."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from baselines.topologies import (
    SUPPORTED_BASELINES,
    BroadcastTopology,
    CentralCoordinatorTopology,
    FixedRolesTopology,
    HierarchicalCoordinatorTopology,
    IndependentTopology,
    OrchestraTopology,
    RandomTopology,
    create_baseline_topology,
)
from baselines.compare import generate_paper_comparison_table
import pandas as pd


def test_supported_baselines_registry():
    """Verify all 6 baselines + orchestra are registered and constructible."""
    expected = [
        "independent",
        "broadcast",
        "random_topology",
        "central_coordinator",
        "hierarchical_coordinator",
        "fixed_roles",
        "orchestra",
    ]
    for b in expected:
        assert b in SUPPORTED_BASELINES
        topo = create_baseline_topology(b)
        assert topo.name == b
        assert len(topo.citation) > 0


def test_independent_topology_filters_all_messages():
    """Verify IndependentTopology drops all cross-agent messages."""
    topo = IndependentTopology()
    with tempfile.TemporaryDirectory() as tmpdir:
        case_dir = Path(tmpdir)
        msg_dir = case_dir / "rounds" / "round-000001" / "env" / "messages"
        msg_dir.mkdir(parents=True)

        # Write 2 test messages
        (msg_dir / "m1.json").write_text(json.dumps({"sender_id": 0, "recipient_id": 1, "content": "hi"}))
        (msg_dir / "m2.json").write_text(json.dumps({"sender_id": 1, "recipient_id": 0, "content": "hello"}))

        res = topo.apply_post_round(case_dir, current_round=1, num_agents=2)
        assert res["dropped_messages"] == 2
        assert len(list(msg_dir.glob("*.json"))) == 0


def test_central_coordinator_blocks_worker_to_worker():
    """Verify CentralCoordinator allows Hub traffic (Agent 0) and drops Worker-Worker."""
    topo = CentralCoordinatorTopology(hub_id=0)
    with tempfile.TemporaryDirectory() as tmpdir:
        case_dir = Path(tmpdir)
        msg_dir = case_dir / "rounds" / "round-000001" / "env" / "messages"
        msg_dir.mkdir(parents=True)

        # Message 1: 0 -> 1 (Hub to Worker: ALLOWED)
        (msg_dir / "m1.json").write_text(json.dumps({"sender_id": 0, "recipient_id": 1}))
        # Message 2: 1 -> 0 (Worker to Hub: ALLOWED)
        (msg_dir / "m2.json").write_text(json.dumps({"sender_id": 1, "recipient_id": 0}))
        # Message 3: 1 -> 2 (Worker to Worker: FORBIDDEN)
        (msg_dir / "m3.json").write_text(json.dumps({"sender_id": 1, "recipient_id": 2}))

        res = topo.apply_post_round(case_dir, current_round=1, num_agents=3)
        assert res["dropped_messages"] == 1
        assert res["kept_messages"] == 2
        remaining = [f.name for f in msg_dir.glob("*.json")]
        assert "m3.json" not in remaining
        assert "m1.json" in remaining
        assert "m2.json" in remaining


def test_hierarchical_coordinator_tree_edges():
    """Verify HierarchicalCoordinator enforces tree chain-of-command for N=5."""
    topo = HierarchicalCoordinatorTopology()
    with tempfile.TemporaryDirectory() as tmpdir:
        case_dir = Path(tmpdir)
        msg_dir = case_dir / "rounds" / "round-000001" / "env" / "messages"
        msg_dir.mkdir(parents=True)

        # In N=5 tree: 0<->1, 0<->2, 1<->3, 2<->4
        # Allowed: 1 -> 3
        (msg_dir / "m1.json").write_text(json.dumps({"sender_id": 1, "recipient_id": 3}))
        # Forbidden: 3 -> 4 (Cross-division worker)
        (msg_dir / "m2.json").write_text(json.dumps({"sender_id": 3, "recipient_id": 4}))
        # Forbidden: 0 -> 3 (Skip-level)
        (msg_dir / "m3.json").write_text(json.dumps({"sender_id": 0, "recipient_id": 3}))

        res = topo.apply_post_round(case_dir, current_round=1, num_agents=5)
        assert res["dropped_messages"] == 2
        assert res["kept_messages"] == 1
        assert (msg_dir / "m1.json").exists()
        assert not (msg_dir / "m2.json").exists()
        assert not (msg_dir / "m3.json").exists()


def test_paper_comparison_table_generation():
    """Verify comparison table generation from dataframe."""
    df = pd.DataFrame([
        {"baseline": "orchestra", "num_agents": 2, "perturbation": "none", "success_rate": 1.0, "token_consumption": 1800, "total_rounds": 2, "gini_out_degree": 0.167},
        {"baseline": "orchestra", "num_agents": 2, "perturbation": "agent_dropout", "success_rate": 0.8, "token_consumption": 1200, "total_rounds": 2, "gini_out_degree": 0.200},
        {"baseline": "broadcast", "num_agents": 2, "perturbation": "none", "success_rate": 0.7, "token_consumption": 3200, "total_rounds": 4, "gini_out_degree": 0.0},
        {"baseline": "central_coordinator", "num_agents": 2, "perturbation": "none", "success_rate": 0.75, "token_consumption": 2100, "total_rounds": 3, "gini_out_degree": 0.5},
    ])
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        table = generate_paper_comparison_table(df, out_dir)
        assert not table.empty
        assert (out_dir / "table1_master_baseline_comparison.csv").exists()
        assert (out_dir / "table1_master_baseline_comparison.md").exists()
