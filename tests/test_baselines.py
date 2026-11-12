"""Unit tests for the 6 Multi-Agent Baselines and Topology Enforcers."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd

from baselines.compare import generate_paper_comparison_table, load_and_standardize_results
from baselines.topologies import (
    EXTERNAL_BASELINES,
    SUPPORTED_BASELINES,
    CentralCoordinatorTopology,
    HierarchicalCoordinatorTopology,
    IndependentTopology,
    create_baseline_topology,
)
from orchestra.config import SELECTED_15_TASKS, expand_task_ids


def test_supported_baselines_registry():
    """Verify all 6 baselines + orchestra are registered and constructible."""
    expected = [
        "independent",
        "broadcast",
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


def test_baseline_initialization_conditioning():
    """Verify literature baselines inject domain-appropriate guidance in round-000000."""
    # 1. Independent
    with tempfile.TemporaryDirectory() as tmpdir:
        case_dir = Path(tmpdir)
        round0 = case_dir / "rounds" / "round-000000"
        for i in range(2):
            agent_dir = round0 / f"agent-{i:03d}"
            agent_dir.mkdir(parents=True)
            ctx = {"messages": [{"role": "system", "content": "Base prompt."}]}
            (agent_dir / "context.json").write_text(json.dumps(ctx))

        topo_ind = create_baseline_topology("independent")
        res_ind = topo_ind.apply_initialization(case_dir, 2)
        assert res_ind.get("applied") is True
        c0 = json.loads((round0 / "agent-000" / "context.json").read_text())
        assert "INDEPENDENT" in c0["messages"][0]["content"]

    # 2. Central Coordinator
    with tempfile.TemporaryDirectory() as tmpdir:
        case_dir = Path(tmpdir)
        round0 = case_dir / "rounds" / "round-000000"
        for i in range(5):
            agent_dir = round0 / f"agent-{i:03d}"
            agent_dir.mkdir(parents=True)
            ctx = {"messages": [{"role": "system", "content": "Base prompt."}]}
            (agent_dir / "context.json").write_text(json.dumps(ctx))

        topo_hub = create_baseline_topology("central_coordinator", hub_id=0)
        res_hub = topo_hub.apply_initialization(case_dir, 5)
        assert res_hub.get("applied") is True
        c0 = json.loads((round0 / "agent-000" / "context.json").read_text())
        c1 = json.loads((round0 / "agent-001" / "context.json").read_text())
        assert "Central Hub Coordinator" in c0["messages"][0]["content"]
        assert "Central Coordinator" in c1["messages"][0]["content"]

    # 3. Hierarchical Coordinator
    with tempfile.TemporaryDirectory() as tmpdir:
        case_dir = Path(tmpdir)
        round0 = case_dir / "rounds" / "round-000000"
        for i in range(5):
            agent_dir = round0 / f"agent-{i:03d}"
            agent_dir.mkdir(parents=True)
            ctx = {"messages": [{"role": "system", "content": "Base prompt."}]}
            (agent_dir / "context.json").write_text(json.dumps(ctx))

        topo_tree = create_baseline_topology("hierarchical_coordinator")
        res_tree = topo_tree.apply_initialization(case_dir, 5)
        assert res_tree.get("applied") is True
        c3 = json.loads((round0 / "agent-003" / "context.json").read_text())
        assert "HIERARCHICAL TREE" in c3["messages"][0]["content"].upper()


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


def test_standardize_results_with_mixed_csvs():
    """Verify load_and_standardize_results correctly identifies ORCHESTRA rows from protocol."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # CSV 1: Baseline CSV (has 'baseline' column)
        df_base = pd.DataFrame([
            {"baseline": "central_coordinator", "task_id": "I-01", "num_agents": 2, "success_rate": 0.8, "token_consumption": 2000, "total_rounds": 3, "perturbation": "none"}
        ])
        csv1 = tmp_path / "baseline_results.csv"
        df_base.to_csv(csv1, index=False)

        # CSV 2: ORCHESTRA batch CSV (has 'protocol'='msg', no 'baseline')
        df_orch = pd.DataFrame([
            {"task_id": "I-01", "protocol": "msg", "num_agents": 2, "success_rate": 1.0, "token_consumption": 1500, "total_rounds": 2, "case_id": "I-01_n2_msg_rep1_agent_dropout"}
        ])
        csv2 = tmp_path / "orch_results.csv"
        df_orch.to_csv(csv2, index=False)

        merged = load_and_standardize_results([csv1, csv2])
        baselines = merged["baseline"].tolist()
        perts = merged["perturbation"].tolist()

        assert "central_coordinator" in baselines
        assert "orchestra" in baselines
        assert "nan" not in baselines
        assert perts[1] == "agent_dropout"


def test_streamlined_450_matrix_configuration():
    """Verify urop_exec 450-run matrix uses 3 active external baselines and 15 stratified tasks."""
    assert EXTERNAL_BASELINES == [
        "independent",
        "central_coordinator",
        "hierarchical_coordinator",
    ]
    assert len(SELECTED_15_TASKS) == 15
    assert sum(1 for t in SELECTED_15_TASKS if t.startswith("I-")) == 5
    assert sum(1 for t in SELECTED_15_TASKS if t.startswith("II-")) == 5
    assert sum(1 for t in SELECTED_15_TASKS if t.startswith("III-")) == 5
    assert expand_task_ids(["selected"]) == SELECTED_15_TASKS

