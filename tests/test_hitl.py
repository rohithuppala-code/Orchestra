"""Tests for ORCHESTRA Human-in-the-Loop (HITL) oversight module."""

import json
import pytest
from pathlib import Path

from orchestra.hitl import BoundaryViolation, HITLMode, HITLSupervisor
from orchestra.instrumentation import RoundNetworkSnapshot


def create_dummy_snapshot(
    round_num: int = 1,
    num_agents: int = 3,
    out_degrees: dict = None,
    in_degrees: dict = None,
    total_msgs: int = 0,
) -> RoundNetworkSnapshot:
    """Helper to generate mock RoundNetworkSnapshot."""
    out_d = out_degrees or {i: 0 for i in range(num_agents)}
    in_d = in_degrees or {i: 0 for i in range(num_agents)}
    return RoundNetworkSnapshot(
        round_num=round_num,
        num_agents=num_agents,
        active_agents=[i for i in range(num_agents) if out_d.get(i, 0) > 0 or in_d.get(i, 0) > 0],
        edges=[],
        total_messages_this_round=total_msgs,
        density=0.5,
        reciprocity=0.0,
        in_degrees=in_d,
        out_degrees=out_d,
        betweenness_centrality={i: 0.0 for i in range(num_agents)},
        closeness_centrality={i: 0.0 for i in range(num_agents)},
        clustering_coefficient=0.0,
        cumulative_density=0.5,
        cumulative_edges_count=2,
        cumulative_reciprocity=0.0,
        cumulative_betweenness={i: 0.0 for i in range(num_agents)},
        jaccard_distance_from_prev=0.2,
        adjacency_frobenius_diff=1.0,
        tool_counts={i: {} for i in range(num_agents)},
    )


def test_hitl_monopolization_detection(tmp_path):
    """Test detection of message monopolization by a single agent."""
    supervisor = HITLSupervisor(
        mode=HITLMode.AUDIT_ONLY,
        monopolization_threshold=0.80,
    )
    
    # 3 agents: Agent 0 sends 9 messages out of 10 (90% >= 80% threshold)
    snap = create_dummy_snapshot(
        round_num=1,
        num_agents=3,
        out_degrees={0: 9, 1: 1, 2: 0},
        in_degrees={0: 0, 1: 5, 2: 5},
        total_msgs=10,
    )
    
    violations = supervisor.inspect_round(tmp_path, snap)
    assert len(violations) >= 1
    v = [x for x in violations if x.violation_type == "monopolization"][0]
    assert v.agent_id == 0
    assert v.metric_value == 0.90
    assert (tmp_path / "hitl_interventions.jsonl").exists()


def test_hitl_isolation_detection(tmp_path):
    """Test detection of agent isolation across consecutive rounds."""
    supervisor = HITLSupervisor(
        mode=HITLMode.AUDIT_ONLY,
        max_isolated_rounds=2,
    )
    
    # Round 1: Agent 2 has 0 in, 0 out
    snap1 = create_dummy_snapshot(
        round_num=1,
        num_agents=3,
        out_degrees={0: 2, 1: 2, 2: 0},
        in_degrees={0: 2, 1: 2, 2: 0},
        total_msgs=4,
    )
    v1 = supervisor.inspect_round(tmp_path, snap1)
    assert not any(x.violation_type == "isolation" for x in v1)  # Only 1 round
    
    # Round 2: Agent 2 remains isolated (2nd consecutive round -> triggers)
    snap2 = create_dummy_snapshot(
        round_num=2,
        num_agents=3,
        out_degrees={0: 2, 1: 2, 2: 0},
        in_degrees={0: 2, 1: 2, 2: 0},
        total_msgs=4,
    )
    v2 = supervisor.inspect_round(tmp_path, snap2)
    iso = [x for x in v2 if x.violation_type == "isolation"]
    assert len(iso) == 1
    assert iso[0].agent_id == 2
    assert iso[0].metric_value == 2.0


def test_hitl_stagnation_detection(tmp_path):
    """Test detection of coordination deadlock/stagnation."""
    supervisor = HITLSupervisor(
        mode=HITLMode.AUDIT_ONLY,
        stagnation_threshold_rounds=2,
    )
    
    # Round 1: 0 messages
    snap1 = create_dummy_snapshot(round_num=1, num_agents=2, total_msgs=0)
    supervisor.inspect_round(tmp_path, snap1)
    
    # Round 2: 0 messages -> triggers stagnation
    snap2 = create_dummy_snapshot(round_num=2, num_agents=2, total_msgs=0)
    v2 = supervisor.inspect_round(tmp_path, snap2)
    stag = [x for x in v2 if x.violation_type == "stagnation"]
    assert len(stag) == 1
    
    summary = supervisor.get_summary()
    assert summary["total_violations"] >= 1
    assert "stagnation" in summary["violations_by_type"]
