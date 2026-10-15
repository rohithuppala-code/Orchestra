"""Tests for ORCHESTRA configuration, population scaling, and provider resolution."""

import os
import pytest
from pathlib import Path

from orchestra.config import (
    SUPPORTED_AGENT_SCALES,
    SUPPORTED_PROTOCOLS,
    ExperimentConfig,
)


def test_supported_agent_scales():
    """Verify standard benchmark agent scales are defined."""
    assert 2 in SUPPORTED_AGENT_SCALES
    assert 5 in SUPPORTED_AGENT_SCALES
    assert 10 in SUPPORTED_AGENT_SCALES
    assert 20 in SUPPORTED_AGENT_SCALES
    assert 50 in SUPPORTED_AGENT_SCALES
    assert 100 in SUPPORTED_AGENT_SCALES


def test_experiment_config_validation():
    """Test validation of experiment configurations."""
    # Valid config
    cfg = ExperimentConfig(task_id="I-01", agent_count=2, protocol="msg", max_rounds=10)
    cfg.validate()
    
    # Invalid protocol
    with pytest.raises(ValueError, match="Unsupported protocol"):
        bad_cfg = ExperimentConfig(task_id="I-01", agent_count=2, protocol="invalid_proto")
        bad_cfg.validate()
        
    # Invalid agent count
    with pytest.raises(ValueError, match="positive"):
        bad_cfg2 = ExperimentConfig(task_id="I-01", agent_count=-1, protocol="msg")
        bad_cfg2.validate()
        
    # Invalid HITL mode
    with pytest.raises(ValueError, match="Invalid HITL mode"):
        bad_cfg3 = ExperimentConfig(task_id="I-01", agent_count=2, hitl_mode="unsupported")
        bad_cfg3.validate()


def test_task_file_resolution_by_id():
    """Test resolving benchmark task file by task ID and agent count."""
    for n in [2, 5, 10]:
        cfg = ExperimentConfig(task_id="I-01", agent_count=n)
        task_file = cfg.resolve_task_file()
        assert task_file.exists(), f"Benchmark task file for n={n} should exist"
        assert f"I-01_n{n}.json" in task_file.name


def test_task_file_resolution_nonexistent():
    """Test error handling when task does not exist."""
    cfg = ExperimentConfig(task_id="NONEXISTENT_99", agent_count=2)
    with pytest.raises(FileNotFoundError):
        cfg.resolve_task_file()


def test_model_provider_resolution(monkeypatch):
    """Test model configuration resolution precedence."""
    # 1. Explicit values
    cfg = ExperimentConfig(
        task_id="I-01",
        agent_count=2,
        model="custom-llm",
        api_base="https://custom-api.org/v1",
        api_key="secret-key",
    )
    mcfg = cfg.resolve_model_config()
    assert mcfg["model"] == "custom-llm"
    assert mcfg["api_base"] == "https://custom-api.org/v1"
    assert mcfg["api_key"] == "secret-key"
    
    # 2. Environment variable overrides
    monkeypatch.setenv("ORCHESTRA_MODEL", "env-llm:8b")
    monkeypatch.setenv("ORCHESTRA_API_BASE", "http://remote-server:8000/v1")
    monkeypatch.setenv("ORCHESTRA_API_KEY", "env-token")
    
    cfg_env = ExperimentConfig(task_id="I-01", agent_count=2)
    mcfg_env = cfg_env.resolve_model_config()
    assert mcfg_env["model"] == "env-llm:8b"
    assert mcfg_env["api_base"] == "http://remote-server:8000/v1"
    assert mcfg_env["api_key"] == "env-token"
