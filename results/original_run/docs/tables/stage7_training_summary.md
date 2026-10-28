<!-- Table: stage7_training_summary -->

| Candidate ID | Name | Family | Validation AUDC | AUDC Std | Validation Recall | Cumulative Damage | Tuning Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | PPO-MLP | policy_gradient | 0.0252 | 0.0225 | 0.0625 | 115.2000 | Tuned (Reverted) |
| C02 | PPO-GNN | structure_aware | 0.0435 | 0.0322 | 0.0625 | 4154.20 | Initial |
| C03 | PPO-GRU | recurrent | 0.0390 | 0.0551 | 0.0417 | 58.2000 | Initial |
| C04 | A2C | policy_gradient | 0.0312 | 0.0442 | 0.0312 | 298.1000 | Tuned (Accepted) |
| C05 | DQN-Dueling | value_based | 0.0311 | 0.0432 | 0.0417 | 95.2000 | Tuned (Accepted) |
| C06 | REINFORCE | policy_gradient | 0.0339 | 0.0424 | 0.1042 | 288.0000 | Initial |
| C07 | Curriculum-PPO | curriculum | 0.0304 | 0.0430 | 0.0312 | 302.3000 | Initial |
| C08 | BC-PPO | imitation | 0.0291 | 0.0411 | 0.0312 | 106.8000 | Tuned (Reverted) |
| C09 | PPO-RND | exploration | 0.0489 | 0.0352 | 0.0938 | 83.1000 | Initial |
| C10 | ES-Policy | gradient_free | 0.0205 | 0.0241 | 0.0312 | 151.3000 | Tuned (Reverted) |
| C11 | LinUCB-Contextual | bandit | 0.0000 | 0.0000 | 0.0000 | 5.6000 | Tuned (Reverted) |
| C12 | TreeRanker | supervised | **0.0938** | 0.0000 | 0.0938 | 576.4000 | Initial |
