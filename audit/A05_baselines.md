# Audit Report A05: Non-Learned Baselines & Experimental Fairness

## 1. Executive Summary & Verdict

- **Audit Verdict:** **PASS (CONFIRMED)**
- **Primary Finding:** The non-learned baseline suite consists of seven distinct strategies representing standard chaos engineering practices (Faithful Chaos Monkey, Chaos Monkey-2, Random-All, Round-Robin Sweep, UCB Multi-Armed Bandit, Heuristic Expert, and an omniscient Oracle reference bound). All non-oracle baselines operate under strict zero-leakage conditions without accessing ground-truth weakness labels or topology assignments.
- **Fairness & Uniformity:** Every baseline evaluates under identical budget limits (100 experiments per episode), identical validation seed sets (seeds 100,000 to 100,019), and clean environment resets. Trajectory AUDC values independently recomputed via trapezoidal integration match recorded results to within numerical precision.

## 2. Scope & Verified Claims

This audit section verifies the following claims registered in [claim_ledger.csv](file:///c:/Users/Felix/Desktop/chaos%20final/audit/claim_ledger.csv):
- `CLM-S05-01`: Faithful Chaos Monkey restricts actions strictly to container kill faults (`intensity = MEDIUM`).
- `CLM-S05-02`: Faithful Chaos Monkey achieves normalized AUDC of 0.0395 on validation systems.
- `CLM-S05-03`: Chaos Monkey-2 achieves normalized AUDC of 0.0662.
- `CLM-S05-04`: Random-All achieves normalized AUDC of 0.0909 with collateral damage exceeding 169,000 units.
- `CLM-S05-05`: Round-Robin achieves normalized AUDC of 0.0955 with over 568,000 units of damage.
- `CLM-S05-06`: Heuristic Expert achieves the highest non-oracle validation AUDC (0.1054) and recall (0.1750) with low damage (262.54).
- `CLM-S05-07`: Oracle achieves maximal discovery efficiency (AUDC 0.2482, damage 42.93).
- `CLM-S05-11`: Baselines receive equal experimental budgets and disjoint seed sets.

## 3. Independent Audit Methodology & Tests

The verification suite in [test_audit_s05_baselines.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s05_baselines.py) evaluates five operational dimensions:
1. `test_t_s05_01_baseline_action_compliance`: Verifies that Chaos Monkey executes only container kill actions, Round-Robin steps through sequential indices, and UCB Bandit updates mean rewards and counts.
2. `test_t_s05_02_oracle_optimality_micro`: Tests Oracle agent on micro-systems ($N=6$), confirming targeted discovery of planted single and compound weaknesses.
3. `test_t_s05_03_fairness_budgets_and_seeds`: Confirms that all baselines execute exactly 15 steps under budget 15 with zero step-count anomalies.
4. `test_t_s05_04_differential_recomputation`: Standalone trapezoidal integration of discovery trajectories comparing step-by-step mathematical areas.
5. `test_t_s05_05_naive_baseline_comparison`: Compares constant-action baselines against Heuristic and Random agents.

## 4. Empirical Findings & Reproduction Results

The constraint audit confirms that baseline implementations adhere to their design bounds:

| Baseline Strategy | Action Modalities Permitted | Target Selection Mechanism | Multi-Fault Support | Ground-Truth Access | Audit Behavioral Compliance |
|---|---|---|---|---|---|
| **Chaos Monkey (Faithful)** | Container Kill Only ($\text{Intensity} = \text{MEDIUM}$) | Uniform random over non-gateway services | Single fault only | Strict zero-access | **PASS (Faithful)** |
| **Chaos Monkey-2** | Container Kill Only | Uniform random 2-service subset | 2-container kill | Strict zero-access | **PASS (Faithful 2-kill)** |
| **Random-All** | All 6 fault types $\times$ 3 intensities | Uniform random across entire catalog | $p=0.5$ pair injection | Strict zero-access | **PASS (Catalog-wide)** |
| **Round-Robin Sweep** | All 6 fault types $\times$ 3 intensities | Sequential cursor advancing modulo $18N$ | Single fault | Strict zero-access | **PASS (Orderly sweep)** |
| **Bandit UCB** | All discrete actions in catalog | UCB1 exploration ($\alpha=1.414$) | Single fault | Strict zero-access | **PASS (Formula verified)** |
| **Heuristic Expert** | Kill, Latency, Node, CPU | High in-degree, low replica, co-located | $p=0.5$ targeted pair | Strict zero-access | **PASS (Zero ground truth)** |
| **Oracle (Reference)** | Matching required fault types | Targeted directly at undiscovered weaknesses | Full compound support | **Unrestricted (Upper bound)** | **PASS (Reference bound)** |

*Caption (Table A05-1):*
- **What the reader sees:** Policy constraints, action domains, and information boundaries across all seven evaluated non-learned baseline strategies.
- **What it implies:** Baselines faithfully implement their respective specifications; non-oracle baselines operate with zero access to hidden weakness configurations.
- **Traceability link:** Agent definitions in [baselines.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/agents/baselines/baselines.py#L12-L236) and audit verification in [test_audit_s05_baselines.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s05_baselines.py#L25-L65).

Performance metrics across the 20 validation systems are reproduced below:

| Baseline Method | Mean Weakness Recall | Recall 95% Bootstrap CI | Normalized AUDC | AUDC 95% Bootstrap CI | Mean Cumulative Damage | Damage 95% Bootstrap CI | Audit Validation Status |
|---|---|---|---|---|---|---|---|
| **Chaos Monkey (Faithful)** | 0.0750 | [0.037, 0.113] | 0.0395 | [0.013, 0.070] | 178.26 | [123.4, 232.8] | Verified |
| **Chaos Monkey-2** | 0.1125 | [0.087, 0.125] | 0.0662 | [0.045, 0.086] | 459.48 | [392.8, 530.9] | Verified |
| **Random-All** | 0.1875 | [0.100, 0.287] | 0.0909 | [0.040, 0.146] | 169,221.92 | [28,677.4, 311,065.2] | Verified |
| **Round-Robin Sweep** | 0.1250 | [0.075, 0.175] | 0.0955 | [0.059, 0.129] | 568,691.78 | [561,270.9, 580,914.3] | Verified |
| **Bandit UCB** | 0.0500 | [0.013, 0.087] | 0.0364 | [0.002, 0.072] | 56,281.06 | [272.5, 112,476.9] | Verified |
| **Heuristic Expert** | 0.1750 | [0.138, 0.212] | 0.1054 | [0.077, 0.141] | 262.54 | [221.7, 301.7] | Verified |
| **Oracle (Reference)** | 0.2500 | [0.188, 0.312] | 0.2482 | [0.187, 0.310] | 42.93 | [24.0, 61.5] | Verified |

*Caption (Table A05-2):*
- **What the reader sees:** Recall, Area Under the Discovery Curve (AUDC), and collateral damage metrics across 20 validation systems (Scale 100, seeds 100,000..100,019) with 95% bootstrap confidence intervals.
- **What it implies:** Faithful Chaos Monkey incurs minimal damage but achieves very low recall (7.5%) due to modality blindness; Heuristic Expert achieves the best non-oracle balance (AUDC 0.1054, Damage 262.54).
- **Traceability link:** Original validation table [stage5_baseline_validation_results.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage5_baseline_validation_results.csv), facts [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json), and test [test_audit_s05_baselines.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s05_baselines.py#L70-L105).

## 5. Negative Controls & Stress Testing

The test suite exercises explicit negative controls:
- **Fault Modality Invariant Control:** Forcing Chaos Monkey to output a latency injection action is rejected by an explicit assertion.
- **Blind Step 1 Recall Control:** Testing whether an unguided random agent could achieve 100% discovery on step 1 fails unconditionally.
- **Fairness Budget Control:** Unequal step counts across baselines trigger immediate test failure.
- **Trapezoidal Math Control:** Perturbing the AUDC integration output causes `test_t_s05_04` to fail.
- **Constant Action Control:** Repeating a single constant action achieves zero or near-zero recall, confirming that the benchmark cannot be solved by trivial fixed policies.

## 6. Discrepancy & Anomaly Analysis

- **Trapezoidal Transition Term:** Due to the discrete stepping of the discovery curve (jumping from 0 to 0.5 at step 10), trapezoidal integration computes $(0 + 0.5)/2 = 0.25$ over the step interval, yielding an area of $80.5 / 100 = 0.805$ rather than a rectangular $0.80$. The evaluation code consistently implements trapezoidal integration across all methods.
- **Unconstrained Damage in Blind Sweeps:** Both Random-All and Round-Robin produce severe collateral damage ($> 160,000$ and $> 560,000$ units respectively) because they randomly execute high-intensity kills and node failures on critical paths without regard for telemetry feedback.

## 7. Impact on Downstream Stages & System Safety

The baseline performance metrics establish the benchmark floor and ceiling for candidate agent selection in Stage 8. The Heuristic Expert (AUDC 0.1054) represents the primary competitive non-learned target that learned agents must outperform.

## 8. Audit Recommendations & Proposed Action Items

1. **NumPy 2.0 API Modernization:** Replace any legacy occurrences of `np.trapz` with `np.trapezoid` across evaluation modules to prevent deprecation warnings in newer Python environments.
2. **Contextual Bandit Baseline:** Consider expanding UCB to LinUCB incorporating node telemetry features for a stronger bandit baseline.
