"""ORCHESTRA: Experiment Configuration and Provider Resolution Module.

Provides decoupled, reproducible configuration handling across model providers,
configurable agent counts (2, 5, 10, 20, 50, 100), communication protocols,
benchmark task discovery, perturbations, and HITL oversight.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Supported benchmark agent scales in SILO-BENCH
SUPPORTED_AGENT_SCALES = [2, 5, 10, 20, 50, 100]
SUPPORTED_PROTOCOLS = ["msg", "broadcast", "sfs"]

# Canonical 30-task SILO-BENCH suite
ALL_30_TASKS: List[str] = (
    [f"I-{i:02d}" for i in range(1, 11)]
    + [f"II-{i:02d}" for i in range(11, 21)]
    + [f"III-{i:02d}" for i in range(21, 31)]
)

# Stratified 15-task Q1 subset (5 tasks evenly spanning easy, medium, and hard per level)
SELECTED_15_TASKS: List[str] = [
    "I-01", "I-04", "I-07", "I-09", "I-10",
    "II-11", "II-14", "II-15", "II-17", "II-20",
    "III-21", "III-23", "III-25", "III-28", "III-30",
]


def expand_task_ids(task_ids: List[str]) -> List[str]:
    """Expand symbolic task selectors ('selected', 'all') into concrete task IDs."""
    lowered = [t.lower() for t in task_ids]
    if "selected" in lowered:
        return list(SELECTED_15_TASKS)
    if "all" in lowered:
        return list(ALL_30_TASKS)
    return list(task_ids)


@dataclass
class ExperimentConfig:
    """Complete experimental run configuration."""
    
    # Task specification: specify either task_file directly OR task_id + agent_count
    task_file: Optional[str] = None
    task_id: Optional[str] = None
    agent_count: Optional[int] = None
    
    # Communication protocol: 'msg' (P2P), 'broadcast', or 'sfs'
    protocol: str = "msg"
    
    # Model provider configuration
    model: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    
    # Execution constraints
    max_rounds: int = 15
    workspace: str = "workspace"
    experiment_id: Optional[str] = None
    seed: Optional[int] = None
    
    # Perturbation configuration
    perturbation_type: Optional[str] = None
    perturbation_params: Optional[Dict[str, Any]] = None
    
    # Human-in-the-Loop oversight configuration
    hitl_enabled: bool = False
    hitl_mode: str = "audit_only"  # 'audit_only' or 'active_intervention'
    hitl_params: Optional[Dict[str, Any]] = None
    
    def resolve_task_file(self, benchmark_dir: Optional[Path] = None) -> Path:
        """Resolve and validate the benchmark task file path."""
        root_dir = Path(__file__).resolve().parent.parent
        if self.task_file:
            path = Path(self.task_file)
            if not path.is_absolute() and not path.exists():
                # Check relative to benchmark_dir or workspace root
                candidates = [
                    Path.cwd() / path,
                    root_dir / path,
                    Path.cwd() / "silo-bench" / path,
                    root_dir / "silo-bench" / path,
                    Path.cwd() / "benchmarks" / path.name,
                    root_dir / "benchmarks" / path.name,
                    Path.cwd() / "silo-bench" / "benchmarks" / path.name,
                    root_dir / "silo-bench" / "benchmarks" / path.name,
                ]
                if benchmark_dir:
                    candidates.insert(0, benchmark_dir / path.name)
                for cand in candidates:
                    if cand.exists():
                        path = cand
                        break
            if not path.exists():
                raise FileNotFoundError(f"Task file not found: {self.task_file}")
            return path.resolve()
            
        if self.task_id and self.agent_count is not None:
            filename = f"{self.task_id}_n{self.agent_count}.json"
            candidates = [
                Path.cwd() / "benchmarks" / filename,
                root_dir / "benchmarks" / filename,
                Path.cwd() / "silo-bench" / "benchmarks" / filename,
                root_dir / "silo-bench" / "benchmarks" / filename,
            ]
            if benchmark_dir:
                candidates.insert(0, benchmark_dir / filename)
            for cand in candidates:
                if cand.exists():
                    return cand.resolve()
            raise FileNotFoundError(
                f"Task file for task '{self.task_id}' with {self.agent_count} agents not found. "
                f"Expected: {filename} in benchmarks directory."
            )
            
        raise ValueError("Must provide either 'task_file' or both 'task_id' and 'agent_count'.")
        
    def resolve_model_config(self) -> Dict[str, str]:
        """Resolve model name, API base, and API key with precedence:
        1. Explicit config values
        2. Environment variables (ORCHESTRA_MODEL, OPENAI_API_BASE, OPENAI_API_KEY)
        3. Config file fallback (silo-bench/configs/config.yaml or configs/config.yaml)
        4. Sensible local defaults (Ollama gemma4:e2b)
        """
        # 1. Environment variables
        env_model = os.environ.get("ORCHESTRA_MODEL") or os.environ.get("OPENAI_MODEL")
        env_api_base = os.environ.get("ORCHESTRA_API_BASE") or os.environ.get("OPENAI_API_BASE") or os.environ.get("OLLAMA_HOST")
        env_api_key = os.environ.get("ORCHESTRA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        
        # 2. Config file fallback
        yaml_model = None
        yaml_api_base = None
        yaml_api_key = None
        
        for cfg_path in [
            Path.cwd() / "configs" / "config.yaml",
            Path.cwd() / "silo-bench" / "configs" / "config.yaml",
        ]:
            if cfg_path.exists():
                try:
                    import yaml
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    defaults = data.get("defaults", {})
                    yaml_model = defaults.get("model")
                    yaml_api_base = defaults.get("api_base")
                    yaml_api_key = defaults.get("api_key")
                    break
                except Exception:
                    pass
                    
        model = self.model or env_model or yaml_model or "gemma4:e2b"
        api_base = self.api_base or env_api_base or yaml_api_base or "http://localhost:11434/v1"
        api_key = self.api_key or env_api_key or yaml_api_key or "ollama"
        
        return {
            "model": model,
            "api_base": api_base,
            "api_key": api_key,
        }
        
    def validate(self) -> None:
        """Validate configuration settings."""
        if self.protocol not in SUPPORTED_PROTOCOLS:
            raise ValueError(f"Unsupported protocol: '{self.protocol}'. Must be one of {SUPPORTED_PROTOCOLS}")
        if self.agent_count is not None and self.agent_count <= 0:
            raise ValueError(f"Agent count must be positive, got {self.agent_count}")
        if self.max_rounds <= 0:
            raise ValueError(f"Max rounds must be positive, got {self.max_rounds}")
        if self.hitl_mode not in ["audit_only", "active_intervention"]:
            raise ValueError(f"Invalid HITL mode: '{self.hitl_mode}'. Must be 'audit_only' or 'active_intervention'")
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
