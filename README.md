# ORCHESTRA: Research Framework for Emergent Organizational Evolution

ORCHESTRA is a scalable, research-grade framework designed to study emergent organizational evolution, behavioral specialization, communication topology dynamics, resilience under perturbations, and human-in-the-loop oversight in autonomous AI-agent societies.

The experimental execution engine and role-free coordination tasks are grounded in **SILO-BENCH** (`silo-bench/`), while the longitudinal network instrumentation, dynamic perturbation hooks, HITL supervision, and comparative statistical analytics are implemented in `orchestra/`.

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
    ollama pull gemma4:e2b
    # or
    ollama pull qwen3.5:0.8b
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
   export ORCHESTRA_MODEL="gemma4:e2b"
   export ORCHESTRA_API_BASE="http://localhost:11434/v1"
   export ORCHESTRA_API_KEY="ollama"
   ```
3. Configuration file fallback (`silo-bench/configs/config.yaml` or `configs/config.yaml`). Copy template:
   ```bash
   cp silo-bench/configs/config.example.yaml silo-bench/configs/config.yaml
   ```

---

## 🧪 Running Validation Tests

Run the complete automated test suite verifying configuration resolution, population scaling, graph metrics, perturbations, HITL oversight, and runner integration:

```bash
pytest tests -v
```

All 21 unit and integration tests should pass.

---

## 🚀 Running an Experiment

### Single Pilot Run
Run an end-to-end experiment with configurable agent count ($N \in \{2, 5, 10, 20, 50, 100\}$), communication protocol (`msg`, `broadcast`, `sfs`), and optional perturbation or HITL monitoring:

```bash
# 2-Agent P2P baseline on task I-01
python -m orchestra.runner --task-id I-01 --agent-count 2 --protocol msg --max-rounds 10

# 5-Agent Broadcast run with fail-stop Agent Dropout perturbation at Round 2
python -m orchestra.runner --task-id I-01 --agent-count 5 --protocol broadcast --perturbation agent_dropout --drop-round 2 --drop-agent 1

# 5-Agent Broadcast run with Human-in-the-Loop oversight monitoring
python -m orchestra.runner --task-id I-01 --agent-count 5 --protocol broadcast --hitl --hitl-mode audit_only
```

### Automated Batch Matrix Runner
Execute a multi-condition experimental matrix across tasks, agent counts, protocols, and seed repetitions:

```bash
# Run a matrix across 2 and 5 agents, P2P and Broadcast, with 3 seed repetitions
python -m orchestra.batch_runner --task-ids I-01 --agent-counts 2 5 --protocols msg broadcast --repetitions 3 --workspace workspace
```

Each run automatically generates in the case directory:
- `orchestra_profile.json`: Full round-by-round instantaneous and cumulative graph snapshots, Gini coefficients, structural drift, and role classifications.
- `orchestra_summary.json`: Top-level experiment summary with task metrics, organizational metrics, and perturbation/HITL audit results.
- `hitl_interventions.jsonl` (if HITL enabled): Trace of boundary violations (monopolization, isolation, stagnation).

### Comparative Analysis & Publication Figures
Aggregate profiles across experimental runs in a workspace to produce statistical tables, structure-performance correlations, and figures:

```bash
python -m orchestra.analysis --workspace silo-bench/workspace --output-dir orchestra/figures
```

Outputs:
- Markdown summary comparison table
- `comparison_results.csv`
- Longitudinal network density & structural drift plots (`longitudinal_comparison.png`)

---

## 📁 Project Coordination Documents

Per project guidelines, team coordination is maintained strictly through:
- `context.txt`: Enduring research questions, design decisions, and scientific boundaries.
- `master_prompt.txt`: Implementation milestones and research execution directives.
- `PROGRESS.md`: Living status log of verified implementation status, test outcomes, and experimental validation.
