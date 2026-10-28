<!-- Table: stage6_candidate_smoke_benchmarks -->

| Candidate ID | Name | Family | Trainable Parameters | Throughput (steps/sec) | Memory Delta (MB) | Gradient Update Clean |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | PPO-MLP | policy_gradient | 18323 | 77.9000 | 5.8600 | PASS |
| C02 | PPO-GNN | structure_aware | 22611 | 75.3000 | 0.3600 | PASS |
| C03 | PPO-GRU | recurrent | 47123 | 73.2000 | 0.9100 | PASS |
| C04 | A2C | policy_gradient | 18323 | 106.0000 | 0.0000 | PASS |
| C05 | DQN-Dueling | value_based | 7634 | 114.0000 | 0.0000 | PASS |
| C06 | REINFORCE | policy_gradient | 18323 | 111.6000 | 0.0000 | PASS |
| C07 | Curriculum-PPO | curriculum | 22611 | 79.5000 | 0.0200 | PASS |
| C08 | BC-PPO | imitation | 18323 | 79.9000 | 0.0000 | PASS |
| C09 | PPO-RND | exploration | 18323 | 78.1000 | 0.0100 | PASS |
| C10 | ES-Policy | gradient_free | 2802 | 112.8000 | 0.0500 | PASS |
| C11 | LinUCB-Contextual | bandit | 1536 | 30.7000 | 0.3200 | PASS |
| C12 | TreeRanker | supervised | 12000 | **120.0000** | 0.0200 | PASS |
