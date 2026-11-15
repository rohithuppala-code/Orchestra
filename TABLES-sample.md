# ORCHESTRA: Research Paper Tables & Figures Blueprint (`urop_exec` Empirical Matrix)

**Document Purpose:** Complete specification of all tables, figures, and datasets automatically generated for the Q1 journal paper submission from the executed **300-run empirical matrix** ($N=2$ and $N=5$, with $N=10$ defined as future scaling expansion) on branch `urop_exec`.

---

## 🎯 **Experimental Scope Summary (300 Completed Runs)**

* **Selected Stratified Tasks (15 Total — 5 Evenly Spread Across Difficulty & Type per Level):**
  * **Level I (Cross-Silo Aggregation):** `I-01` (Global Max), `I-04` (Any Match), `I-07` (Average Value), `I-09` (Top-K Select), `I-10` (Standard Deviation)
  * **Level II (Spatial Mesh & Neighborhood Routing):** `II-11` (Prefix Sum), `II-14` (1D Life Game), `II-15` (Pattern Search), `II-17` (Diff Array), `II-20` (Pipeline Hash)
  * **Level III (Global Shuffle & Distributed Joins):** `III-21` (Distributed Sort), `III-23` (Graph Components), `III-25` (K-Means Iteration), `III-28` (PageRank Step), `III-30` (Matrix Multiply)
* **Scales:** $N \in \{2, 5\}$ Agents (with $N=10$ planned as future expansion)
* **Conditions:** Healthy (`none`) vs. Fail-Stop Agent Crash (`agent_dropout` at Round 2)
* **Run Breakdown (Zero Redundancy):**
  * **Baselines (`run_baselines_benchmark.ps1`):** `3 baselines` (`independent`, `central_coordinator`, `hierarchical_coordinator`) × `15 tasks` × `2 cases` = **90 runs/scale** × `2 scales` = **180 completed runs**
  * **ORCHESTRA (`run_master_benchmark.ps1`):** `15 tasks` × `2 protocols` (`msg` = ORCHESTRA, `broadcast` = Flat Broadcast Debate baseline) × `2 cases` = **60 runs/scale** × `2 scales` = **120 completed runs**
  * **Grand Total:** `180 + 120` = **300 completed runs** (comparing **5 distinct coordination paradigms**)

> *Design Rationale:* Duplicate `broadcast` execution is eliminated by sourcing `Flat Broadcast Debate` directly from ORCHESTRA's `protocol="broadcast"` runs; `sfs` is omitted as it is unused in baseline comparisons; and `fixed_roles` is omitted as it enforces the exact same Star Hub communication graph around Agent 0 as `central_coordinator`.

---

## 📊 **TABLE 1: Master Empirical Multi-Agent Baseline Comparison**

**Location:** `paper_results/baselines/table1_master_baseline_comparison.csv` and `.md`

**Purpose:** Primary head-to-head comparison table showing all **5 distinct coordination paradigms** (4 literature baselines + ORCHESTRA) across accuracy, token cost, convergence speed, hierarchy emergence, and fault tolerance.

### Structure:

| Baseline | Paradigm | Citation | Success_N2 | Success_N5 | Success_N10 | Success_Overall | Tokens_Mean | Rounds_Mean | Gini_OutDegree | Dropout_Success | Resilience_Delta |
|----------|----------|----------|------------|------------|-------------|-----------------|-------------|-------------|----------------|-----------------|------------------|
| Independent Agents | No Communication | Wang et al. (ICLR 2023) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| Flat Broadcast Debate | Complete Mesh | Qian et al. (ACL 2024); Du et al. (2023) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| Central Coordinator | Star Hub | Wu et al. (AutoGen / ICLR 2024) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| Hierarchical Tree | Static Tree | Wang et al. (MacNet, 2024/2025) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| **ORCHESTRA (Ours)** | **Emergent Dynamic** | **This Work** | **XX.X%** | **XX.X%** | **XX.X%** | **XX.X%** | **X,XXX** | **X.X** | **X.XXX** | **XX.X%** | **±X.X%** |

