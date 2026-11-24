# Table 1: Master Empirical Multi-Agent Baseline Comparison

| Baseline              | Paradigm         | Citation                                 | Success_N2   | Success_N5   | Success_N10   | Success_Overall   | Tokens_Mean   |   Rounds_Mean |   Gini_OutDegree | Dropout_Success   | Resilience_Delta   |
|:----------------------|:-----------------|:-----------------------------------------|:-------------|:-------------|:--------------|:------------------|:--------------|--------------:|-----------------:|:------------------|:-------------------|
| Independent Agents    | No Communication | Wang et al. (ICLR 2023)                  | 13.3%        | 10.7%        | -             | 12.0%             | 7,348         |           8.6 |            0     | 8.3%              | -3.7%              |
| Flat Broadcast Debate | Complete Mesh    | Qian et al. (ACL 2024); Du et al. (2023) | 46.7%        | 28.0%        | -             | 37.3%             | 11,887        |          11.9 |            0.188 | 11.0%             | -26.3%             |
| Central Coordinator   | Star Hub         | Wu et al. (AutoGen / ICLR 2024)          | 30.0%        | 28.0%        | -             | 29.0%             | 17,125        |          12.6 |            0.26  | 13.7%             | -15.3%             |
| Hierarchical Tree     | Static Tree      | Wang et al. (MacNet, 2024/2025)          | 50.0%        | 18.7%        | -             | 34.3%             | 10,532        |          12   |            0.184 | 6.7%              | -27.7%             |
| ORCHESTRA (Ours)      | Emergent Dynamic | This Work                                | 40.0%        | 26.7%        | -             | 33.3%             | 11,969        |          12.7 |            0.258 | 6.7%              | -26.7%             |

*Note: N=2, 5 empirically evaluated on SILO-BENCH (N=10 designated for future scaling). Resilience Delta denotes accuracy change under agent dropout failure.*
