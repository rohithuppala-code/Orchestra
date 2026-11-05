# ORCHESTRA: Research Paper Tables & Figures Blueprint

**Document Purpose:** Complete specification of all tables and figures that will be automatically generated for the Q1 journal paper submission after completing the 1,440 experimental runs.

---

## 📊 **TABLE 1: Master Empirical Multi-Agent Baseline Comparison**

**Location:** `paper_results/baselines/table1_master_baseline_comparison.csv` and `.md`

**Purpose:** Primary comparison table showing all 6 methods (5 baselines + ORCHESTRA) across all performance metrics

### Structure:

| Baseline | Paradigm | Citation | Success_N2 | Success_N5 | Success_N10 | Success_Overall | Tokens_Mean | Rounds_Mean | Gini_OutDegree | Dropout_Success | Resilience_Delta |
|----------|----------|----------|------------|------------|-------------|-----------------|-------------|-------------|----------------|-----------------|------------------|
| Independent Agents | No Communication | Wang et al. (ICLR 2023) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| Flat Broadcast Debate | Complete Mesh | Qian et al. (ACL 2024); Du et al. (2023) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| Central Coordinator | Star Hub | Wu et al. (AutoGen / ICLR 2024) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| Hierarchical Tree | Static Tree | Wang et al. (MacNet, 2024/2025) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| Fixed Predefined Roles | Prompt Hierarchy | Hong et al. (MetaGPT, ICLR 2024) | XX.X% | XX.X% | XX.X% | XX.X% | X,XXX | X.X | X.XXX | XX.X% | ±X.X% |
| **ORCHESTRA (Ours)** | **Emergent Dynamic** | **This Work** | **XX.X%** | **XX.X%** | **XX.X%** | **XX.X%** | **X,XXX** | **X.X** | **X.XXX** | **XX.X%** | **±X.X%** |

**Column Definitions:**
- **Baseline:** Method name (display format)
- **Paradigm:** Coordination topology type
- **Citation:** Literature reference
- **Success_N2/N5/N10:** Task success rate at specific agent scales
- **Success_Overall:** Mean success rate across all scales and tasks
- **Tokens_Mean:** Average token consumption per task
- **Rounds_Mean:** Average rounds to convergence
- **Gini_OutDegree:** Gini coefficient of out-degree distribution (0=egalitarian, 1=monopolized)
- **Dropout_Success:** Task success rate under agent dropout perturbation
- **Resilience_Delta:** Accuracy change from healthy to dropout condition (negative = degradation, positive = improvement)

**Total Rows:** 6 (5 baselines + ORCHESTRA)

**Key Insights to Highlight:**
- ORCHESTRA's emergent hierarchy (Gini) vs. fixed hierarchies
- Token efficiency (lower is better)
- Resilience delta (smaller absolute value = more robust)
- Scale-wise performance trends

---

## 📊 **TABLE 2: Detailed Evaluation Metrics Across Agent Scales**

**Location:** `paper_results/baselines/table2_metrics_by_agent_scale.csv` and `.md`

**Purpose:** Break down performance by agent scale (N=2, 5, 10) for each baseline

### Structure:

| Baseline | Scale_N | Runs | Success_Rate | Partial_Correctness | Avg_Tokens | Avg_Rounds | Gini_Hierarchy | Comm_Density | Avg_Latency_s |
|----------|---------|------|--------------|---------------------|------------|------------|----------------|--------------|---------------|
| Independent Agents | 2 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Independent Agents | 5 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Independent Agents | 10 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Flat Broadcast Debate | 2 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Flat Broadcast Debate | 5 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Flat Broadcast Debate | 10 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Central Coordinator | 2 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Central Coordinator | 5 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Central Coordinator | 10 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Hierarchical Tree | 2 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Hierarchical Tree | 5 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Hierarchical Tree | 10 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Fixed Predefined Roles | 2 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Fixed Predefined Roles | 5 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| Fixed Predefined Roles | 10 | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX | X.XXX | XXX.X |
| **ORCHESTRA (Ours)** | **2** | **XX** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** | **X.XXX** | **XXX.X** |
| **ORCHESTRA (Ours)** | **5** | **XX** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** | **X.XXX** | **XXX.X** |
| **ORCHESTRA (Ours)** | **10** | **XX** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** | **X.XXX** | **XXX.X** |

