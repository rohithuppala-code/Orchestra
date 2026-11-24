# Table 2: Detailed Evaluation Metrics Across Agent Scales (N=2, 5, 10)

| Baseline              |   Scale_N |   Runs | Success_Rate   |   Partial_Correctness | Avg_Tokens   |   Avg_Rounds |   Gini_Hierarchy |   Comm_Density |   Avg_Latency_s |
|:----------------------|----------:|-------:|:---------------|----------------------:|:-------------|-------------:|-----------------:|---------------:|----------------:|
| Independent Agents    |         5 |     15 | 10.7%          |                 0.135 | 11,113       |         9.27 |            0     |          0.003 |           761.5 |
| Flat Broadcast Debate |         5 |     15 | 28.0%          |                 0.293 | 19,927       |        13    |            0.221 |          0.787 |          1038.5 |
| Central Coordinator   |         5 |     15 | 28.0%          |                 0.278 | 26,186       |        13.2  |            0.363 |          1.01  |          1238.7 |
| Hierarchical Tree     |         5 |     15 | 18.7%          |                 0.197 | 13,918       |        14.8  |            0.257 |          1.227 |          1520.7 |
| ORCHESTRA (Ours)      |         5 |     15 | 26.7%          |                 0.267 | 17,802       |        14.4  |            0.334 |          1.83  |          1378.8 |

*Evaluated under healthy conditions (perturbation=none).*
