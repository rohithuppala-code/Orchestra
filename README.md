# ORCHESTRA: Research Framework for Emergent Organizational Evolution

[![Tests](https://img.shields.io/badge/pytest-29%20passed-brightgreen)](#-running-validation-tests)
[![Status](https://img.shields.io/badge/Status-Architecture%20%26%20Baselines%20Verified%20%E2%9C%85-blue)](#-current-project-status)
[![Benchmark](https://img.shields.io/badge/Benchmark-SILO--BENCH-orange)](https://github.com/jwyjohn/acl26-silo-bench)
[![Target](https://img.shields.io/badge/Target-Q1%20Journal%20Publication-purple)](#)

ORCHESTRA is a scalable, research-grade framework designed to study emergent organizational evolution, behavioral specialization, communication topology dynamics, resilience under perturbations, and human-in-the-loop oversight in autonomous AI-agent societies.

The experimental execution engine and role-free coordination tasks are grounded in **SILO-BENCH** (`silo-bench/`), while the longitudinal network instrumentation, dynamic perturbation hooks, HITL supervision, comparative statistical analytics, and the 5 literature baseline topologies are implemented in `orchestra/` and `baselines/`.

---

## 📊 Current Project Status

- **Architecture Status:** 100% Complete & Verified ✅
- **Automated Tests:** **29 passed, 0 failed** (`pytest tests -v`)
- **Experimental Protocol:** Finalized and frozen for **1,440 planned experimental runs** across agent scales $N \in \{2, 5, 10\}$:
  1. **ORCHESTRA Benchmark Suite (540 runs):** 30 tasks × 3 protocols (`msg`, `broadcast`, `sfs`) × 2 perturbation conditions (`none`, `agent_dropout`) with real-time HITL boundary supervision.
  2. **Multi-Agent Baselines Suite (900 runs):** 30 tasks × 5 foundational/SOTA literature baselines × 2 perturbation conditions (`none`, `agent_dropout`).
- **Paper Artifact Pipeline:** Fully automated synthesis generating publication-ready Markdown/CSV tables (Tables 1–4) and high-resolution figures (Figures 1–3).

---

## 🏛️ Grounded Literature Baselines

ORCHESTRA provides direct empirical comparisons against 5 state-of-the-art multi-agent coordination paradigms from published literature:

| Baseline | Literature Citation | Paradigm / Topology | Enforcement Mechanism |
|---|---|---|---|
| **1. Independent Agents** | Wang et al. (*ICLR 2023*) | No Communication / Self-Consistency Ensemble | Zero peer messaging; prompt conditioning + total message drop |
| **2. Flat Broadcast Debate** | Qian et al. (*ChatDev, ACL 2024*); Du et al. (*ICML 2023*) | Full Mesh / All-to-All Broadcast | Unconstrained broadcast protocol |
| **3. Central Coordinator** | Wu et al. (*AutoGen, ICLR 2024*) | Star Hub-and-Spoke | Agent 0 designated as Hub; worker-to-worker messages blocked |
| **4. Hierarchical Coordinator** | Wang et al. (*MacNet, ICLR 2024 / Neural Networks 2025*) | Multi-Tier Tree / Chain of Command | Strict organizational tree hierarchy; cross-tier messages blocked |
| **5. Fixed Predefined Roles** | Hong et al. (*MetaGPT, ICLR 2024 Oral*) | Prompt Hierarchy / SOP Roles | Static role prompt injection; worker-to-worker routing blocked |
| **ORCHESTRA (Ours)** | *This Work* | Emergent Dynamic Self-Organization | Zero predefined roles; unconstrained P2P messaging + HITL oversight |

---

## 🛠️ Quick Setup for Teammates

### 1. Prerequisites
- **Python**: Supported versions: `3.10`, `3.11`, `3.12`, `3.13` (tested on Python 3.13.5).
- **Ollama** (for local model integration validation):
  - Ollama is an external system application (not a pip package). Download and install from [ollama.com](https://ollama.com).
  - Verify Ollama daemon is running:
    ```bash
    curl http://localhost:11434/api/tags
    ```
  - Pull a lightweight model for integration testing:
    ```bash
    ollama pull qwen2.5:7b
    # or lightweight
    ollama pull gemma4:e2b
    ```

### 2. Environment Setup
Clone the repository and create an isolated Python virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install all direct dependencies
pip install -r requirements.txt
```

### 3. Model Configuration
ORCHESTRA supports both local Ollama inference and any remote OpenAI-compatible endpoint (e.g. OpenAI, vLLM, OpenRouter).

Precedence for model configuration:
1. CLI flags (`--model`, `--api-base`, `--api-key`)
2. Environment variables:
   ```bash
   export ORCHESTRA_MODEL="qwen2.5:7b"
   export ORCHESTRA_API_BASE="http://localhost:11434/v1"
   export ORCHESTRA_API_KEY="ollama"
   ```
3. Configuration file fallback (`silo-bench/configs/config.yaml` or `configs/config.yaml`). Copy template:
   ```bash
   cp silo-bench/configs/config.example.yaml silo-bench/configs/config.yaml
   ```

---

## 🧪 Running Validation Tests

Run the complete automated test suite verifying configuration resolution, population scaling, graph metrics, perturbations, HITL oversight, baseline topologies, and synthesis:

```bash
pytest tests -v
```

All **29 unit and integration tests** should pass.

---

## 🚀 Master Experimental Benchmark Execution

### 1. Full ORCHESTRA Benchmark (540 Runs)
Executes all 30 algorithmic tasks across scales $N \in \{2, 5, 10\}$, 3 protocols (`msg`, `broadcast`, `sfs`), and 2 perturbation states (`none`, `agent_dropout`) with real-time HITL oversight:

```powershell
.\run_master_benchmark.ps1 -Model "qwen2.5:7b"
```

Outputs segregated by scale:
- `final_workspace_n2/` (180 runs + longitudinal plots + Pearson correlation matrix)
- `final_workspace_n5/` (180 runs + longitudinal plots + Pearson correlation matrix)
- `final_workspace_n10/` (180 runs + longitudinal plots + Pearson correlation matrix)

### 2. Full Multi-Agent Baselines Benchmark & Paper Synthesis (900 Runs)
Executes all 5 literature baselines across all 30 tasks, scales $N \in \{2, 5, 10\}$, and perturbation conditions, then **automatically synthesizes the final paper tables and figures**:

```powershell
.\run_baselines_benchmark.ps1 -Model "qwen2.5:7b"
```

Outputs segregated by scale:
- `workspace_baselines_n2/` (300 runs)
- `workspace_baselines_n5/` (300 runs)
- `workspace_baselines_n10/` (300 runs)

### 3. Publication Paper Artifacts Generated (`paper_results/baselines/`)
The synthesis engine combines all 1,440 runs to produce publication-ready artifacts:
- **Table 1 (Master Comparison):** `table1_master_baseline_comparison.md` & `.csv` (Accuracy, Tokens, Rounds, Gini, Dropout Delta across all 6 methods).
- **Table 2 (Scale Breakdown):** `table2_metrics_by_agent_scale.md` & `.csv` (Detailed evaluation metrics across scales $N=2, 5, 10$).
- **Table 3 (Complexity Tiers):** `table3_task_complexity_breakdown.md` & `.csv` (Performance across Levels I, II, III).
- **Table 4 (Fault Tolerance):** `table4_perturbation_resilience_breakdown.md` & `.csv` (Healthy vs. Dropout degradation).
- **Figure 1 (Accuracy Bar Chart):** `figure_baseline_accuracy_comparison.png`
- **Figure 2 (Dropout Resilience):** `figure_perturbation_resilience.png`
- **Figure 3 (Pareto Frontier):** `figure_token_accuracy_pareto.png` (Accuracy vs. Token Cost with ORCHESTRA highlighted).
- **Master Dataset:** `master_baseline_results.csv` (Complete unified dataset of all experimental runs).

---

## 📁 Project Coordination Documents

Per project guidelines, team coordination is maintained strictly through:
- `context.txt`: Enduring research questions, design decisions, and scientific boundaries.
- `master_prompt.txt`: Implementation milestones and research execution directives.
- `PROGRESS.md`: Living status log of verified implementation status, test outcomes, and experimental validation.

