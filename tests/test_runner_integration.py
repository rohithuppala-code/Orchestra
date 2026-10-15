"""Tests for ORCHESTRA experiment runner orchestration and integration."""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from orchestra.config import ExperimentConfig
from orchestra.runner import run_orchestra_experiment


def test_runner_mock_execution(tmp_path, monkeypatch):
    """Test full runner orchestration using mocked SILO-BENCH engine."""
    case_dir = tmp_path / "mock_runner_case"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Setup mock case metadata
    metadata = {
        "case_id": "test_mock_case_001",
        "task": {"case_id": "I-01"},
        "config": {"protocol": "msg", "agent_count": 2},
        "execution": {"current_round": 2, "status": "running"},
    }
    with open(case_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f)
        
    # Setup mock rounds
    r1_dir = case_dir / "rounds" / "round-000001" / "env" / "messages"
    r1_dir.mkdir(parents=True, exist_ok=True)
    with open(r1_dir / "m1.json", "w") as f:
        json.dump({"sender_id": 0, "recipient_id": 1}, f)
        
    r2_dir = case_dir / "rounds" / "round-000002" / "env" / "messages"
    r2_dir.mkdir(parents=True, exist_ok=True)
    with open(r2_dir / "m2.json", "w") as f:
        json.dump({"sender_id": 1, "recipient_id": 0}, f)
        
    # Mock engine functions
    monkeypatch.setattr("orchestra.runner.init_case", lambda **kw: str(case_dir))
    
    round_counter = [0]
    def mock_run_round(cd):
        round_counter[0] += 1
        return round_counter[0] >= 2  # Terminate at round 2
    monkeypatch.setattr("orchestra.runner.run_round", mock_run_round)
    
    def mock_evaluate(cd):
        res = {
            "success": True,
            "metrics": {
                "S_success_rate": 1.0,
                "P_partial_correctness": 1.0,
                "C_token_consumption": 1200.0,
                "D_communication_density": 0.5,
            },
        }
        with open(case_dir / "results.json", "w", encoding="utf-8") as f:
            json.dump(res, f)
    monkeypatch.setattr("orchestra.runner.evaluate", mock_evaluate)
    
    cfg = ExperimentConfig(
        task_id="I-01",
        agent_count=2,
        protocol="msg",
        max_rounds=5,
        hitl_enabled=True,
    )
    
    summary = run_orchestra_experiment(cfg)
    assert summary.status == "completed"
    assert summary.total_rounds == 2
    assert summary.success is True
    assert (case_dir / "orchestra_summary.json").exists()
    assert (case_dir / "orchestra_profile.json").exists()


def test_runner_error_handling(tmp_path, monkeypatch):
    """Test runner records failure cleanly when engine raises exception."""
    case_dir = tmp_path / "mock_error_case"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        "case_id": "test_error_case",
        "task": {"case_id": "I-01"},
        "config": {"protocol": "msg", "agent_count": 2},
        "execution": {"current_round": 1, "status": "running"},
    }
    with open(case_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f)
        
    monkeypatch.setattr("orchestra.runner.init_case", lambda **kw: str(case_dir))
    
    def mock_failing_round(cd):
        raise RuntimeError("Simulated inference engine timeout")
    monkeypatch.setattr("orchestra.runner.run_round", mock_failing_round)
    
    cfg = ExperimentConfig(
        task_id="I-01",
        agent_count=2,
        protocol="msg",
        max_rounds=5,
    )
    
    summary = run_orchestra_experiment(cfg)
    assert summary.status == "failed"
    assert "Simulated inference engine timeout" in summary.error_message
    assert (case_dir / "orchestra_summary.json").exists()


def test_batch_matrix_runner(tmp_path, monkeypatch):
    """Test automated batch matrix runner across conditions."""
    from orchestra.batch_runner import MatrixConfig, run_batch_matrix

    case_dirs = []
    call_idx = [0]

    def mock_init(**kw):
        call_idx[0] += 1
        cd = tmp_path / f"batch_case_{call_idx[0]}"
        cd.mkdir(parents=True, exist_ok=True)
        # Create metadata
        meta = {
            "case_id": f"batch_case_{call_idx[0]}",
            "task": {"case_id": "I-01"},
            "config": {"protocol": kw.get("protocol", "msg"), "agent_count": 2},
            "execution": {"current_round": 1, "status": "completed"},
        }
        with open(cd / "metadata.json", "w") as f:
            json.dump(meta, f)
        case_dirs.append(cd)
        return str(cd)

    monkeypatch.setattr("orchestra.runner.init_case", mock_init)
    monkeypatch.setattr("orchestra.runner.run_round", lambda cd: True)
    monkeypatch.setattr("orchestra.runner.evaluate", lambda cd: None)

    matrix = MatrixConfig(
        task_ids=["I-01"],
        agent_counts=[2],
        protocols=["msg", "broadcast"],
        repetitions=1,
        workspace=str(tmp_path / "ws"),
    )

    summaries = run_batch_matrix(matrix)
    assert len(summaries) == 2
    assert all(s.status == "completed" for s in summaries)
    assert (tmp_path / "ws" / "batch_comparison_results.csv").exists()
