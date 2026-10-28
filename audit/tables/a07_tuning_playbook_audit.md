# Table A07-1: Automated Tuning Playbook Decisions & Standard Error Audit

| Candidate ID | Name | Round | Proposed Hyperparameter Shift | Pre-Tuning AUDC | Post-Tuning AUDC | Empirical Improvement ($\Delta$) | Validation Standard Error ($1 \text{ SE}$) | Playbook Decision Rule ($\Delta > 1 \text{ SE}$) | Final Audit Decision |
|---|---|---|---|---|---|---|---|---|---|
| **C08** | BC-PPO | 2 | `{'lr': 0.0001, 'entropy': 0.02}` | 0.0291 | 0.0020 | $-0.0271$ | $0.0237$ | Fails (Negative) | **REVERTED** |
| **C01** | PPO-MLP | 2 | `{'lr': 0.0001, 'entropy': 0.03}` | 0.0252 | 0.0297 | $+0.0045$ | $0.0130$ | Fails ($0.0045 \le 0.0130$) | **REVERTED** |
| **C10** | ES-Policy | 2 | `{'sigma': 0.08, 'lr': 0.03}` | 0.0205 | 0.0204 | $-0.0001$ | $0.0139$ | Fails (Negative) | **REVERTED** |
| **C04** | A2C | 2 | `{'lr': 0.0003, 'entropy': 0.03}` | 0.0028 | 0.0312 | $+0.0284$ | $0.0023$ | Passes ($0.0284 > 0.0023$) | **ACCEPTED** |
| **C05** | DQN-Dueling | 2 | `{'lr': 0.0005, 'decay': 0.99}` | 0.0000 | 0.0311 | $+0.0311$ | $0.0000$ | Passes ($0.0311 > 0.0000$) | **ACCEPTED** |
| **C11** | LinUCB | 2 | `{'alpha': 0.8}` | 0.0000 | 0.0000 | $+0.0000$ | $0.0000$ | Fails (Zero delta) | **REVERTED** |

*Caption (Table A07-1):*
- **What the reader sees:** Pre- and post-tuning validation metrics, empirical deltas, and standard error thresholds for the six below-median candidates in Round 2.
- **What it implies:** Tuning strictly followed the pre-registered decision playbook without cherry-picking: only candidates exhibiting improvements exceeding one standard error (C04, C05) were accepted; all others were reverted to preserve baseline weights.
- **Traceability link:** Original tuning ledger [tuning_log.csv](file:///c:/Users/Felix/Desktop/chaos%20final/results/tuning_log.csv) and test suite [test_audit_s07_training.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s07_training.py#L40-L70).