**Column Definitions:**
- **Scale_N:** Number of agents (2, 5, or 10)
- **Runs:** Number of experimental runs at this scale (typically 90 runs per scale per baseline: 30 tasks × 3 protocols)
- **Success_Rate:** Task success percentage
- **Partial_Correctness:** Benchmark's P metric (continuous score for partial solutions)
- **Avg_Tokens:** Mean token consumption
- **Avg_Rounds:** Mean rounds to convergence
- **Gini_Hierarchy:** Gini coefficient of communication hierarchy
- **Comm_Density:** Communication network density (0-1)
- **Avg_Latency_s:** Mean wall-clock time per task

**Total Rows:** 18 (6 baselines × 3 scales)

**Key Insights to Highlight:**
- Scalability trends (does performance degrade or improve with more agents?)
- Token cost scaling (linear, sublinear, or superlinear?)
- Gini evolution across scales (does hierarchy emerge naturally at larger scales?)

---

## 📊 **TABLE 3: Performance Breakdown by Algorithmic Complexity Tier**

**Location:** `paper_results/baselines/table3_task_complexity_breakdown.csv` and `.md`

**Purpose:** Evaluate how each baseline performs across the 3 task complexity paradigms

### Structure:

| Baseline | Complexity_Tier | Runs | Success_Rate | Partial_Correctness | Avg_Tokens | Avg_Rounds | Gini_Hierarchy |
|----------|----------------|------|--------------|---------------------|------------|------------|----------------|
| Independent Agents | Level I (Aggregation) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Independent Agents | Level II (Mesh Routing) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Independent Agents | Level III (Global Shuffle) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Flat Broadcast Debate | Level I (Aggregation) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Flat Broadcast Debate | Level II (Mesh Routing) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Flat Broadcast Debate | Level III (Global Shuffle) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Central Coordinator | Level I (Aggregation) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Central Coordinator | Level II (Mesh Routing) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Central Coordinator | Level III (Global Shuffle) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Hierarchical Tree | Level I (Aggregation) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Hierarchical Tree | Level II (Mesh Routing) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Hierarchical Tree | Level III (Global Shuffle) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Fixed Predefined Roles | Level I (Aggregation) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Fixed Predefined Roles | Level II (Mesh Routing) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| Fixed Predefined Roles | Level III (Global Shuffle) | XX | XX.X% | X.XXX | X,XXX | X.XX | X.XXX |
| **ORCHESTRA (Ours)** | **Level I (Aggregation)** | **XX** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** |
| **ORCHESTRA (Ours)** | **Level II (Mesh Routing)** | **XX** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** |
| **ORCHESTRA (Ours)** | **Level III (Global Shuffle)** | **XX** | **XX.X%** | **X.XXX** | **X,XXX** | **X.XX** | **X.XXX** |

**Complexity Tier Definitions:**
- **Level I (Tasks 1-10):** Cross-silo aggregation (sum, max, median, threshold count)
- **Level II (Tasks 11-20):** Spatial mesh & neighborhood routing (shortest paths, boundary reconciliation)
- **Level III (Tasks 21-30):** Global shuffle & distributed joins (relational joins, key-value lookups)

**Total Rows:** 18 (6 baselines × 3 tiers)

**Key Insights to Highlight:**
- Which coordination paradigm excels at which task type?
- Does emergent organization (ORCHESTRA) adapt better to complexity than fixed structures?
- Token efficiency vs. task complexity

---

## 📊 **TABLE 4: Fault Tolerance and Agent Dropout Degradation**

**Location:** `paper_results/baselines/table4_perturbation_resilience_breakdown.csv` and `.md`

**Purpose:** Measure organizational resilience under fail-stop agent failures

### Structure:

| Baseline | Healthy_Accuracy | Dropout_Accuracy | Accuracy_Delta | Healthy_Tokens | Dropout_Tokens | Token_Delta |
|----------|------------------|------------------|----------------|----------------|----------------|-------------|
| Independent Agents | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| Flat Broadcast Debate | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| Central Coordinator | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| Hierarchical Tree | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| Fixed Predefined Roles | XX.X% | XX.X% | ±X.X% | X,XXX | X,XXX | ±X.X% |
| **ORCHESTRA (Ours)** | **XX.X%** | **XX.X%** | **±X.X%** | **X,XXX** | **X,XXX** | **±X.X%** |

**Column Definitions:**
- **Healthy_Accuracy:** Success rate under normal conditions (no perturbations)
- **Dropout_Accuracy:** Success rate when Agent 1 is dropped at Round 2
- **Accuracy_Delta:** Change in success rate (Dropout - Healthy)
- **Healthy_Tokens:** Mean tokens under normal conditions
- **Dropout_Tokens:** Mean tokens under dropout
- **Token_Delta:** Percentage change in token consumption

