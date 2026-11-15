# Table 3: Performance Breakdown by Algorithmic Complexity Tier

| Baseline              | Complexity_Tier            |   Runs | Success_Rate   |   Partial_Correctness | Avg_Tokens   |   Avg_Rounds |   Gini_Hierarchy |
|:----------------------|:---------------------------|-------:|:---------------|----------------------:|:-------------|-------------:|-----------------:|
| Independent Agents    | Level I (Aggregation)      |      5 | 20.0%          |                 0.2   | 2,104        |          7   |            0     |
| Independent Agents    | Level II (Mesh Routing)    |      5 | 20.0%          |                 0.378 | 1,892        |          9.2 |            0     |
| Independent Agents    | Level III (Global Shuffle) |      5 | 0.0%           |                 0.06  | 6,756        |          7.4 |            0     |
| Flat Broadcast Debate | Level I (Aggregation)      |      5 | 50.0%          |                 0.5   | 3,649        |         10.2 |            0.129 |
| Flat Broadcast Debate | Level II (Mesh Routing)    |      5 | 70.0%          |                 0.7   | 2,992        |          9.8 |            0.201 |
| Flat Broadcast Debate | Level III (Global Shuffle) |      5 | 20.0%          |                 0.26  | 4,903        |         12.2 |            0.133 |
| Central Coordinator   | Level I (Aggregation)      |      5 | 40.0%          |                 0.6   | 3,980        |          9.8 |            0.133 |
| Central Coordinator   | Level II (Mesh Routing)    |      5 | 40.0%          |                 0.628 | 11,442       |         12.8 |            0.144 |
| Central Coordinator   | Level III (Global Shuffle) |      5 | 10.0%          |                 0.16  | 8,771        |         13.2 |            0.19  |
| Hierarchical Tree     | Level I (Aggregation)      |      5 | 60.0%          |                 0.8   | 3,345        |          7.8 |            0.133 |
| Hierarchical Tree     | Level II (Mesh Routing)    |      5 | 50.0%          |                 0.54  | 3,139        |         11.2 |            0.087 |
| Hierarchical Tree     | Level III (Global Shuffle) |      5 | 40.0%          |                 0.4   | 14,955       |          8.4 |            0.112 |
| ORCHESTRA (Ours)      | Level I (Aggregation)      |      5 | 60.0%          |                 0.6   | 8,917        |          9   |            0.048 |
| ORCHESTRA (Ours)      | Level II (Mesh Routing)    |      5 | 20.0%          |                 0.2   | 3,971        |         12.2 |            0.22  |
| ORCHESTRA (Ours)      | Level III (Global Shuffle) |      5 | 40.0%          |                 0.4   | 5,520        |         12   |            0.28  |

*Task Tiers: Level I (Aggregation, I-*), Level II (Mesh Routing, II-*), Level III (Global Shuffle, III-*).*
