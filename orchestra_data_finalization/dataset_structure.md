# SILO-BENCH Dataset Structure Reference

> For ORCHESTRA research use. All information verified against actual repository files.
> Repository: `silo-bench/` (v1.0.0)

---

## 1. Repository Layout

```
silo-bench/
├── benchmarks/                    # 180 task JSON files + 2 aggregated files + 1 zip
│   ├── I-01_n2.json ... I-10_n100.json       # Level I (Aggregation): 10 tasks × 6 scales
│   ├── II-11_n2.json ... II-20_n100.json     # Level II (Mesh Network): 10 tasks × 6 scales
│   ├── III-21_n2.json ... III-30_n100.json   # Level III (Global Shuffle): 10 tasks × 6 scales
│   ├── benchmark_summary.json                 # Index of all 30 tasks
│   └── silo_bench_full.json                   # All benchmarks in one file (~93 MB)
├── benchmark_generator/           # Scripts that generated the benchmark files
│   ├── main.py                    # Generator entry point
│   ├── paradigm_i.py              # Level I task generators
│   ├── paradigm_ii.py             # Level II task generators
│   └── paradigm_iii.py            # Level III task generators
├── src/                           # Execution framework
│   ├── engine.py                  # Core loop: init_case(), run_round(), evaluate()
│   ├── models.py                  # Pydantic models for all data structures
│   ├── batch_run.py               # CLI batch runner
│   ├── analyze.py                 # Result analysis tool
│   ├── msg/tools.py               # P2P protocol implementation
│   ├── broadcast/tools.py         # Broadcast protocol implementation
│   ├── sfs/tools.py               # Shared File System protocol implementation
│   └── utils/
│       ├── prompts.py             # System prompt templates (protocol-specific)
│       ├── metrics.py             # S, P, C, D metric computation
│       ├── parsing.py             # XML tool call parser
│       ├── persistence.py         # JSON/JSONL I/O
│       ├── config.py              # YAML config loader
│       └── llm.py                 # OpenAI-compatible API wrapper
├── configs/
│   └── config.example.yaml        # API credential template
├── pyproject.toml                 # Dependencies: openai, pydantic, pyyaml, srsly, tenacity
└── run.sh                         # Batch execution helper script
```

---

## 2. File Naming Convention

```
{Level}-{TaskNumber}_n{AgentCount}.json
```

| Component | Values | Example |
|---|---|---|
| Level | `I`, `II`, `III` | `III` |
| TaskNumber | `01`–`30` | `25` |
| AgentCount | `2`, `5`, `10`, `20`, `50`, `100` | `10` |
| Full filename | — | `III-25_n10.json` |

---

## 3. Benchmark JSON Schema

Every benchmark file (`{Level}-{Task}_n{N}.json`) contains exactly these top-level keys:

```json
{
  "case_id": "I-01",                          // string: unique task identifier
  "case_name": "Global Max",                  // string: human-readable name
  "paradigm": "Paradigm I",                   // string: "Paradigm I"|"Paradigm II"|"Paradigm III"
  "leetcode": { ... },                        // object: source problem reference
  "metadata": { ... },                        // object: task configuration (see §3.1)
  "task_description": "...",                  // string: template with {agent_id}, {input_shard}, {max_id}
  "agent_configs": [ ... ],                   // array: per-agent configuration (see §3.2)
  "expected_output": { ... },                 // object: global expected output (see §3.3)
  "evaluation_metrics": { ... }               // object: metric definitions (see §3.4)
}
```

### 3.1 `metadata` Object

```json
{
  "num_agents": 10,
  "optimal_topology": "Star (all agents → leader) or Tree, then broadcast result",
  "optimal_message_count": "9 messages to collect + 9 to broadcast = 18 total",
  "theoretical_complexity": "O(N) - MapReduce/Aggregation",
  "output_type": "distributed",
  "is_segmented": false
}
```

| Field | Type | Description |
|---|---|---|
| `num_agents` | int | Number of agents in this configuration |
| `optimal_topology` | string | Theoretically optimal communication structure |
| `optimal_message_count` | string | Minimum messages needed (descriptive) |
| `theoretical_complexity` | string | Computational/communication complexity class |
| `output_type` | string | Always `"distributed"` — each agent submits |
| `is_segmented` | bool | `true` = each agent submits its own output segment; `false` = all submit same answer |

### 3.2 `agent_configs` Array

Each element:

```json
{
  "agent_id": 0,                              // int: 0-indexed agent identifier
  "system_prompt": "[PLACEHOLDER] ...",       // string: overridden at runtime
  "user_prompt": "**Task: Global Max**...",   // string: instantiated task prompt with actual data
  "input_shard": [309, -772, ...],            // array|any: this agent's private data partition
  "expected_output": 827                       // any: ground truth for this agent
}
```

