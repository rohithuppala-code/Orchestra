# Table 2: Detailed Evaluation Metrics Across Agent Scales (N=2, 5, 10)

| Baseline              |   Scale_N |   Runs | Success_Rate   |   Partial_Correctness | Avg_Tokens   |   Avg_Rounds |   Gini_Hierarchy |   Comm_Density |   Avg_Latency_s |
|:----------------------|----------:|-------:|:---------------|----------------------:|:-------------|-------------:|-----------------:|---------------:|----------------:|
| Independent Agents    |         2 |     15 | 13.3%          |                 0.213 | 3,584        |         7.87 |            0     |          0.033 |           142.8 |
| Flat Broadcast Debate |         2 |     15 | 46.7%          |                 0.487 | 3,848        |        10.73 |            0.154 |          2.267 |           279.3 |
| Central Coordinator   |         2 |     15 | 30.0%          |                 0.463 | 8,064        |        11.93 |            0.156 |          2.3   |           449.8 |
| Hierarchical Tree     |         2 |     15 | 50.0%          |                 0.58  | 7,146        |         9.13 |            0.111 |          2.367 |           287.3 |
| ORCHESTRA (Ours)      |         2 |     15 | 40.0%          |                 0.4   | 6,136        |        11.07 |            0.183 |          2.567 |           353.3 |

*Evaluated under healthy conditions (perturbation=none).*
