# Table 3: Performance Breakdown by Algorithmic Complexity Tier

| Baseline              | Complexity_Tier            |   Runs | Success_Rate   |   Partial_Correctness | Avg_Tokens   |   Avg_Rounds |   Gini_Hierarchy |
|:----------------------|:---------------------------|-------:|:---------------|----------------------:|:-------------|-------------:|-----------------:|
| Independent Agents    | Level I (Aggregation)      |      5 | 16.0%          |                 0.16  | 10,601       |         12.2 |            0     |
| Independent Agents    | Level II (Mesh Routing)    |      5 | 16.0%          |                 0.196 | 7,143        |          9.4 |            0     |
| Independent Agents    | Level III (Global Shuffle) |      5 | 0.0%           |                 0.05  | 15,594       |          6.2 |            0     |
| Flat Broadcast Debate | Level I (Aggregation)      |      5 | 64.0%          |                 0.64  | 14,179       |         10.6 |            0.173 |
| Flat Broadcast Debate | Level II (Mesh Routing)    |      5 | 20.0%          |                 0.232 | 29,634       |         13.4 |            0.225 |
| Flat Broadcast Debate | Level III (Global Shuffle) |      5 | 0.0%           |                 0.006 | 15,967       |         15   |            0.265 |
| Central Coordinator   | Level I (Aggregation)      |      5 | 40.0%          |                 0.4   | 26,854       |         11   |            0.361 |
| Central Coordinator   | Level II (Mesh Routing)    |      5 | 20.0%          |                 0.2   | 34,581       |         14   |            0.358 |
| Central Coordinator   | Level III (Global Shuffle) |      5 | 24.0%          |                 0.234 | 17,124       |         14.6 |            0.371 |
| Hierarchical Tree     | Level I (Aggregation)      |      5 | 48.0%          |                 0.48  | 11,920       |         14.4 |            0.166 |
| Hierarchical Tree     | Level II (Mesh Routing)    |      5 | 8.0%           |                 0.112 | 13,761       |         15   |            0.285 |
| Hierarchical Tree     | Level III (Global Shuffle) |      5 | 0.0%           |                 0     | 16,072       |         15   |            0.32  |
| ORCHESTRA (Ours)      | Level I (Aggregation)      |      5 | 48.0%          |                 0.48  | 16,987       |         14.8 |            0.266 |
| ORCHESTRA (Ours)      | Level II (Mesh Routing)    |      5 | 28.0%          |                 0.28  | 18,392       |         13.4 |            0.334 |
| ORCHESTRA (Ours)      | Level III (Global Shuffle) |      5 | 4.0%           |                 0.04  | 18,026       |         15   |            0.401 |

*Task Tiers: Level I (Aggregation, I-*), Level II (Mesh Routing, II-*), Level III (Global Shuffle, III-*).*