**Critical note:** `system_prompt` is a placeholder. The actual system prompt is generated at runtime by [`prompts.py`](file:///c:/Users/sairo/OneDrive/Documents/UROP/silo-bench/src/utils/prompts.py) `generate_system_prompt(protocol, agent_id, num_agents)` based on the chosen communication protocol.

### 3.3 `expected_output` Object

```json
{
  "type": "distributed",
  "per_agent_values": [827, 827],             // array: expected answer per agent
  "is_segmented": false,
  "verification_logic": "len(agent_outputs) == num_agents and all(...)",
  "verification_logic_hint": "all(submitted_values) == max(global_data)",
  "format_description": "ALL agents must submit..."
}
```

For **non-segmented** tasks: all entries in `per_agent_values` are identical.
For **segmented** tasks: each entry is a different segment (e.g., a sorted sub-array).

### 3.4 `evaluation_metrics` Object

```json
{
  "success_rate": "Percentage of agents that submitted correct answers over K trials",
  "round_to_completion": "Number of communication rounds needed",
  "communication_redundancy_ratio": "M_total / M_opt",
  "topological_fidelity": "Jaccard(E_empirical, E_optimal)"
}
```

**Note:** These are **descriptive definitions**, not computed values. Actual metric computation is in [`metrics.py`](file:///c:/Users/sairo/OneDrive/Documents/UROP/silo-bench/src/utils/metrics.py).

### 3.5 `leetcode` Object

```json
{
  "url": "https://leetcode.com/problems/third-maximum-number/",
  "description": "This case is inspired by the LeetCode problem..."
}
```

---

## 4. Input Data Types by Task

| Task | `input_shard` Type | Example |
|---|---|---|
| I-01 (Global Max) | `int[]` | `[309, -772, 518, ...]` |
| I-02 (Word Frequency) | `string[]` | `["apple", "banana", ...]` |
| I-03 (Distributed Vote) | `string[]` | `["Alice", "Bob", ...]` |
| I-04 (Any Match) | `string[]` | `["INFO: ok", "ERROR: fail", ...]` |
| I-05 (Range Count) | `int[]` | `[14, 87, 23, ...]` |
| I-06 (Checksum) | `int[]` | `[42, 17, 88, ...]` |
| I-07 (Average Value) | `int[]` | `[309, -772, ...]` |
| I-08 (Set Union Size) | `int[]` | `[1, 5, 3, 5, ...]` |
| I-09 (Top-K Select) | `int[]` | `[309, -772, ...]` |
| I-10 (Standard Deviation) | `int[]` | `[42, 17, ...]` |
| II-11 (Prefix Sum) | `int[]` | `[43, 22, 40, ...]` |
| II-12 (Moving Average) | `int[]`/`float[]` | `[10, 20, 30, ...]` |
| III-21 (Distributed Sort) | `int[]` | `[942, 873, ...]` |
| III-25 (K-Means) | `float[][]` (2D points) | `[[20.1, 78.6], ...]` |
| III-28 (PageRank) | `dict[]` (graph edges) | `[{"node": 0, "edges": [1,2]}, ...]` |

---

## 5. Task Inventory

### Level I — Aggregation (Tasks I-01 through I-10)

| ID | Name | Optimal Topology | Segmented | Complexity |
|---|---|---|---|---|
| I-01 | Global Max | Star/Tree → broadcast | No | O(N) |
| I-02 | Word Frequency | Star → broadcast | No | O(N) |
| I-03 | Distributed Vote | Star/Tree → broadcast | No | O(N) |
| I-04 | Any Match | Star with early termination | No | O(N) |
| I-05 | Range Count | Star → broadcast | No | O(N) |
| I-06 | Checksum | Star → broadcast | No | O(N) |
| I-07 | Average Value | Star (sum, count) → broadcast | No | O(N) |
| I-08 | Set Union Size | Star/hash → broadcast | No | O(N) |
| I-09 | Top-K Select | Star (local top-K) → broadcast | No | O(N) |
| I-10 | Standard Deviation | Star two-phase → broadcast | No | O(N) |

### Level II — Mesh Network (Tasks II-11 through II-20)

| ID | Name | Optimal Topology | Segmented | Complexity |
|---|---|---|---|---|
| II-11 | Prefix Sum | Chain (0→1→...→N-1) | Yes | O(N) |
| II-12 | Moving Average | Chain bidirectional | No | O(N) |
| II-13 | Longest Palindrome | Chain prefix/suffix exchange | No | O(N) |
| II-14 | 1D Life Game | Chain repeated boundary | Yes | O(N) |
| II-15 | Pattern Search | Chain state passing | No | O(N) |
| II-16 | Trapping Rain | Chain bidirectional | No | O(N) |
| II-17 | Diff Array | Chain (each → next) | No | O(N) |
| II-18 | List Ranking | Chain/pointer-jumping | No | O(N) |
| II-19 | Merge Neighbors | Chain boundary comparison | No | O(N) |
| II-20 | Pipeline Hash | Chain strict sequential | Yes | O(N) |

### Level III — Global Shuffle (Tasks III-21 through III-30)

| ID | Name | Optimal Topology | Segmented | Complexity |
|---|---|---|---|---|
| III-21 | Distributed Sort | All-to-all / partitioning | Yes | O(N log N)–O(N²) |
| III-22 | Median of Medians | Iterative broadcast | No | O(N log N)–O(N²) |
| III-23 | Graph Components | Hash/all-to-all | No | O(N log N)–O(N²) |
| III-24 | BFS Distance | Dynamic routing | No | O(N log N)–O(N²) |
| III-25 | K-Means Iteration | Shuffle by cluster / all-to-all | No | O(N log N)–O(N²) |
| III-26 | Global Distinct | Hash-based shuffle | No | O(N log N)–O(N²) |
| III-27 | Collaborative Filtering | Broadcast / hash partition | No | O(N log N)–O(N²) |
| III-28 | PageRank Step | Node-based partition | No | O(N log N)–O(N²) |
| III-29 | Load Balance | All-to-all + coordinator | No | O(N log N)–O(N²) |
| III-30 | Matrix Multiply | All-to-all | No | O(N log N)–O(N²) |

---

## 6. Communication Protocols

| Protocol | CLI flag | Tools available | Message visibility |
|---|---|---|---|
| P2P | `msg` | `send_message(target_id, content)`, `receive_messages()`, `wait()`, `submit_result(answer)` | Directed: only recipient sees it |
| Broadcast | `broadcast` | `broadcast_message(content)`, `receive_messages()`, `list_agents()`, `wait()`, `submit_result(answer)` | All agents see it |
| Shared File System | `sfs` | `write_file(path, content)`, `read_file(path)`, `list_files(prefix)`, `delete_file(path)`, `wait()`, `submit_result(answer)` | All agents can read |

All protocols use **round-based synchronization**: writes in round *t* become readable in round *t+1*.

---

## 7. Execution Output Structure

When experiments are run, the framework creates this structure per case:

```
workspace/{case_id}_{protocol}_{model}_{timestamp}/
├── metadata.json                  # CaseMetadata: task info, config, execution state
├── results.json                   # Evaluation results: submissions, metrics (S, P, C, D)
├── logs/
│   ├── agent-000.jsonl            # Per-agent event log (every tool call, LLM response)
│   ├── agent-001.jsonl
│   └── ...
└── rounds/
    ├── round-000000/
    │   ├── agent-000/
    │   │   ├── context.json       # Full conversation history (system + user + assistant)
    │   │   ├── state.json         # AgentState: submitted, messages_sent/received, etc.
    │   │   └── submission.json    # If agent submitted this round
    │   ├── agent-001/
    │   │   └── ...
    │   └── env/
    │       ├── messages/          # P2P: individual message JSONs
    │       ├── broadcasts/        # Broadcast: broadcast message JSONs
    │       └── shared_kv.json     # SFS: key-value store snapshot
    ├── round-000001/
    │   └── ...
    └── ...
```

**This structure does not exist in the downloaded repository.** It is created only by running experiments.

---

## 8. Implemented Evaluation Metrics

From [`src/utils/metrics.py`](file:///c:/Users/sairo/OneDrive/Documents/UROP/silo-bench/src/utils/metrics.py):

| Metric | Symbol | Formula | Implementation |
|---|---|---|---|
| Success Rate | S | `(1/N) × Σ 𝟙[ŷᵢ = y*]` | `compute_success_rate()` L45-78 |
| Partial Correctness | P | `(1/N) × Σ qᵢ` (per-level scoring) | `compute_partial_correctness()` L96-211 |
| Token Consumption | C | `Σᵢ Σᵣ tᵢᵒᵘᵗ[r] / R_max` | `compute_token_consumption()` L214-229 |
| Communication Density | D | `Σᵢ mᵢ / N(N-1)` | `compute_communication_density()` L238-263 |

---

## 9. Pydantic Data Models

From [`src/models.py`](file:///c:/Users/sairo/OneDrive/Documents/UROP/silo-bench/src/models.py):

| Model | Key Fields | Purpose |
|---|---|---|
| `AgentState` | `agent_id`, `submitted`, `submission_round`, `messages_sent`, `messages_received`, `files_written`, `files_read` | Per-agent tracking during execution |
| `LogEvent` | `round`, `event`, `agent_id`, `timestamp`, `input_tokens`, `output_tokens`, `response`, `tool`, `parameters`, `result`, `answer` | Per-agent event logging |
| `P2PMessage` | `sender_id`, `recipient_id`, `content`, `timestamp`, `read` | P2P message record |
| `BroadcastMessage` | `sender_id`, `content`, `timestamp`, `broadcast_id` | Broadcast message record |
| `SharedFileEntry` | `content`, `modified_by`, `modified_at_round` | SFS file record |
| `Submission` | `agent_id`, `answer`, `round` | Agent's final answer |
| `Metrics` | `success_rate`, `token_efficiency`, `communication_density` | Computed metrics |
| `ToolCall` | `tool`, `parameters` | Parsed LLM tool invocation |
| `ToolResult` | `tool`, `parameters`, `result`, `success`, `error` | Tool execution result |
