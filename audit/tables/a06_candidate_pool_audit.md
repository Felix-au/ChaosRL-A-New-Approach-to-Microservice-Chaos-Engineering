# Table A06-1: Candidate Agents Pool Architecture & Performance Specification Audit

| Candidate ID | Agent Name | Algorithmic Family | Core Architectural Mechanism | Trainable Parameters | Inference Throughput (steps/sec) | Audit Verification Status |
|---|---|---|---|---|---|---|
| **C01** | PPO-MLP | Policy Gradient | Per-node shared MLP scorer + value network | 18,323 | 77.9 | **VERIFIED** |
| **C02** | PPO-GNN | Structure-Aware | 2-layer Graph Convolutional Network (GCN) | 22,611 | 75.3 | **VERIFIED** |
| **C03** | PPO-GRU | Recurrent Policy | Gated Recurrent Unit (GRU) temporal memory | 47,123 | 73.2 | **VERIFIED** |
| **C04** | A2C | Policy Gradient | Synchronous Advantage Actor-Critic baseline | 18,323 | 106.0 | **VERIFIED** |
| **C05** | DQN-Dueling | Value-Based | Dueling Q-network with masked action values | 7,634 | 114.0 | **VERIFIED** |
| **C06** | REINFORCE | Policy Gradient | Monte Carlo policy gradient with baseline | 18,323 | 111.6 | **VERIFIED** |
| **C07** | Curriculum-PPO | Curriculum RL | Multi-scale progressive topology staging | 22,611 | 79.5 | **VERIFIED** |
| **C08** | BC-PPO | Imitation / Hybrid | Behavioral cloning pretraining on Oracle traces | 18,323 | 79.9 | **VERIFIED** |
| **C09** | PPO-RND | Exploration | Random Network Distillation curiosity bonus | 18,323 | 78.1 | **VERIFIED** |
| **C10** | ES-Policy | Gradient-Free | Natural Evolution Strategies parameter search | 2,802 | 112.8 | **VERIFIED** |
| **C11** | LinUCB-Contextual | Bandit | Ridge regression over node telemetry vectors | 1,536 | 30.7 | **VERIFIED** |
| **C12** | TreeRanker | Supervised / Heuristic | Gradient-boosted decision tree ranker | 12,000 | 120.0 | **VERIFIED** |

*Caption (Table A06-1):*
- **What the reader sees:** Architecture, algorithmic family, parameter count, and CPU inference throughput across all 12 candidate agents in the Stage 6 pool.
- **What it implies:** The pool spans 8 distinct machine learning families (policy gradient, structure-aware, recurrent, value-based, curriculum, imitation, curiosity, and supervised ranking), all operating under identical action masking.
- **Traceability link:** Registry [registry.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/agents/candidates/registry.py#L1-L60), smoke runner [smoke_runner.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/agents/candidates/smoke_runner.py#L25-L65), and test [test_audit_s06_candidates.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s06_candidates.py#L20-L45).