**Total Rows:** 6 (5 baselines + ORCHESTRA)

**Key Insights to Highlight:**
- Resilience ranking (smallest accuracy delta = most robust)
- Token efficiency under failure (does coordination collapse waste tokens?)
- Which paradigms gracefully degrade vs. catastrophically fail?

---

## 📈 **FIGURE 1: Multi-Agent Algorithmic Task Success Across Scales**

**Location:** `paper_results/baselines/figure_baseline_accuracy_comparison.png`

**Type:** Grouped Bar Chart

**Purpose:** Visualize success rates for all 6 methods across N=2, 5, 10

### Structure:
- **X-axis:** 6 Baselines (Independent, Broadcast, Central, Hierarchical, Fixed Roles, ORCHESTRA)
- **Y-axis:** Task Success Rate (0-100%)
- **Bars:** 3 bars per baseline (N=2 in blue, N=5 in green, N=10 in orange)
- **Resolution:** 300 DPI (publication quality)

**Visual Highlights:**
- ORCHESTRA bar highlighted with bold border
- Scale-wise color coding
- Grid for readability
- Legend positioned top-left

---

## 📈 **FIGURE 2: Fault Tolerance - Control vs. Agent Dropout Degradation**

**Location:** `paper_results/baselines/figure_perturbation_resilience.png`

**Type:** Side-by-Side Bar Chart

**Purpose:** Compare healthy vs. perturbed accuracy for each baseline

### Structure:
- **X-axis:** 6 Baselines
- **Y-axis:** Success Rate (0-100%)
- **Bars:** 2 bars per baseline (Control/Healthy in blue, Dropout/Perturbed in red)
- **Resolution:** 300 DPI

**Visual Highlights:**
- Clear visual gap between healthy and dropout bars
- ORCHESTRA highlighted
- Annotations showing delta percentages

---

## 📈 **FIGURE 3: Pareto Frontier - Solution Accuracy vs. Token Efficiency**

**Location:** `paper_results/baselines/figure_token_accuracy_pareto.png`

**Type:** Scatter Plot

**Purpose:** Show the accuracy-efficiency tradeoff across all baselines

### Structure:
- **X-axis:** Mean Token Consumption per Task
- **Y-axis:** Task Success Rate (0-100%)
- **Points:** One scatter point per baseline
  - ORCHESTRA as **gold star ⭐** (size 220)
  - Other baselines as circles (size 130)
  - Color-coded per baseline metadata
- **Resolution:** 300 DPI

**Visual Highlights:**
- Upper-left quadrant = ideal (high accuracy, low tokens)
- ORCHESTRA positioned to demonstrate optimal tradeoff
- Annotations with baseline names
- Grid for reference

---

## 📊 **SUPPLEMENTARY DATA: Master Baseline Results CSV**

**Location:** `paper_results/baselines/master_baseline_results.csv`

**Purpose:** Complete unified dataset of all 1,440 experimental runs

**Columns:**
- `case_id` - Unique case identifier
- `baseline` - Method name
- `task_id` - Task identifier (I-01 to III-30)
- `num_agents` - Agent scale (2, 5, 10)
- `protocol` - Communication protocol (msg, broadcast, sfs)
- `perturbation` - Perturbation type (none, agent_dropout)
- `total_rounds` - Rounds to convergence
- `success` - Boolean success flag
- `success_rate` - Continuous success metric (0-1)
- `partial_correctness` - Partial solution score (0-1)
- `token_consumption` - Total tokens used
- `communication_density` - Network density (0-1)
- `gini_out_degree` - Out-degree Gini coefficient
- `gini_in_degree` - In-degree Gini coefficient
- `mean_structural_drift` - Jaccard drift across rounds
- `model` - Model identifier
- `seed` - Random seed
- `total_time_seconds` - Wall-clock execution time

**Total Rows:** 1,440 (540 ORCHESTRA + 900 baselines)

---

## 📊 **ORCHESTRA-SPECIFIC TABLES (Scale-Segregated)**

For each agent scale (N=2, 5, 10), ORCHESTRA generates additional analysis in separate workspace folders:

### **Per-Scale Outputs** (`final_workspace_n2/`, `final_workspace_n5/`, `final_workspace_n10/`):

1. **`batch_comparison_results.csv`** - All 180 ORCHESTRA runs for that scale
   - 30 tasks × 3 protocols × 2 perturbations = 180 runs

