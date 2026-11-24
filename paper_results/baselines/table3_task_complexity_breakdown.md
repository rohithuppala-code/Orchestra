# Table 3: Performance Breakdown by Algorithmic Complexity Tier

| Baseline              | Complexity_Tier            |   Runs | Success_Rate   |   Partial_Correctness | Avg_Tokens   |   Avg_Rounds |   Gini_Hierarchy |
|:----------------------|:---------------------------|-------:|:---------------|----------------------:|:-------------|-------------:|-----------------:|
| Independent Agents    | Level I (Aggregation)      |     10 | 18.0%          |                 0.18  | 6,353        |          9.6 |            0     |
| Independent Agents    | Level II (Mesh Routing)    |     10 | 18.0%          |                 0.287 | 4,518        |          9.3 |            0     |
| Independent Agents    | Level III (Global Shuffle) |     10 | 0.0%           |                 0.055 | 11,175       |          6.8 |            0     |
| Flat Broadcast Debate | Level I (Aggregation)      |     10 | 57.0%          |                 0.57  | 8,914        |         10.4 |            0.151 |
| Flat Broadcast Debate | Level II (Mesh Routing)    |     10 | 45.0%          |                 0.466 | 16,313       |         11.6 |            0.213 |
| Flat Broadcast Debate | Level III (Global Shuffle) |     10 | 10.0%          |                 0.133 | 10,435       |         13.6 |            0.199 |
| Central Coordinator   | Level I (Aggregation)      |     10 | 40.0%          |                 0.5   | 15,417       |         10.4 |            0.247 |
| Central Coordinator   | Level II (Mesh Routing)    |     10 | 30.0%          |                 0.414 | 23,012       |         13.4 |            0.251 |
| Central Coordinator   | Level III (Global Shuffle) |     10 | 17.0%          |                 0.197 | 12,947       |         13.9 |            0.28  |
| Hierarchical Tree     | Level I (Aggregation)      |     10 | 54.0%          |                 0.64  | 7,632        |         11.1 |            0.15  |
| Hierarchical Tree     | Level II (Mesh Routing)    |     10 | 29.0%          |                 0.326 | 8,450        |         13.1 |            0.186 |
| Hierarchical Tree     | Level III (Global Shuffle) |     10 | 20.0%          |                 0.2   | 15,513       |         11.7 |            0.216 |
| ORCHESTRA (Ours)      | Level I (Aggregation)      |     10 | 54.0%          |                 0.54  | 12,952       |         11.9 |            0.157 |
| ORCHESTRA (Ours)      | Level II (Mesh Routing)    |     10 | 24.0%          |                 0.24  | 11,181       |         12.8 |            0.277 |
| ORCHESTRA (Ours)      | Level III (Global Shuffle) |     10 | 22.0%          |                 0.22  | 11,773       |         13.5 |            0.341 |

*Task Tiers: Level I (Aggregation, I-*), Level II (Mesh Routing, II-*), Level III (Global Shuffle, III-*).*
