<!-- Table: stage9_ablation_study -->

| Ablation Dimension | Configuration | AUDC | Weakness Recall | Cumulative Damage |
| --- | --- | --- | --- | --- |
| Reward Formulation | Sparse R1 (No Penalty) | 0.0620 | 0.0625 | 780.7000 |
| Reward Formulation | Regularized R2 (Default) | 0.0625 | 0.0625 | 781.2000 |
| Reward Formulation | Dense Shaped R3 | 0.0625 | 0.0625 | 781.8000 |
| Observation Mode | Black-Box (Telemetry Only) | 0.0622 | 0.0625 | 738.9000 |
| Observation Mode | Gray-Box (Static Flags Exposed) | 0.0241 | 0.0312 | 19254974.60 |
