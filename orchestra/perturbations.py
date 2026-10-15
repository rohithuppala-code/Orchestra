"""ORCHESTRA: Controlled Perturbations & Organizational Resilience Module.

Implements controlled experimental interventions to measure organizational
adaptation, resilience, and recovery following structural disruptions:
- Fail-stop agent dropout
- Network communication partition
- Message noise / payload corruption
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class BasePerturbation(ABC):
    """Abstract base class for experimental perturbations."""
    
    @abstractmethod
    def name(self) -> str:
        """Name of the perturbation."""
        pass
        
    @abstractmethod
    def apply_pre_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        """Apply perturbation before agents execute the round."""
        pass
        
    @abstractmethod
    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        """Apply perturbation after agents execute the round (e.g., filter messages)."""
        pass


@dataclass
class AgentDropoutPerturbation(BasePerturbation):
    """Simulates fail-stop failure: target agent ceases communication and action."""
    trigger_round: int
    target_agent_id: int
    
    def name(self) -> str:
        return f"AgentDropout(agent={self.target_agent_id}, round={self.trigger_round})"
        
    def apply_pre_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        if current_round >= self.trigger_round:
            # Force target agent's previous state to submitted=True to disable it in run_round
            rounds_dir = case_dir / "rounds"
            prev_round_dir = rounds_dir / f"round-{current_round - 1:06d}"
            state_file = prev_round_dir / f"agent-{self.target_agent_id:03d}" / "state.json"
            if state_file.exists():
                with open(state_file, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                state_data["submitted"] = True  # Engine skips this agent
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(state_data, f)
            return {
                "applied": True,
                "type": "agent_dropout",
                "round": current_round,
                "agent_id": self.target_agent_id,
            }
        return {"applied": False}
        
    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        return {"applied": False}


@dataclass
class CommunicationPartitionPerturbation(BasePerturbation):
    """Partitions the agent network into isolated subsets where cross-group messages are dropped."""
    trigger_round: int
    partition_groups: List[Set[int]]  # e.g., [{0, 1}, {2, 3, 4}]
    
    def name(self) -> str:
        return f"CommunicationPartition(round={self.trigger_round}, groups={self.partition_groups})"
        
    def apply_pre_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        return {"applied": False}
        
    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        """Filter out messages exchanged across partition boundaries in this round's env."""
        if current_round < self.trigger_round:
            return {"applied": False}
            
        dropped_count = 0
        round_dir = case_dir / "rounds" / f"round-{current_round:06d}"
        
        # 1. P2P messages
        msg_dir = round_dir / "env" / "messages"
        if msg_dir.exists():
            for mf in list(msg_dir.glob("*.json")):
                try:
                    with open(mf, "r", encoding="utf-8") as f:
                        mdata = json.load(f)
                    u = mdata.get("sender_id")
                    v = mdata.get("recipient_id")
                    
                    if u is not None and v is not None:
                        same_group = any(u in grp and v in grp for grp in self.partition_groups)
                        if not same_group:
                            mf.unlink(missing_ok=True)
                            dropped_count += 1
                except Exception:
                    pass
                    
        # 2. Broadcasts (if cross-group, isolate)
        bc_dir = round_dir / "env" / "broadcasts"
        if bc_dir.exists():
            for bf in list(bc_dir.glob("*.json")):
                try:
                    with open(bf, "r", encoding="utf-8") as f:
                        bdata = json.load(f)
                    u = bdata.get("sender_id")
                    # If broadcasting agent is isolated, note in metadata
                except Exception:
                    pass
                    
        return {
            "applied": True,
            "type": "communication_partition",
            "round": current_round,
            "dropped_messages": dropped_count,
        }


@dataclass
class MessageCorruptionPerturbation(BasePerturbation):
    """Simulates Byzantine message noise / value corruption to test consensus resilience."""
    trigger_round: int
    target_agent_id: int
    corrupted_value: Any = -999999
    
    def name(self) -> str:
        return f"MessageCorruption(agent={self.target_agent_id}, round={self.trigger_round})"
        
    def apply_pre_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        return {"applied": False}
        
    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        if current_round < self.trigger_round:
            return {"applied": False}
            
        corrupted_count = 0
        round_dir = case_dir / "rounds" / f"round-{current_round:06d}"
        
        # Corrupt P2P messages sent by target_agent_id
        msg_dir = round_dir / "env" / "messages"
        if msg_dir.exists():
            for mf in msg_dir.glob("*.json"):
                try:
                    with open(mf, "r", encoding="utf-8") as f:
                        mdata = json.load(f)
                    if mdata.get("sender_id") == self.target_agent_id:
                        mdata["content"] = str(self.corrupted_value)
                        with open(mf, "w", encoding="utf-8") as f:
                            json.dump(mdata, f)
                        corrupted_count += 1
                except Exception:
                    pass
                    
        return {
            "applied": True,
            "type": "message_corruption",
            "round": current_round,
            "corrupted_messages": corrupted_count,
        }


def create_perturbation(
    perturbation_type: Optional[str],
    params: Optional[Dict[str, Any]] = None,
) -> Optional[BasePerturbation]:
    """Factory function to instantiate perturbations from configuration."""
    if not perturbation_type or perturbation_type.lower() in ("none", "null"):
        return None
        
    p = params or {}
    ptype = perturbation_type.lower()
    
    if ptype == "agent_dropout":
        return AgentDropoutPerturbation(
            trigger_round=int(p.get("round", p.get("trigger_round", 2))),
            target_agent_id=int(p.get("agent_id", p.get("target_agent_id", 1))),
        )
    elif ptype == "communication_partition":
        raw_groups = p.get("partition_groups", [{0, 1}, {2, 3, 4}])
        # Normalize groups to sets of ints
        groups = [set(g) for g in raw_groups]
        return CommunicationPartitionPerturbation(
            trigger_round=int(p.get("round", p.get("trigger_round", 2))),
            partition_groups=groups,
        )
    elif ptype == "message_corruption":
        return MessageCorruptionPerturbation(
            trigger_round=int(p.get("round", p.get("trigger_round", 2))),
            target_agent_id=int(p.get("agent_id", p.get("target_agent_id", 1))),
            corrupted_value=p.get("corrupted_value", -999999),
        )
    else:
        raise ValueError(f"Unknown perturbation type: '{perturbation_type}'")
