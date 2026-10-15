"""ORCHESTRA: Research Instrumentation & Organizational Metrics Module.

Extracts, tracks, and computes round-by-round organizational and network
metrics from SILO-BENCH case executions without modifying benchmark evaluation.
Supports P2P messaging ('msg'), broadcast ('broadcast'), and shared file system ('sfs')
across configurable agent populations (2, 5, 10, 20, 50, 100).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np


@dataclass
class RoundNetworkSnapshot:
    """Snapshot of communication network and agent activity at a single round."""
    round_num: int
    num_agents: int
    active_agents: List[int]
    
    # Message / Communication events this round
    edges: List[Dict[str, Any]]  # [{"from": u, "to": v, "weight": count}]
    total_messages_this_round: int
    
    # Graph metrics for this round (instantaneous)
    density: float
    reciprocity: float
    in_degrees: Dict[int, int]
    out_degrees: Dict[int, int]
    betweenness_centrality: Dict[int, float]
    closeness_centrality: Dict[int, float]
    clustering_coefficient: float
    
    # Cumulative graph metrics up to this round
    cumulative_density: float
    cumulative_edges_count: int
    cumulative_reciprocity: float
    cumulative_betweenness: Dict[int, float]
    
    # Structural evolution (distance from previous round)
    jaccard_distance_from_prev: float  # 0 = identical edges, 1 = completely new edges
    adjacency_frobenius_diff: float
    
    # Tool call distributions this round
    tool_counts: Dict[int, Dict[str, int]] = field(default_factory=dict)  # agent_id -> {tool_name: count}


@dataclass
class OrganizationalProfile:
    """Summary of organizational structure, specialization, and evolution for a case."""
    case_id: str
    task_id: str
    protocol: str
    num_agents: int
    total_rounds: int
    
    # Round-by-round snapshots
    snapshots: List[RoundNetworkSnapshot] = field(default_factory=list)
    
    # Emergent Specialization Metrics (over whole run)
    gini_out_degree: float = 0.0  # High = centralized dissemination, Low = equal participation
    gini_in_degree: float = 0.0   # High = centralized aggregation
    gini_tool_usage: Dict[str, float] = field(default_factory=dict)
    
    # Role Classifications per agent
    # e.g., 'Hub_Coordinator', 'Broadcaster_Disseminator', 'Aggregator_Collector',
    # 'Peer_Collaborator', 'Isolated'
    agent_roles: Dict[int, str] = field(default_factory=dict)
    
    # Structural Stability & Evolution
    mean_structural_drift: float = 0.0  # Mean Jaccard distance between consecutive rounds
    final_network_entropy: float = 0.0
    network_diameter: Optional[int] = None
    is_connected: bool = False
    
    # Benchmark correlation hooks
    success: bool = False
    success_rate: float = 0.0
    partial_correctness: float = 0.0
    token_consumption: float = 0.0
    communication_density: float = 0.0


def calculate_gini(array: np.ndarray | List[float]) -> float:
    """Calculate the Gini coefficient of a numeric array.
    
    0 = complete equality, 1 = complete inequality.
    """
    if len(array) == 0:
        return 0.0
    arr = np.asarray(array, dtype=float)
    if np.amin(arr) < 0:
        arr -= np.amin(arr)
    if np.sum(arr) == 0:
        return 0.0
    arr = np.sort(arr)
    n = len(arr)
    index = np.arange(1, n + 1)
    return float((np.sum((2 * index - n - 1) * arr)) / (n * np.sum(arr)))


def calculate_entropy(probs: List[float]) -> float:
    """Compute Shannon entropy given a list of non-negative values."""
    s = sum(probs)
    if s == 0:
        return 0.0
    norm_probs = [p / s for p in probs if p > 0]
    return float(-sum(p * np.log2(p) for p in norm_probs))


def parse_round_communication(
    round_dir: Path,
    protocol: str,
    num_agents: int,
    agent_logs: Optional[Dict[int, List[Dict[str, Any]]]] = None,
    r: int = 1,
) -> Tuple[Dict[Tuple[int, int], int], int]:
    """Parse communication events for a given round based on protocol."""
    edge_counts: Dict[Tuple[int, int], int] = {}
    total_msgs = 0
    
    if protocol == "msg":
        msg_dir = round_dir / "env" / "messages"
        if msg_dir.exists():
            for mf in msg_dir.glob("*.json"):
                try:
                    with open(mf, "r", encoding="utf-8") as f:
                        mdata = json.load(f)
                    u = mdata.get("sender_id")
                    v = mdata.get("recipient_id")
                    if u is not None and v is not None and 0 <= u < num_agents and 0 <= v < num_agents:
                        edge_counts[(u, v)] = edge_counts.get((u, v), 0) + 1
                        total_msgs += 1
                except Exception:
                    pass
                    
    elif protocol == "broadcast":
        bc_dir = round_dir / "env" / "broadcasts"
        if bc_dir.exists():
            for bf in bc_dir.glob("*.json"):
                try:
                    with open(bf, "r", encoding="utf-8") as f:
                        bdata = json.load(f)
                    u = bdata.get("sender_id")
                    if u is not None and 0 <= u < num_agents:
                        for v in range(num_agents):
                            if v != u:
                                edge_counts[(u, v)] = edge_counts.get((u, v), 0) + 1
                                total_msgs += 1
                except Exception:
                    pass
                    
    elif protocol == "sfs":
        # In Shared File System, track writes as dissemination to peers
        # and reads as directed information flow from writer to reader
        kv_file = round_dir / "env" / "shared_kv.json"
        writers_by_path: Dict[str, int] = {}
        if kv_file.exists():
            try:
                with open(kv_file, "r", encoding="utf-8") as f:
                    kv = json.load(f)
                for path, entry in kv.items():
                    if isinstance(entry, dict):
                        u = entry.get("modified_by")
                        if u is not None and 0 <= u < num_agents:
                            writers_by_path[path] = u
                            if entry.get("modified_at_round") == r:
                                # Write in this round broadcasts availability
                                for v in range(num_agents):
                                    if v != u:
                                        edge_counts[(u, v)] = edge_counts.get((u, v), 0) + 1
                                        total_msgs += 1
            except Exception:
                pass
                
        # Also inspect agent read calls if logs are provided
        if agent_logs:
            for aid, entries in agent_logs.items():
                if 0 <= aid < num_agents:
                    for e in entries:
                        if e.get("round") == r and e.get("event") == "tool_call" and e.get("tool") == "read_file":
                            read_path = e.get("args", {}).get("path")
                            writer = writers_by_path.get(read_path)
                            if writer is not None and writer != aid:
                                edge_counts[(writer, aid)] = edge_counts.get((writer, aid), 0) + 1
                                total_msgs += 1
                                
    return edge_counts, total_msgs


def extract_round_snapshot(
    case_dir: str | Path,
    round_num: int,
    num_agents: int,
    protocol: str,
    prev_graph: Optional[nx.DiGraph] = None,
    cumulative_graph: Optional[nx.DiGraph] = None,
    agent_logs: Optional[Dict[int, List[Dict[str, Any]]]] = None,
) -> RoundNetworkSnapshot:
    """Extract a single round network snapshot."""
    case_path = Path(case_dir)
    round_dir = case_path / "rounds" / f"round-{round_num:06d}"
    
    round_graph = nx.DiGraph()
    round_graph.add_nodes_from(range(num_agents))
    
    if cumulative_graph is None:
        cumulative_graph = nx.DiGraph()
        cumulative_graph.add_nodes_from(range(num_agents))
        
    edge_counts: Dict[Tuple[int, int], int] = {}
    total_msgs = 0
    if round_dir.exists():
        edge_counts, total_msgs = parse_round_communication(
            round_dir=round_dir,
            protocol=protocol,
            num_agents=num_agents,
            agent_logs=agent_logs,
            r=round_num,
        )
        
    edges_list = []
    for (u, v), w in edge_counts.items():
        round_graph.add_edge(u, v, weight=w)
        if cumulative_graph.has_edge(u, v):
            cumulative_graph[u][v]["weight"] += w
        else:
            cumulative_graph.add_edge(u, v, weight=w)
        edges_list.append({"from": u, "to": v, "weight": w})
        
    density = nx.density(round_graph)
    try:
        reciprocity = nx.reciprocity(round_graph)
    except Exception:
        reciprocity = 0.0
        
    in_degrees = {i: round_graph.in_degree(i) for i in range(num_agents)}
    out_degrees = {i: round_graph.out_degree(i) for i in range(num_agents)}
    
    try:
        betweenness = nx.betweenness_centrality(round_graph, weight=None)
    except Exception:
        betweenness = {i: 0.0 for i in range(num_agents)}
        
    try:
        closeness = nx.closeness_centrality(round_graph)
    except Exception:
        closeness = {i: 0.0 for i in range(num_agents)}
        
    try:
        clustering = nx.average_clustering(round_graph.to_undirected())
    except Exception:
        clustering = 0.0
        
    cum_density = nx.density(cumulative_graph)
    try:
        cum_reciprocity = nx.reciprocity(cumulative_graph)
    except Exception:
        cum_reciprocity = 0.0
    try:
        cum_betweenness = nx.betweenness_centrality(cumulative_graph, weight="weight")
    except Exception:
        cum_betweenness = {i: 0.0 for i in range(num_agents)}
        
    if prev_graph is not None:
        prev_edges = set(prev_graph.edges())
        curr_edges = set(round_graph.edges())
        union_len = len(prev_edges.union(curr_edges))
        jaccard_dist = 1.0 - (len(prev_edges.intersection(curr_edges)) / union_len) if union_len > 0 else 0.0
        
        prev_adj = nx.to_numpy_array(prev_graph, nodelist=range(num_agents))
        curr_adj = nx.to_numpy_array(round_graph, nodelist=range(num_agents))
        frob_diff = float(np.linalg.norm(curr_adj - prev_adj))
    else:
        jaccard_dist = 0.0
        frob_diff = 0.0
        
    tool_counts: Dict[int, Dict[str, int]] = {i: {} for i in range(num_agents)}
    if agent_logs:
        for aid, entries in agent_logs.items():
            if 0 <= aid < num_agents:
                for e in entries:
                    if e.get("round") == round_num and e.get("event") == "tool_call":
                        t = e.get("tool", "unknown")
                        tool_counts[aid][t] = tool_counts[aid].get(t, 0) + 1
                        
    active_agents = [
        i for i in range(num_agents)
        if out_degrees[i] > 0 or in_degrees[i] > 0 or sum(tool_counts[i].values()) > 0
    ]
    
    return RoundNetworkSnapshot(
        round_num=round_num,
        num_agents=num_agents,
        active_agents=active_agents,
        edges=edges_list,
        total_messages_this_round=total_msgs,
        density=density,
        reciprocity=reciprocity,
        in_degrees=in_degrees,
        out_degrees=out_degrees,
        betweenness_centrality=betweenness,
        closeness_centrality=closeness,
        clustering_coefficient=clustering,
        cumulative_density=cum_density,
        cumulative_edges_count=len(cumulative_graph.edges()),
        cumulative_reciprocity=cum_reciprocity,
        cumulative_betweenness=cum_betweenness,
        jaccard_distance_from_prev=jaccard_dist,
        adjacency_frobenius_diff=frob_diff,
        tool_counts=tool_counts,
    )


def extract_case_instrumentation(case_dir: str | Path) -> OrganizationalProfile:
    """Analyze a completed or in-progress SILO-BENCH case directory.
    
    Parses rounds, messages/broadcasts/sfs, agent logs, and results.json
    to generate a complete OrganizationalProfile.
    """
    case_path = Path(case_dir)
    metadata_file = case_path / "metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Case metadata not found at {metadata_file}")
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    case_id = metadata["case_id"]
    task_id = metadata["task"]["case_id"]
    protocol = metadata["config"]["protocol"]
    num_agents = metadata["config"]["agent_count"]
    current_round = metadata["execution"]["current_round"]
    
    logs_dir = case_path / "logs"
    agent_logs: Dict[int, List[Dict[str, Any]]] = {}
    if logs_dir.exists():
        for log_file in logs_dir.glob("agent-*.jsonl"):
            try:
                aid = int(log_file.stem.split("-")[1])
                entries = []
                with open(log_file, "r", encoding="utf-8") as lf:
                    for line in lf:
                        if line.strip():
                            entries.append(json.loads(line))
                agent_logs[aid] = entries
            except Exception:
                pass
                
    cumulative_graph = nx.DiGraph()
    cumulative_graph.add_nodes_from(range(num_agents))
    prev_graph: Optional[nx.DiGraph] = None
    snapshots: List[RoundNetworkSnapshot] = []
    
    for r in range(1, current_round + 1):
        snapshot = extract_round_snapshot(
            case_dir=case_path,
            round_num=r,
            num_agents=num_agents,
            protocol=protocol,
            prev_graph=prev_graph,
            cumulative_graph=cumulative_graph,
            agent_logs=agent_logs,
        )
        snapshots.append(snapshot)
        
        # Build round_graph for next iteration's prev_graph
        rg = nx.DiGraph()
        rg.add_nodes_from(range(num_agents))
        for e in snapshot.edges:
            rg.add_edge(e["from"], e["to"], weight=e.get("weight", 1))
        prev_graph = rg
        
    all_out_degrees = np.array([cumulative_graph.out_degree(i, weight="weight") for i in range(num_agents)])
    all_in_degrees = np.array([cumulative_graph.in_degree(i, weight="weight") for i in range(num_agents)])
    
    gini_out = calculate_gini(all_out_degrees)
    gini_in = calculate_gini(all_in_degrees)
    
    tool_totals: Dict[str, List[int]] = {}
    for aid in range(num_agents):
        agent_entries = agent_logs.get(aid, [])
        for e in agent_entries:
            if e.get("event") == "tool_call":
                t = e.get("tool", "unknown")
                if t not in tool_totals:
                    tool_totals[t] = [0] * num_agents
                tool_totals[t][aid] += 1
                
    gini_tools = {t: calculate_gini(np.array(counts)) for t, counts in tool_totals.items()}
    
    # Role Classification (Operational definitions grounded in network metrics)
    agent_roles: Dict[int, str] = {}
    cum_bet = nx.betweenness_centrality(cumulative_graph, weight="weight")
    mean_out = float(np.mean(all_out_degrees)) if len(all_out_degrees) > 0 else 0
    mean_in = float(np.mean(all_in_degrees)) if len(all_in_degrees) > 0 else 0
    
    for aid in range(num_agents):
        out_d = cumulative_graph.out_degree(aid, weight="weight")
        in_d = cumulative_graph.in_degree(aid, weight="weight")
        bet = cum_bet.get(aid, 0.0)
        
        if bet > 0.3 or (out_d > mean_out * 1.3 and in_d > mean_in * 1.3 and (out_d + in_d) > 0):
            role = "Hub_Coordinator"
        elif out_d > in_d * 1.5 and out_d > 0:
            role = "Broadcaster_Disseminator"
        elif in_d > out_d * 1.5 and in_d > 0:
            role = "Aggregator_Collector"
        elif out_d == 0 and in_d == 0:
            role = "Isolated"
        else:
            role = "Peer_Collaborator"
        agent_roles[aid] = role
        
    drift_values = [s.jaccard_distance_from_prev for s in snapshots[1:]] if len(snapshots) > 1 else [0.0]
    mean_drift = float(np.mean(drift_values)) if drift_values else 0.0
    
    deg_probs = [float(d) for d in all_out_degrees]
    net_entropy = calculate_entropy(deg_probs)
    
    undir_cum = cumulative_graph.to_undirected()
    is_conn = nx.is_connected(undir_cum) if len(undir_cum.nodes()) > 0 else False
    diameter = nx.diameter(undir_cum) if is_conn and len(undir_cum.nodes()) > 1 else None
    
    profile = OrganizationalProfile(
        case_id=case_id,
        task_id=task_id,
        protocol=protocol,
        num_agents=num_agents,
        total_rounds=current_round,
        snapshots=snapshots,
        gini_out_degree=gini_out,
        gini_in_degree=gini_in,
        gini_tool_usage=gini_tools,
        agent_roles=agent_roles,
        mean_structural_drift=mean_drift,
        final_network_entropy=net_entropy,
        network_diameter=diameter,
        is_connected=is_conn,
    )
    
    results_file = case_path / "results.json"
    if results_file.exists():
        try:
            with open(results_file, "r", encoding="utf-8") as rf:
                res = json.load(rf)
            profile.success = res.get("success", False)
            metrics = res.get("metrics", {})
            profile.success_rate = metrics.get("S_success_rate", 0.0)
            profile.partial_correctness = metrics.get("P_partial_correctness", 0.0)
            profile.token_consumption = metrics.get("C_token_consumption", 0.0)
            profile.communication_density = metrics.get("D_communication_density", 0.0)
        except Exception:
            pass
            
    return profile


def save_orchestra_instrumentation(profile: OrganizationalProfile, output_path: str | Path) -> None:
    """Save organizational profile as structured JSON for downstream analysis."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(asdict(profile), f, indent=2)
