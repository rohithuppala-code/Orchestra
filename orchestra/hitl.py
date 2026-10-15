"""ORCHESTRA: Human-in-the-Loop (HITL) Organizational Oversight Module.

Monitors emergent organizational evolution to detect, record, and optionally
constrain structural boundary violations:
- Communication monopolization (single agent bottleneck / dominance)
- Agent starvation / isolation
- Coordination stagnation / deadlock

Supports audit-only and active corrective intervention modes, maintaining a full
trace of all interventions for empirical reproducibility.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from orchestra.instrumentation import RoundNetworkSnapshot


class HITLMode(str, Enum):
    AUDIT_ONLY = "audit_only"
    ACTIVE_INTERVENTION = "active_intervention"


@dataclass
class BoundaryViolation:
    """Record of an organizational boundary violation."""
    round_num: int
    violation_type: str  # 'monopolization', 'isolation', 'stagnation'
    agent_id: Optional[int]
    description: str
    metric_value: float
    threshold: float
    action_taken: str


class HITLSupervisor:
    """Supervises agent organizational evolution and records boundary interventions."""
    
    def __init__(
        self,
        mode: HITLMode | str = HITLMode.AUDIT_ONLY,
        monopolization_threshold: float = 0.85,
        max_isolated_rounds: int = 2,
        stagnation_threshold_rounds: int = 3,
    ):
        if isinstance(mode, str):
            mode = HITLMode(mode)
        self.mode = mode
        self.monopolization_threshold = monopolization_threshold
        self.max_isolated_rounds = max_isolated_rounds
        self.stagnation_threshold_rounds = stagnation_threshold_rounds
        self.violations: List[BoundaryViolation] = []
        self._isolation_history: Dict[int, int] = {}  # agent_id -> consecutive rounds isolated
        self._zero_msg_rounds: int = 0
        
    def inspect_round(
        self,
        case_dir: Path,
        snapshot: RoundNetworkSnapshot,
    ) -> List[BoundaryViolation]:
        """Inspect a round snapshot against organizational boundaries."""
        new_violations = []
        r = snapshot.round_num
        n = snapshot.num_agents
        
        # 1. Monopolization check (single agent out-degree dominance)
        total_msgs = snapshot.total_messages_this_round
        if total_msgs > 0 and n > 2:
            for aid, out_d in snapshot.out_degrees.items():
                ratio = out_d / total_msgs
                if ratio >= self.monopolization_threshold:
                    v = BoundaryViolation(
                        round_num=r,
                        violation_type="monopolization",
                        agent_id=aid,
                        description=f"Agent {aid} sent {ratio:.1%} of all messages this round (threshold: {self.monopolization_threshold:.1%})",
                        metric_value=ratio,
                        threshold=self.monopolization_threshold,
                        action_taken="logged" if self.mode == HITLMode.AUDIT_ONLY else "advisory_logged",
                    )
                    new_violations.append(v)
                    
        # 2. Isolation / Starvation check
        for aid in range(n):
            in_d = snapshot.in_degrees.get(aid, 0)
            out_d = snapshot.out_degrees.get(aid, 0)
            # Active tool calls count
            tools_used = sum(snapshot.tool_counts.get(aid, {}).values()) if snapshot.tool_counts else 0
            if in_d == 0 and out_d == 0 and tools_used == 0:
                self._isolation_history[aid] = self._isolation_history.get(aid, 0) + 1
            else:
                self._isolation_history[aid] = 0
                
            if self._isolation_history[aid] >= self.max_isolated_rounds:
                v = BoundaryViolation(
                    round_num=r,
                    violation_type="isolation",
                    agent_id=aid,
                    description=f"Agent {aid} completely isolated for {self._isolation_history[aid]} consecutive rounds",
                    metric_value=float(self._isolation_history[aid]),
                    threshold=float(self.max_isolated_rounds),
                    action_taken="logged" if self.mode == HITLMode.AUDIT_ONLY else "reconnect_prompt",
                )
                new_violations.append(v)
                
        # 3. Coordination Stagnation / Deadlock check
        if total_msgs == 0:
            self._zero_msg_rounds += 1
        else:
            self._zero_msg_rounds = 0
            
        if self._zero_msg_rounds >= self.stagnation_threshold_rounds:
            v = BoundaryViolation(
                round_num=r,
                violation_type="stagnation",
                agent_id=None,
                description=f"Zero communication messages observed across {self._zero_msg_rounds} consecutive rounds",
                metric_value=float(self._zero_msg_rounds),
                threshold=float(self.stagnation_threshold_rounds),
                action_taken="logged" if self.mode == HITLMode.AUDIT_ONLY else "stagnation_advisory",
            )
            new_violations.append(v)
                
        # 4. Log violations to disk
        if new_violations:
            self.violations.extend(new_violations)
            log_file = Path(case_dir) / "hitl_interventions.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                for viol in new_violations:
                    f.write(json.dumps(asdict(viol)) + "\n")
                    
        return new_violations
        
    def get_summary(self) -> Dict[str, Any]:
        """Return summary of all observed boundary violations."""
        by_type: Dict[str, int] = {}
        for v in self.violations:
            by_type[v.violation_type] = by_type.get(v.violation_type, 0) + 1
        return {
            "total_violations": len(self.violations),
            "mode": self.mode.value,
            "violations_by_type": by_type,
        }
