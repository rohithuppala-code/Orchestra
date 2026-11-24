# Table 4: Fault Tolerance and Agent Dropout Degradation Breakdown

| Baseline              | Healthy_Accuracy   | Dropout_Accuracy   | Accuracy_Delta   | Healthy_Tokens   | Dropout_Tokens   | Token_Delta   |
|:----------------------|:-------------------|:-------------------|:-----------------|:-----------------|:-----------------|:--------------|
| Independent Agents    | 13.3%              | 10.0%              | -3.3%            | 3,584            | 4,658            | +30.0%        |
| Flat Broadcast Debate | 46.7%              | 10.0%              | -36.7%           | 3,848            | 4,209            | +9.4%         |
| Central Coordinator   | 30.0%              | 16.7%              | -13.3%           | 8,064            | 4,495            | -44.3%        |
| Hierarchical Tree     | 50.0%              | 13.3%              | -36.7%           | 7,146            | 2,593            | -63.7%        |
| ORCHESTRA (Ours)      | 40.0%              | 6.7%               | -33.3%           | 6,136            | 2,202            | -64.1%        |

*Agent Dropout: Node dropped at Round 2 during active coordination.*
