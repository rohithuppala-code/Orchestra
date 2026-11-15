# ORCHESTRA: Research Framework for Emergent Organizational Evolution

[![Tests](https://img.shields.io/badge/pytest-30%20passed-brightgreen)](#-running-validation-tests)
[![Branch](https://img.shields.io/badge/Branch-urop__exec%20(300%20Runs%20Complete)-blue)](#-current-project-status)
[![Empirical Evidence](https://img.shields.io/badge/Empirical%20Runs-300%20Complete%20(N=2%2C%205)-brightgreen)](#-current-project-status)
[![Benchmark](https://img.shields.io/badge/Benchmark-SILO--BENCH-orange)](https://github.com/jwyjohn/acl26-silo-bench)
[![Target](https://img.shields.io/badge/Target-Q1%20Journal%20Publication-purple)](#)

ORCHESTRA is a scalable, research-grade framework designed to study emergent organizational evolution, behavioral specialization, communication topology dynamics, resilience under perturbations, and human-in-the-loop oversight in autonomous AI-agent societies.

The experimental execution engine and role-free coordination tasks are grounded in **SILO-BENCH** (`silo-bench/`), while the longitudinal network instrumentation, dynamic perturbation hooks, HITL supervision, comparative statistical analytics, and literature baseline topologies are implemented in `orchestra/` and `baselines/`.

---

## 📊 Current Project Status (`urop_exec` Execution Branch)

- **Architecture Status:** 100% Complete & Verified ✅
- **Automated Tests:** **30 passed, 0 failed** (`pytest tests -v`)
- **Streamlined Experimental Protocol:** **300 completed empirical runs** across agent scales $N \in \{2, 5\}$ (with $N=10$ specified as future scaling expansion) across **15 stratified tasks** (5 easy/medium/hard tasks per complexity level):
  - **Level I (5):** `I-01` (Global Max), `I-04` (Any Match), `I-07` (Average Value), `I-09` (Top-K Select), `I-10` (Standard Deviation)
  - **Level II (5):** `II-11` (Prefix Sum), `II-14` (1D Life Game), `II-15` (Pattern Search), `II-17` (Diff Array), `II-20` (Pipeline Hash)
  - **Level III (5):** `III-21` (Distributed Sort), `III-23` (Graph Components), `III-25` (K-Means Iteration), `III-28` (PageRank Step), `III-30` (Matrix Multiply)
- **Run Matrix Breakdown (300 Completed Empirical Runs):**
  1. **ORCHESTRA + Broadcast Suite (`run_master_benchmark.ps1` — 120 completed runs):** 15 stratified tasks × 2 protocols (`msg`, `broadcast`) × 2 perturbation conditions (`none`, `agent_dropout`) × 2 scales ($N=2, 5$) with real-time HITL boundary supervision. *(Note: `sfs` is omitted as unused in baseline comparison.)*
  2. **Non-Redundant Multi-Agent Baselines Suite (`run_baselines_benchmark.ps1` — 180 completed runs):** 15 stratified tasks × 3 distinct baseline topologies (`independent`, `central_coordinator`, `hierarchical_coordinator`) × 2 perturbation conditions × 2 scales ($N=2, 5$). *(`broadcast` is automatically sourced from ORCHESTRA's `broadcast` runs without duplication, and `fixed_roles` is excluded as structurally redundant with `central_coordinator`'s Star graph.)*
- **Paper Artifact Pipeline:** Fully automated synthesis combining all **300 executed runs** across **5 distinct paradigms** into publication-ready Markdown/CSV tables (Tables 1–4) and 300 DPI figures (Figures 1–3) in `paper_results/baselines/`. See [`claude-review.md`](file:///c:/Users/sairo/OneDrive/Documents/UROP/claude-review.md) and [`TABLES-sample.md`](file:///c:/Users/sairo/OneDrive/Documents/UROP/TABLES-sample.md).

*(Note: The original full 1,440-run / 30-task matrix remains preserved untouched on the `main` branch.)*

---

## 🏛️ Grounded Literature Baselines & ORCHESTRA (5 Distinct Paradigms)

| Method | Literature Citation | Paradigm / Topology | Enforcement / Source |
|---|---|---|---|
| **1. Independent Agents** | Wang et al. (*ICLR 2023*) | No Communication / Ensemble | Zero peer messaging; prompt conditioning + total message drop |
| **2. Flat Broadcast Debate** | Qian et al. (*ChatDev, ACL 2024*); Du et al. (*ICML 2023*) | Full Mesh / All-to-All Broadcast | Executed via `protocol="broadcast"` in master suite (zero duplicate runs) |
| **3. Central Coordinator** | Wu et al. (*AutoGen, ICLR 2024*) | Star Hub-and-Spoke | Agent 0 designated as Hub; worker-to-worker messages blocked |
| **4. Hierarchical Coordinator** | Wang et al. (*MacNet, ICLR 2024 / Neural Networks 2025*) | Multi-Tier Tree / Chain of Command | Strict organizational tree hierarchy; cross-tier messages blocked |
| **ORCHESTRA (Ours)** | *This Work* | Emergent Dynamic Self-Organization | Zero predefined roles; unconstrained P2P messaging (`msg`) + HITL oversight |

---

## 🛠️ Quick Setup

### 1. Prerequisites
- **Python**: Supported versions `3.10`–`3.13` (tested on Python 3.13.5).
- **LLM Backend**: Works with local Ollama or any remote OpenAI-compatible 3rd-party API endpoint.

### 2. Environment Setup
```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Model Provider Configuration
```powershell
# For 3rd-party OpenAI-compatible APIs (e.g., Qwen 3.8 27B / DeepSeek):
$env:ORCHESTRA_API_BASE = "https://your-provider-endpoint/v1"
$env:ORCHESTRA_API_KEY  = "your-api-key"

# Or for local Ollama:
$env:ORCHESTRA_API_BASE = "http://localhost:11434/v1"
$env:ORCHESTRA_API_KEY  = "ollama"
```

---

## 🧪 Running Validation Tests

```bash
pytest tests -v
```
All **30 unit and integration tests** pass.

---

## 🚀 Master Experimental Benchmark Execution (300 Runs Complete, N=10 Future Expansion)

### 1. ORCHESTRA + Broadcast Suite (120 Completed Runs)
Executes the 15 stratified tasks across agent scales $N \in \{2, 5\}$, 2 protocols (`msg`, `broadcast`), and 2 perturbation states (`none`, `agent_dropout`) with real-time HITL oversight:

```powershell
.\run_master_benchmark.ps1 -Model "your-model-id"
```

Outputs segregated by scale:
- `final_workspace_n2/` (60 runs complete + longitudinal plots + Pearson correlation matrix)
- `final_workspace_n5/` (60 runs complete + longitudinal plots + Pearson correlation matrix)
- *(Optional future expansion: `final_workspace_n10/` for scale $N=10$)*

### 2. Non-Redundant Multi-Agent Baselines & Paper Synthesis (180 Completed Runs -> 300 Combined)
Executes the 3 distinct external baselines (`independent`, `central_coordinator`, `hierarchical_coordinator`) across the 15 stratified tasks and scales $N \in \{2, 5\}$, then **automatically combines all 300 runs to synthesize paper tables and figures**:

```powershell
.\run_baselines_benchmark.ps1 -Model "your-model-id"
```

Outputs segregated by scale:
- `workspace_baselines_n2/` (90 runs complete)
- `workspace_baselines_n5/` (90 runs complete)
- *(Optional future expansion: `workspace_baselines_n10/` for scale $N=10$)*

### 3. Publication Paper Artifacts Generated (`paper_results/baselines/`)
- **Table 1 (Master Comparison):** `table1_master_baseline_comparison.md` & `.csv` (5 rows: 4 baselines + ORCHESTRA)
- **Table 2 (Scale Breakdown):** `table2_metrics_by_agent_scale.md` & `.csv` (Detailed metrics across $N=2$ and $N=5$)
- **Table 3 (Complexity Tiers):** `table3_task_complexity_breakdown.md` & `.csv` (15 rows across Levels I, II, III)
- **Table 4 (Fault Tolerance):** `table4_perturbation_resilience_breakdown.md` & `.csv` (Healthy vs. Dropout degradation)
- **Figure 1 (Accuracy Bar Chart):** `figure_baseline_accuracy_comparison.png`
- **Figure 2 (Dropout Resilience):** `figure_perturbation_resilience.png`
- **Figure 3 (Pareto Frontier):** `figure_token_accuracy_pareto.png`
- **Master Dataset:** `master_baseline_results.csv` (All 300 runs unified)

---

## 📁 Project Coordination Documents

- `claude-review.md`: Full academic conference reviewer evaluation, empirical validation, Pareto analysis, and topological emergence metrics.
- `TABLES-sample.md`: Complete blueprint of Tables 1–4, Figures 1–3, and empirical schema.
- `PROGRESS.md`: Ongoing status log of verified implementation status, test outcomes, and branch milestones.
- `papers.txt`: Literature grounding & taxonomy of related multi-agent systems and baselines.
- `to_sir.txt`: Professor-facing project & experimental matrix briefing.
- `context.txt` & `master_prompt.txt`: Enduring research design and milestone directives.