**Column Definitions:**
- **Baseline:** Method display name
- **Paradigm:** Coordination topology class
- **Citation:** Literature reference
- **Success_N2/N5/N10:** Mean healthy task success rate at each agent scale ($N=2, 5, 10$)
- **Success_Overall:** Mean healthy task success rate across all 45 runs per method
- **Tokens_Mean:** Average token consumption per round (`C` metric)
- **Rounds_Mean:** Average rounds to convergence
- **Gini_OutDegree:** Gini coefficient of out-degree distribution (0=egalitarian, 1=monopolized)
- **Dropout_Success:** Mean task success rate under agent dropout perturbation
- **Resilience_Delta:** Accuracy change from healthy to dropout condition (Dropout - Healthy)

**Total Rows:** **5** (4 distinct literature topologies + ORCHESTRA)

---

## 📊 **TABLE 2: Detailed Evaluation Metrics Across Agent Scales ($N=2, 5, 10$)**

**Location:** `paper_results/baselines/table2_metrics_by_agent_scale.csv` and `.md`

**Purpose:** Break down healthy-condition performance by agent population scale ($N=2, 5, 10$) for each method.

### Structure:

| Baseline | Scale_N | Runs | Success_Rate | Partial_Correctness | Avg_Tokens | Avg_Rounds | Gini_Hierarchy | Comm_Density | Avg_Latency_s |
|----------|---------|------|--------------|---------------------|------------|------------|----------------|--------------|---------------|
| Independent Agents | 2 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Independent Agents | 5 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Independent Agents | 10 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Flat Broadcast Debate | 2 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Flat Broadcast Debate | 5 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Flat Broadcast Debate | 10 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Central Coordinator | 2 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Central Coordinator | 5 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Central Coordinator | 10 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Hierarchical Tree | 2 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Hierarchical Tree | 5 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Hierarchical Tree | 10 | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| **ORCHESTRA (Ours)** | **2** | **15** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** | **X.XXX** | **XXX.X** |
| **ORCHESTRA (Ours)** | **5** | **15** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** | **X.XXX** | **XXX.X** |
| **ORCHESTRA (Ours)** | **10** | **15** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** | **X.XXX** | **XXX.X** |

**Column Definitions:**
- **Scale_N:** Number of agents (2, 5, or 10)
- **Runs:** Healthy runs per scale per method (15 stratified tasks)
- **Success_Rate:** Task success percentage ($S$)
- **Partial_Correctness:** Continuous partial solution score ($P$)
- **Avg_Tokens:** Mean token consumption ($C$)
- **Avg_Rounds:** Mean rounds to convergence
- **Gini_Hierarchy:** Gini coefficient of communication out-degree
- **Comm_Density:** Communication network density ($D \in [0, 1]$)
- **Avg_Latency_s:** Mean wall-clock time per task

**Total Rows:** **15** (5 methods × 3 scales)

---

## 📊 **TABLE 3: Performance Breakdown by Algorithmic Complexity Tier**

**Location:** `paper_results/baselines/table3_task_complexity_breakdown.csv` and `.md`

**Purpose:** Evaluate how each coordination paradigm performs across the 3 algorithmic complexity tiers (each represented by 5 stratified tasks across all 3 scales = 15 healthy runs per row).

### Structure:

| Baseline | Complexity_Tier | Runs | Success_Rate | Partial_Correctness | Avg_Tokens | Avg_Rounds | Gini_Hierarchy |
|----------|----------------|------|--------------|---------------------|------------|------------|----------------|
| Independent Agents | Level I (Aggregation) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Independent Agents | Level II (Mesh Routing) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Independent Agents | Level III (Global Shuffle) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Flat Broadcast Debate | Level I (Aggregation) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Flat Broadcast Debate | Level II (Mesh Routing) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Flat Broadcast Debate | Level III (Global Shuffle) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Central Coordinator | Level I (Aggregation) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Central Coordinator | Level II (Mesh Routing) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Central Coordinator | Level III (Global Shuffle) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Hierarchical Tree | Level I (Aggregation) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Hierarchical Tree | Level II (Mesh Routing) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Hierarchical Tree | Level III (Global Shuffle) | 15 | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| **ORCHESTRA (Ours)** | **Level I (Aggregation)** | **15** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** |
| **ORCHESTRA (Ours)** | **Level II (Mesh Routing)** | **15** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** |
| **ORCHESTRA (Ours)** | **Level III (Global Shuffle)** | **15** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** |

