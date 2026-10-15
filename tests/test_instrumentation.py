"""Tests for ORCHESTRA research instrumentation, network metrics, and role classification."""

import json
import numpy as np
import pytest
from pathlib import Path

from orchestra.instrumentation import (
    OrganizationalProfile,
    RoundNetworkSnapshot,
    calculate_entropy,
    calculate_gini,
    extract_case_instrumentation,
    extract_round_snapshot,
    save_orchestra_instrumentation,
)


def test_calculate_gini():
    """Verify Gini coefficient mathematical properties."""
    # Complete equality
    assert calculate_gini([5.0, 5.0, 5.0, 5.0]) == 0.0
    assert calculate_gini([0.0, 0.0, 0.0]) == 0.0
    assert calculate_gini([]) == 0.0
    
    # Skewed inequality
    gini_skewed = calculate_gini([0.0, 0.0, 0.0, 10.0])
    assert 0.70 <= gini_skewed <= 0.80
    
    # Moderate inequality
    gini_mod = calculate_gini([1.0, 2.0, 3.0, 4.0])
    assert 0.20 <= gini_mod <= 0.35


def test_calculate_entropy():
    """Verify Shannon entropy calculation."""
    # Zero / empty
    assert calculate_entropy([]) == 0.0
    assert calculate_entropy([0.0, 0.0]) == 0.0
    
    # Single state (deterministic)
    assert calculate_entropy([10.0, 0.0]) == 0.0
    
    # Uniform 2 states = 1.0 bit
    ent_uniform = calculate_entropy([5.0, 5.0])
    assert abs(ent_uniform - 1.0) < 1e-4


def test_synthetic_round_snapshot(tmp_path):
    """Test extracting a RoundNetworkSnapshot from mock case files."""
    case_dir = tmp_path / "mock_case"
    round1_dir = case_dir / "rounds" / "round-000001"
    msg_dir = round1_dir / "env" / "messages"
    msg_dir.mkdir(parents=True, exist_ok=True)
    
    # Agent 0 sends message to Agent 1 and Agent 2
    msg1 = {"sender_id": 0, "recipient_id": 1, "content": "value: 42"}
    msg2 = {"sender_id": 0, "recipient_id": 2, "content": "value: 42"}
    with open(msg_dir / "msg1.json", "w", encoding="utf-8") as f:
        json.dump(msg1, f)
    with open(msg_dir / "msg2.json", "w", encoding="utf-8") as f:
        json.dump(msg2, f)
        
    num_agents = 3
    snapshot = extract_round_snapshot(
        case_dir=case_dir,
        round_num=1,
        num_agents=num_agents,
        protocol="msg",
    )
    
    assert snapshot.round_num == 1
    assert snapshot.num_agents == 3
    assert snapshot.total_messages_this_round == 2
    assert snapshot.out_degrees[0] == 2
    assert snapshot.in_degrees[1] == 1
    assert snapshot.in_degrees[2] == 1
    assert snapshot.density > 0.0
    assert 0 in snapshot.active_agents


def test_full_case_instrumentation(tmp_path):
    """Test full case extraction and profile generation on synthetic case."""
    case_dir = tmp_path / "case_full"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. metadata.json
    metadata = {
        "case_id": "test_case_001",
        "task": {"case_id": "I-01"},
        "config": {"protocol": "msg", "agent_count": 3},
        "execution": {"current_round": 2, "status": "completed"},
    }
    with open(case_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f)
        
    # 2. results.json
    results = {
        "success": True,
        "metrics": {
            "S_success_rate": 1.0,
            "P_partial_correctness": 1.0,
            "C_token_consumption": 2500.0,
            "D_communication_density": 0.67,
        },
    }
    with open(case_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f)
        
    # 3. Round 1 messages: Agent 0 -> Agent 1, Agent 2
    r1_msg_dir = case_dir / "rounds" / "round-000001" / "env" / "messages"
    r1_msg_dir.mkdir(parents=True, exist_ok=True)
    with open(r1_msg_dir / "m1.json", "w") as f:
        json.dump({"sender_id": 0, "recipient_id": 1}, f)
    with open(r1_msg_dir / "m2.json", "w") as f:
        json.dump({"sender_id": 0, "recipient_id": 2}, f)
        
    # 4. Round 2 messages: Agent 1 -> Agent 0, Agent 2 -> Agent 0
    r2_msg_dir = case_dir / "rounds" / "round-000002" / "env" / "messages"
    r2_msg_dir.mkdir(parents=True, exist_ok=True)
    with open(r2_msg_dir / "m3.json", "w") as f:
        json.dump({"sender_id": 1, "recipient_id": 0}, f)
    with open(r2_msg_dir / "m4.json", "w") as f:
        json.dump({"sender_id": 2, "recipient_id": 0}, f)
        
    profile = extract_case_instrumentation(case_dir)
    assert profile.case_id == "test_case_001"
    assert profile.num_agents == 3
    assert profile.total_rounds == 2
    assert profile.success is True
    assert profile.success_rate == 1.0
    assert len(profile.snapshots) == 2
    assert profile.mean_structural_drift > 0.0
    assert 0 in profile.agent_roles
    
    # Save and reload
    out_profile_file = case_dir / "orchestra_profile.json"
    save_orchestra_instrumentation(profile, out_profile_file)
    assert out_profile_file.exists()
    with open(out_profile_file, "r", encoding="utf-8") as f:
        reloaded = json.load(f)
    assert reloaded["case_id"] == "test_case_001"
