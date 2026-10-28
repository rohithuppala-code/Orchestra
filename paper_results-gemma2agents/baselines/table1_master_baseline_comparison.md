# Table 1: Master Empirical Multi-Agent Baseline Comparison

| Baseline              | Paradigm         | Citation                                 | Success_N2   | Success_N5   | Success_N10   | Success_Overall   | Tokens_Mean   |   Rounds_Mean |   Gini_OutDegree | Dropout_Success   | Resilience_Delta   |
|:----------------------|:-----------------|:-----------------------------------------|:-------------|:-------------|:--------------|:------------------|:--------------|--------------:|-----------------:|:------------------|:-------------------|
| Independent Agents    | No Communication | Wang et al. (ICLR 2023)                  | 1.7%         | -            | -             | 1.7%              | 1,992         |           2.8 |            0.092 | -                 | -                  |
| Flat Broadcast Debate | Complete Mesh    | Qian et al. (ACL 2024); Du et al. (2023) | 5.0%         | -            | -             | 5.0%              | 1,726         |           2.9 |            0.142 | -                 | -                  |
| ORCHESTRA (Ours)      | Emergent Dynamic | This Work                                | 6.7%         | -            | -             | 6.7%              | 1,698         |           2.9 |            0.158 | -                 | -                  |

*Note: N=2, 5, 10 evaluated on SILO-BENCH. Resilience Delta denotes accuracy change under agent dropout failure.*