**Total Rows:** **15** (5 methods × 3 tiers)

---

## 📊 **TABLE 4: Fault Tolerance and Agent Dropout Degradation**

**Location:** `paper_results/baselines/table4_perturbation_resilience_breakdown.csv` and `.md`

**Purpose:** Measure organizational resilience when Agent 1 suffers a fail-stop crash at Round 2 (45 healthy runs vs. 45 dropout runs per method).

### Structure:

| Baseline | Healthy_Accuracy | Dropout_Accuracy | Accuracy_Delta | Healthy_Tokens | Dropout_Tokens | Token_Delta |
|----------|------------------|------------------|----------------|----------------|----------------|-------------|
| Independent Agents | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| Flat Broadcast Debate | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| Central Coordinator | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| Hierarchical Tree | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| **ORCHESTRA (Ours)** | **XX.X%** | **XX.X%** | **±X.X%** | **X,XXX** | **X,XXX** | **±X.X%** |

**Total Rows:** **5** (4 literature baselines + ORCHESTRA)

---

## 📈 **PUBLICATION FIGURES (300 DPI PNG)**

1. **Figure 1 (`paper_results/baselines/figure_baseline_accuracy_comparison.png`):** Grouped Bar Chart of task success across $N \in \{2, 5, 10\}$ for all 5 methods.
2. **Figure 2 (`paper_results/baselines/figure_perturbation_resilience.png`):** Side-by-Side Control (Healthy) vs. Agent Dropout degradation across all 5 methods.
3. **Figure 3 (`paper_results/baselines/figure_token_accuracy_pareto.png`):** Pareto Frontier scatter plot of Mean Token Consumption vs. Success Rate, with ORCHESTRA highlighted as a gold star ($\star$).

---

## 📊 **SUPPLEMENTARY DATA & SCALE WORKSPACES**

### **1. Master Baseline Results CSV (`paper_results/baselines/master_baseline_results.csv`)**
* **Total Rows:** **300** (120 ORCHESTRA/Broadcast + 180 Baselines)
* **Columns (18):** `case_id`, `baseline`, `task_id`, `num_agents`, `protocol`, `perturbation`, `total_rounds`, `success`, `success_rate`, `partial_correctness`, `token_consumption`, `communication_density`, `gini_out_degree`, `gini_in_degree`, `mean_structural_drift`, `model`, `seed`, `total_time_seconds`.

### **2. Scale-Segregated ORCHESTRA Workspaces (`final_workspace_n2/`, `final_workspace_n5/`)**
Each scale folder contains **60 runs** (15 stratified tasks × 2 protocols [`msg`, `broadcast`] × 2 perturbations):
* `batch_comparison_results.csv` (60 runs)
* `structure_performance_correlations.csv` (Pearson $r$ matrix correlating Gini, drift, density, betweenness with $S, P, C, D$)
* `longitudinal_comparison.png` (Round-by-round density evolution & Jaccard structural drift)
*(Note: `final_workspace_n10/` configured for future $N=10$ scaling)*

### **3. Scale-Segregated Baseline Workspaces (`workspace_baselines_n2/`, `workspace_baselines_n5/`)**
Each scale folder contains **90 runs** (15 stratified tasks × 3 non-redundant baselines × 2 perturbations) + `baseline_comparison_results.csv`.
*(Note: `workspace_baselines_n10/` configured for future $N=10$ scaling)*

---

## 🎯 **EXECUTION COMMANDS**

```powershell
# 1. ORCHESTRA + Broadcast (120 completed runs across N=2, 5)
.\run_master_benchmark.ps1 -Model "your-model"

# 2. Non-Redundant Baselines + Automatic Paper Synthesis (180 completed runs -> 300 combined)
.\run_baselines_benchmark.ps1 -Model "your-model"
```

**No manual table formatting or spreadsheet assembly required — all 4 tables, 3 figures, and the 300-row master dataset are automatically generated.**
