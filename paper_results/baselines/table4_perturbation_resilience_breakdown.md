# Table 4: Fault Tolerance and Agent Dropout Degradation Breakdown

| Baseline              | Healthy_Accuracy   | Dropout_Accuracy   | Accuracy_Delta   | Healthy_Tokens   | Dropout_Tokens   | Token_Delta   |
|:----------------------|:-------------------|:-------------------|:-----------------|:-----------------|:-----------------|:--------------|
| Independent Agents    | 12.0%              | 8.3%               | -3.7%            | 7,348            | 10,604           | +44.3%        |
| Flat Broadcast Debate | 37.3%              | 11.0%              | -26.3%           | 11,887           | 9,322            | -21.6%        |
| Central Coordinator   | 29.0%              | 13.7%              | -15.3%           | 17,125           | 8,627            | -49.6%        |
| Hierarchical Tree     | 34.3%              | 6.7%               | -27.7%           | 10,532           | 7,597            | -27.9%        |
| ORCHESTRA (Ours)      | 33.3%              | 6.7%               | -26.7%           | 11,969           | 7,382            | -38.3%        |

*Agent Dropout: Node dropped at Round 2 during active coordination.*
