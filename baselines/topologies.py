"""ORCHESTRA: Multi-Agent Baseline Communication Topologies & Role Injections.

Implements the 5 foundational and state-of-the-art multi-agent baselines
derived directly from published literature without modifying core benchmark logic:
1. Independent Agents (No Communication / Majority Vote Ensemble; Wang et al., ICLR 2023)
2. Fully Connected Broadcast (Flat Multi-Agent Debate; ChatDev, Qian et al., ACL 2024; Du et al., 2023)
3. Central Coordinator (Star Hub-and-Spoke; AutoGen, Wu et al., ICLR 2024)
4. Hierarchical Coordinator (Multi-Tier Tree / Chain of Command; MacNet, Wang et al., 2024/2025)
5. Fixed Predefined Roles (Static Prompt Role Assignment; MetaGPT, Hong et al., ICLR 2024 Oral)
+ ORCHESTRA (Emergent Dynamic Self-Organization)
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Set, Tuple


class BaseTopologyEnforcer(ABC):
    """Abstract base class for baseline communication topologies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this baseline."""
        ...

    @property
    @abstractmethod
    def citation(self) -> str:
        """Paper citation defining this paradigm."""
        ...

    def apply_initialization(self, case_dir: Path, num_agents: int) -> Dict[str, Any]:
        """Apply pre-execution role conditioning or prompt injection in round-000000."""
        return {"applied": False}

    def apply_pre_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        """Hook called immediately before agents execute a round."""
        return {"applied": False}

    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        """Hook called immediately after agents generate tool calls.
        Filters, drops, or alters message transmissions to enforce the topology.
        """
        return {"applied": False}


class IndependentTopology(BaseTopologyEnforcer):
    """Baseline 1: Independent Agents (Wang et al., ICLR 2023).
    Agents operate in complete isolation with zero peer communication.
    All cross-agent messages are dropped.
    """

    @property
    def name(self) -> str:
        return "independent"

    @property
    def citation(self) -> str:
        return "Wang et al. (ICLR 2023)"

    def apply_initialization(self, case_dir: Path, num_agents: int) -> Dict[str, Any]:
        """Condition agents that they operate independently without peer communication."""
        round0_dir = case_dir / "rounds" / "round-000000"
        if not round0_dir.exists():
            return {"applied": False, "reason": "round0_dir not found"}

        for i in range(num_agents):
            agent_ctx_file = round0_dir / f"agent-{i:03d}" / "context.json"
            if not agent_ctx_file.exists():
                continue
            try:
                with open(agent_ctx_file, "r", encoding="utf-8") as f:
                    ctx_data = json.load(f)
                info_text = (
                    "\n\n[INDEPENDENT ENSEMBLE EXECUTION]\n"
                    "You are operating independently without peer communication. "
                    "Analyze your local data shard directly, compute your solution, and submit your final answer using submit_result."
                )
                messages = ctx_data.get("messages", [])
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += info_text
                else:
                    messages.insert(0, {"role": "system", "content": info_text.strip()})
                ctx_data["messages"] = messages
                with open(agent_ctx_file, "w", encoding="utf-8") as f:
                    json.dump(ctx_data, f, indent=2)
            except Exception:
                pass
        return {"applied": True, "rule": "independent_prompt_conditioning"}

    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        round_dir = case_dir / "rounds" / f"round-{current_round:06d}"
        msg_dir = round_dir / "env" / "messages"
        dropped = 0
        if msg_dir.exists():
            for mf in list(msg_dir.glob("*.json")):
                mf.unlink(missing_ok=True)
                dropped += 1
        return {"applied": True, "dropped_messages": dropped, "rule": "drop_all_p2p"}


class BroadcastTopology(BaseTopologyEnforcer):
    """Baseline 2: Fully Connected Broadcast / Flat Debate (Qian et al., ACL 2024; Du et al., 2023).
    All agents communicate via unconstrained broadcast or full mesh.
    No messages are filtered.
    """

    @property
    def name(self) -> str:
        return "broadcast"

    @property
    def citation(self) -> str:
        return "Qian et al. (ACL 2024); Du et al. (ICML 2023)"

    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        return {"applied": False, "rule": "all_to_all_permitted"}


class CentralCoordinatorTopology(BaseTopologyEnforcer):
    """Baseline 3: Central Coordinator / Star Hub (Wu et al., AutoGen 2024).
    Agent 0 is the designated central hub.
    Worker agents (1..N-1) can only communicate with Agent 0.
    Direct worker-to-worker messages are strictly dropped.
    """

    def __init__(self, hub_id: int = 0) -> None:
        self.hub_id = hub_id

    @property
    def name(self) -> str:
        return "central_coordinator"

    @property
    def citation(self) -> str:
        return "Wu et al. (AutoGen / ICLR 2024)"

    def apply_initialization(self, case_dir: Path, num_agents: int) -> Dict[str, Any]:
        """Condition agents on the Star Hub-and-Spoke coordination protocol."""
        round0_dir = case_dir / "rounds" / "round-000000"
        if not round0_dir.exists():
            return {"applied": False, "reason": "round0_dir not found"}

        for i in range(num_agents):
            agent_ctx_file = round0_dir / f"agent-{i:03d}" / "context.json"
            if not agent_ctx_file.exists():
                continue
            try:
                with open(agent_ctx_file, "r", encoding="utf-8") as f:
                    ctx_data = json.load(f)

                if i == self.hub_id:
                    role_text = (
                        f"\n\n[STAR HUB COORDINATOR TOPOLOGY (AutoGen Style)]\n"
                        f"You are designated as the Central Hub Coordinator (Agent {self.hub_id}). "
                        f"All worker agents (1 to {num_agents - 1}) can only communicate with you. "
                        f"Collect data from all workers, synthesize the global result, and coordinate the response."
                    )
                else:
                    role_text = (
                        f"\n\n[STAR SPOKE WORKER TOPOLOGY (AutoGen Style)]\n"
                        f"You are operating in a Central Coordinator Star Topology. "
                        f"Agent {self.hub_id} is the designated Central Coordinator. All communication must flow through Agent {self.hub_id}. "
                        f"Send your local data and report to Agent {self.hub_id} (target_id: {self.hub_id}). Do NOT message other worker peers."
                    )

                messages = ctx_data.get("messages", [])
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += role_text
                else:
                    messages.insert(0, {"role": "system", "content": role_text.strip()})
                ctx_data["messages"] = messages
                with open(agent_ctx_file, "w", encoding="utf-8") as f:
                    json.dump(ctx_data, f, indent=2)
            except Exception:
                pass
        return {"applied": True, "hub_id": self.hub_id, "num_agents": num_agents}

    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        round_dir = case_dir / "rounds" / f"round-{current_round:06d}"
        msg_dir = round_dir / "env" / "messages"
        dropped = 0
        kept = 0

        if msg_dir.exists():
            for mf in list(msg_dir.glob("*.json")):
                try:
                    with open(mf, "r", encoding="utf-8") as f:
                        mdata = json.load(f)
                    u = mdata.get("sender_id")
                    v = mdata.get("recipient_id")

                    # Allowed: u == hub_id or v == hub_id
                    if u != self.hub_id and v != self.hub_id:
                        mf.unlink(missing_ok=True)
                        dropped += 1
                    else:
                        kept += 1
                except Exception:
                    pass

        return {"applied": True, "dropped_messages": dropped, "kept_messages": kept, "hub_id": self.hub_id}


class HierarchicalCoordinatorTopology(BaseTopologyEnforcer):
    """Baseline 4: Hierarchical Tree Coordinator (MacNet, Wang et al., 2024/2025).
    Enforces a strict multi-tier organizational tree / chain-of-command.
    For N=2: 0 <-> 1
    For N=5: 0 (Executive) <-> {1, 2} (Leads); 1 <-> 3 (Worker); 2 <-> 4 (Worker)
    For N=10: 0 <-> {1, 2, 3}; 1 <-> {4, 5}; 2 <-> {6, 7}; 3 <-> {8, 9}
    """

    @property
    def name(self) -> str:
        return "hierarchical_coordinator"

    @property
    def citation(self) -> str:
        return "Wang et al. (MacNet, ICLR 2024 / Neural Networks 2025)"

    def _get_tree_edges(self, num_agents: int) -> Set[Tuple[int, int]]:
        """Compute allowed undirected tree edges for given population scale."""
        edges: Set[Tuple[int, int]] = set()

        if num_agents <= 2:
            edges.add((0, 1))
        elif num_agents <= 5:
            # 0 is Root. 1 and 2 are Leads. 3 reports to 1, 4 reports to 2.
            edges.add((0, 1))
            edges.add((0, 2))
            if num_agents > 3:
                edges.add((1, 3))
            if num_agents > 4:
                edges.add((2, 4))
        else:
            # N=10 or larger
            # 0 is Root. Leads: 1, 2, 3
            leads = [1, 2, 3]
            for lead in leads:
                if lead < num_agents:
                    edges.add((0, lead))

            # Distribute workers among leads
            curr_lead_idx = 0
            for worker in range(4, num_agents):
                lead = leads[curr_lead_idx % len(leads)]
                edges.add((lead, worker))
                curr_lead_idx += 1

        # Symmetric set for undirected communication
        symmetric_edges: Set[Tuple[int, int]] = set()
        for u, v in edges:
            symmetric_edges.add((u, v))
            symmetric_edges.add((v, u))
        return symmetric_edges

    def apply_initialization(self, case_dir: Path, num_agents: int) -> Dict[str, Any]:
        """Condition agents on the Hierarchical Tree communication channels."""
        round0_dir = case_dir / "rounds" / "round-000000"
        if not round0_dir.exists():
            return {"applied": False, "reason": "round0_dir not found"}

        allowed_edges = self._get_tree_edges(num_agents)

        for i in range(num_agents):
            agent_ctx_file = round0_dir / f"agent-{i:03d}" / "context.json"
            if not agent_ctx_file.exists():
                continue
            try:
                with open(agent_ctx_file, "r", encoding="utf-8") as f:
                    ctx_data = json.load(f)

                # Find allowed communication partners for agent i
                partners = sorted([v for (u, v) in allowed_edges if u == i])
                role_text = (
                    f"\n\n[HIERARCHICAL TREE COORDINATOR TOPOLOGY (MacNet Style)]\n"
                    f"You (Agent {i}) are operating within a structured multi-tier organizational tree. "
                    f"Your direct chain-of-command communication channels are strictly: Agents {partners}. "
                    f"Only exchange messages with these assigned tree neighbors (target_id in {partners}). "
                    f"Cross-level or bypass messages to other agents will be filtered by the hierarchy."
                )

                messages = ctx_data.get("messages", [])
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += role_text
                else:
                    messages.insert(0, {"role": "system", "content": role_text.strip()})
                ctx_data["messages"] = messages
                with open(agent_ctx_file, "w", encoding="utf-8") as f:
                    json.dump(ctx_data, f, indent=2)
            except Exception:
                pass
        return {"applied": True, "num_agents": num_agents}

    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        round_dir = case_dir / "rounds" / f"round-{current_round:06d}"
        msg_dir = round_dir / "env" / "messages"
        allowed_edges = self._get_tree_edges(num_agents)

        dropped = 0
        kept = 0

        if msg_dir.exists():
            for mf in list(msg_dir.glob("*.json")):
                try:
                    with open(mf, "r", encoding="utf-8") as f:
                        mdata = json.load(f)
                    u = mdata.get("sender_id")
                    v = mdata.get("recipient_id")

                    if u is not None and v is not None and (u, v) not in allowed_edges:
                        mf.unlink(missing_ok=True)
                        dropped += 1
                    else:
                        kept += 1
                except Exception:
                    pass

        return {"applied": True, "dropped_messages": dropped, "kept_messages": kept}


class FixedRolesTopology(BaseTopologyEnforcer):
    """Baseline 5: Fixed Predefined Roles (MetaGPT, Hong et al., ICLR 2024 Oral).
    Static upfront role conditioning via prompt injection:
    - Agent 0 is designated Chief Project Coordinator.
    - Agents 1..N-1 are designated Subordinate Functional Specialists.
    Communication is structured strictly through Agent 0.
    """

    def __init__(self, leader_id: int = 0) -> None:
        self.leader_id = leader_id

    @property
    def name(self) -> str:
        return "fixed_roles"

    @property
    def citation(self) -> str:
        return "Hong et al. (MetaGPT, ICLR 2024 Oral)"

    def apply_initialization(self, case_dir: Path, num_agents: int) -> Dict[str, Any]:
        """Inject explicit role conditioning into initial context prompts."""
        round0_dir = case_dir / "rounds" / "round-000000"
        if not round0_dir.exists():
            return {"applied": False, "reason": "round0_dir not found"}

        for i in range(num_agents):
            agent_ctx_file = round0_dir / f"agent-{i:03d}" / "context.json"
            if not agent_ctx_file.exists():
                continue

            try:
                with open(agent_ctx_file, "r", encoding="utf-8") as f:
                    ctx_data = json.load(f)

                if i == self.leader_id:
                    role_text = (
                        "\n\n[SYSTEM ROLE INJECTION: LEAD ARCHITECT & PRIMARY COORDINATOR]\n"
                        "You are designated as the authoritative Chief Leader of this multi-agent collective. "
                        "You are responsible for directing subordinate agents, collecting their local data shards, "
                        "synthesizing the global algorithmic result, and submitting the final consensus. "
                        "Command your subordinates to send their data directly to you."
                    )
                else:
                    role_text = (
                        f"\n\n[SYSTEM ROLE INJECTION: SUBORDINATE FUNCTIONAL SPECIALIST (Agent {i})]\n"
                        f"You are a subordinate worker reporting strictly to Agent {self.leader_id} (The Lead Coordinator). "
                        f"Do NOT initiate autonomous routing or communicate with other subordinate peers. "
                        f"When prompted, report your local data shard directly to Agent {self.leader_id} and follow their instructions."
                    )

                # Prepend or append to system prompt or first message
                messages = ctx_data.get("messages", [])
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] += role_text
                else:
                    messages.insert(0, {"role": "system", "content": role_text.strip()})

                ctx_data["messages"] = messages
                with open(agent_ctx_file, "w", encoding="utf-8") as f:
                    json.dump(ctx_data, f, indent=2)

            except Exception as e:
                print(f"[FixedRolesTopology] Warning injecting role for agent {i}: {e}")

        return {"applied": True, "leader_id": self.leader_id, "num_agents": num_agents}

    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        """Workers only report to the leader; worker-worker communication is blocked."""
        round_dir = case_dir / "rounds" / f"round-{current_round:06d}"
        msg_dir = round_dir / "env" / "messages"
        dropped = 0
        kept = 0

        if msg_dir.exists():
            for mf in list(msg_dir.glob("*.json")):
                try:
                    with open(mf, "r", encoding="utf-8") as f:
                        mdata = json.load(f)
                    u = mdata.get("sender_id")
                    v = mdata.get("recipient_id")

                    if u != self.leader_id and v != self.leader_id:
                        mf.unlink(missing_ok=True)
                        dropped += 1
                    else:
                        kept += 1
                except Exception:
                    pass

        return {"applied": True, "dropped_messages": dropped, "kept_messages": kept, "leader_id": self.leader_id}


class OrchestraTopology(BaseTopologyEnforcer):
    """ORCHESTRA: Emergent Dynamic Organizational Evolution (Our Method).
    Zero predefined roles, unconstrained peer-to-peer communication,
    and adaptive emergent self-organization.
    """

    @property
    def name(self) -> str:
        return "orchestra"

    @property
    def citation(self) -> str:
        return "ORCHESTRA (This Work)"

    def apply_post_round(self, case_dir: Path, current_round: int, num_agents: int) -> Dict[str, Any]:
        return {"applied": True, "rule": "emergent_unconstrained_p2p"}


SUPPORTED_BASELINES: Dict[str, type[BaseTopologyEnforcer]] = {
    "independent": IndependentTopology,
    "broadcast": BroadcastTopology,
    "central_coordinator": CentralCoordinatorTopology,
    "hierarchical_coordinator": HierarchicalCoordinatorTopology,
    "fixed_roles": FixedRolesTopology,
    "orchestra": OrchestraTopology,
}

# Active non-redundant competing baselines executed by baselines.batch_runner
# Note: 'broadcast' runs inside ORCHESTRA (protocol='broadcast') to avoid duplicate runs,
# and 'fixed_roles' shares CentralCoordinator's exact Star graph around Agent 0.
EXTERNAL_BASELINES: list[str] = [
    "independent",
    "central_coordinator",
    "hierarchical_coordinator",
]


def create_baseline_topology(baseline_name: str, seed: int = 42, **kwargs: Any) -> BaseTopologyEnforcer:
    """Instantiate a baseline topology enforcer with strict typing."""
    bname = baseline_name.lower().strip()
    if bname not in SUPPORTED_BASELINES:
        raise ValueError(
            f"Unknown baseline: '{baseline_name}'. Supported baselines: {list(SUPPORTED_BASELINES.keys())}"
        )

    if bname == "independent":
        return IndependentTopology()
    elif bname == "broadcast":
        return BroadcastTopology()
    elif bname == "central_coordinator":
        hub_id = int(kwargs.get("hub_id", kwargs.get("leader_id", 0)))
        return CentralCoordinatorTopology(hub_id=hub_id)
    elif bname == "hierarchical_coordinator":
        return HierarchicalCoordinatorTopology()
    elif bname == "fixed_roles":
        leader_id = int(kwargs.get("leader_id", 0))
        return FixedRolesTopology(leader_id=leader_id)
    elif bname == "orchestra":
        return OrchestraTopology()

    return OrchestraTopology()