2. **`structure_performance_correlations.csv`** - Pearson correlation matrix
   - Rows: Organizational metrics (Gini, drift, density, betweenness)
   - Columns: Performance metrics (success, tokens, rounds, partial correctness)
   - Values: Pearson r correlation coefficients

3. **`longitudinal_comparison.png`** - Dual-panel figure showing:
   - **Left Panel:** Cumulative network density evolution across rounds
   - **Right Panel:** Jaccard structural drift (round-over-round rewiring)

---

## 🎯 **WHAT YOU WILL GET AFTER RUNNING THE BENCHMARKS**

### **Single Command Execution:**

```powershell
# 1. ORCHESTRA (540 runs across N=2,5,10)
.\run_master_benchmark.ps1 -Model "qwen2.5:7b"

# 2. Baselines (900 runs across N=2,5,10)
.\run_baselines_benchmark.ps1 -Model "qwen2.5:7b"
```

### **Automatically Generated Artifacts:**

✅ **4 Publication-Ready Tables** (CSV + Markdown):
1. Table 1: Master baseline comparison (6 methods)
2. Table 2: Scale breakdown (N=2,5,10)
3. Table 3: Task complexity tiers (Level I, II, III)
4. Table 4: Fault tolerance / dropout resilience

✅ **3 Publication-Quality Figures** (300 DPI PNG):
1. Figure 1: Accuracy bar chart across scales
2. Figure 2: Dropout resilience comparison
3. Figure 3: Pareto frontier (accuracy vs tokens)

✅ **Master Dataset CSV** (1,440 runs combined)

✅ **3 Scale-Specific ORCHESTRA Workspaces:**
- N=2: 180 runs + correlations + longitudinal plots
- N=5: 180 runs + correlations + longitudinal plots
- N=10: 180 runs + correlations + longitudinal plots

✅ **Raw Case Directories** (1,440 folders) with:
- `orchestra_profile.json` - Full organizational metrics
- `results.json` - Benchmark evaluation
- `metadata.json` - Run configuration
- `logs/agent-*.jsonl` - Complete agent traces
- `rounds/` - Round-by-round state snapshots

---

## 📝 **PAPER SECTIONS THESE TABLES SUPPORT**

### **Results Section:**
- **Table 1** → Primary empirical comparison (Section 4.1)
- **Figure 1** → Scale-wise performance visualization (Section 4.1)
- **Figure 3** → Efficiency-accuracy tradeoff (Section 4.2)

### **Scalability Analysis:**
- **Table 2** → Detailed metrics by scale (Section 4.3)

### **Task Paradigm Analysis:**
- **Table 3** → Complexity tier breakdown (Section 4.4)

### **Resilience & Adaptation:**
- **Table 4** → Fault tolerance comparison (Section 5.1)
- **Figure 2** → Dropout degradation visualization (Section 5.1)

### **Organizational Evolution:**
- **Longitudinal plots** (per scale) → Structural drift & density evolution (Section 5.2)
- **Correlation matrices** (per scale) → Structure-performance relationships (Section 5.3)

---

## ✅ **VERIFICATION CHECKLIST**

Before paper submission, verify:

- [ ] All 4 tables generated in `paper_results/baselines/`
- [ ] All 3 figures generated as 300 DPI PNG files
- [ ] Master CSV contains exactly 1,440 rows
- [ ] Each baseline has proper literature citations
- [ ] ORCHESTRA rows properly identified (not "nan")
- [ ] Perturbation column correctly populated
- [ ] All 6 baselines present in Table 1
- [ ] All 3 scales (2, 5, 10) present in Table 2
- [ ] All 3 tiers (I, II, III) present in Table 3
- [ ] Correlation matrices show meaningful relationships
- [ ] Longitudinal plots display multi-round evolution

---

## 🎓 **FINAL NOTE**

**These tables and figures are automatically generated.** After running the two PowerShell scripts and waiting ~14-20 hours, you will have a complete, publication-ready empirical dataset with:

- ✅ 6 baseline comparisons (5 literature + ORCHESTRA)
- ✅ 3 agent scales (2, 5, 10)
- ✅ 30 algorithmic tasks
- ✅ 3 communication protocols
- ✅ 2 perturbation conditions
- ✅ 1,440 total experimental runs
- ✅ All tables, figures, and raw data for Q1 journal submission

**No manual table creation. No spreadsheet formatting. No plot adjustments. Everything auto-generated from raw experimental data.**
