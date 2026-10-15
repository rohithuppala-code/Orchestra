"""Tests for ORCHESTRA controlled perturbations and resilience interventions."""

import json
import pytest
from pathlib import Path

from orchestra.perturbations import (
    AgentDropoutPerturbation,
    CommunicationPartitionPerturbation,
    MessageCorruptionPerturbation,
    create_perturbation,
)


def test_agent_dropout_perturbation(tmp_path):
    """Test fail-stop agent dropout marking previous round state as submitted."""
    case_dir = tmp_path / "dropout_case"
    prev_round = case_dir / "rounds" / "round-000001" / "agent-001"
    prev_round.mkdir(parents=True, exist_ok=True)
    
    state_file = prev_round / "state.json"
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump({"agent_id": 1, "submitted": False, "round": 1}, f)
        
    pert = AgentDropoutPerturbation(trigger_round=2, target_agent_id=1)
    
    # Pre-round at round 1 (before trigger): not applied
    res1 = pert.apply_pre_round(case_dir, current_round=1, num_agents=3)
    assert res1["applied"] is False
    with open(state_file, "r") as f:
        assert json.load(f)["submitted"] is False
        
    # Pre-round at round 2 (trigger round): applied!
    res2 = pert.apply_pre_round(case_dir, current_round=2, num_agents=3)
    assert res2["applied"] is True
    assert res2["agent_id"] == 1
    with open(state_file, "r") as f:
        assert json.load(f)["submitted"] is True


def test_communication_partition_perturbation(tmp_path):
    """Test network partition dropping cross-group messages."""
    case_dir = tmp_path / "partition_case"
    round_dir = case_dir / "rounds" / "round-000002" / "env" / "messages"
    round_dir.mkdir(parents=True, exist_ok=True)
    
    # Partition: Group A {0, 1}, Group B {2, 3}
    pert = CommunicationPartitionPerturbation(
        trigger_round=2,
        partition_groups=[{0, 1}, {2, 3}],
    )
    
    # Message 1: 0 -> 1 (within group A) -> should be preserved
    m1_file = round_dir / "m1.json"
    with open(m1_file, "w") as f:
        json.dump({"sender_id": 0, "recipient_id": 1}, f)
        
    # Message 2: 0 -> 2 (cross group A -> B) -> should be dropped
    m2_file = round_dir / "m2.json"
    with open(m2_file, "w") as f:
        json.dump({"sender_id": 0, "recipient_id": 2}, f)
        
    res = pert.apply_post_round(case_dir, current_round=2, num_agents=4)
    assert res["applied"] is True
    assert res["dropped_messages"] == 1
    assert m1_file.exists()
    assert not m2_file.exists()


def test_message_corruption_perturbation(tmp_path):
    """Test Byzantine noise / message value corruption."""
    case_dir = tmp_path / "corrupt_case"
    round_dir = case_dir / "rounds" / "round-000002" / "env" / "messages"
    round_dir.mkdir(parents=True, exist_ok=True)
    
    pert = MessageCorruptionPerturbation(
        trigger_round=2,
        target_agent_id=1,
        corrupted_value=-999999,
    )
    
    m_file = round_dir / "m1.json"
    with open(m_file, "w") as f:
        json.dump({"sender_id": 1, "recipient_id": 0, "content": "988"}, f)
        
    res = pert.apply_post_round(case_dir, current_round=2, num_agents=2)
    assert res["applied"] is True
    assert res["corrupted_messages"] == 1
    with open(m_file, "r") as f:
        assert json.load(f)["content"] == "-999999"


def test_create_perturbation_factory():
    """Test perturbation factory initialization."""
    p_none = create_perturbation(None)
    assert p_none is None
    
    p_drop = create_perturbation("agent_dropout", {"round": 3, "agent_id": 2})
    assert isinstance(p_drop, AgentDropoutPerturbation)
    assert p_drop.trigger_round == 3
    assert p_drop.target_agent_id == 2
    
    p_part = create_perturbation("communication_partition", {"round": 2, "partition_groups": [{0}, {1, 2}]})
    assert isinstance(p_part, CommunicationPartitionPerturbation)
    
    with pytest.raises(ValueError):
        create_perturbation("unknown_type")
