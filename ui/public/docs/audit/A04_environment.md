# Audit Report A04: Gymnasium Environment Interface & Reward Safety

## 1. Executive Summary & Verdict

- **Audit Verdict:** **PASS (CONFIRMED)**
- **Primary Finding:** The `ChaosEnv` reinforcement learning environment complies strictly with standard Gymnasium API conventions (`reset`, `step`, discrete action spaces, and dictionary observation spaces). The discrete action catalog scales exactly as $18 \times N$ actions (accounting for 6 fault modalities $\times$ 3 intensity tiers per service). An exhaustive lexical and tensor-level security scan verified zero leakage of planted weakness identities, ground-truth labels, or target service identifiers in observations or step diagnostic dictionaries.
- **Reward Safety Alignment:** The default reward formulation ($R_2$) imposes an explicit penalty on cumulative system damage ($w_d = 0.05$) and action repetition ($w_r = 0.02$). Evaluation of the adversarial Damage Maximizer probe demonstrates that unconstrained destructive actions receive large negative returns under $R_2$, proving that the reward function disincentivizes brute-force denial-of-service reward hacking.

## 2. Scope & Verified Claims

This audit section verifies the following claims registered in [claim_ledger.csv](file:///c:/Users/Felix/Desktop/chaos%20final/audit/claim_ledger.csv):
- `CLM-S04-01`: Scale 100 discrete action catalog size is exactly 1,800.
- `CLM-S04-02`: Damage Maximizer probe return under $R_2$ is negative (observed: $-3.82$).
- `CLM-S04-03`: Random exploration policy return under $R_2$ is negative due to collateral damage (observed: $-20.85$).
- `CLM-S04-04`: Observations contain zero ground-truth weakness or target ID information.
- `CLM-S04-05`: Action masking guarantees that invalid actions (such as direct gateway termination) have zero probability of selection.

## 3. Independent Audit Methodology & Tests

The verification suite in [test_audit_s04_environment.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s04_environment.py) executes five targeted verification modules:
1. `test_t_s04_01_gymnasium_api_and_action_catalog`: Verifies episode step lifecycle, exact termination at the experiment budget, and masking of illegal actions (service 0 container kill).
2. `test_t_s04_02_zero_hidden_information_leak`: Automated security scan searching for forbidden tokens (`target_service_ids`, `required_fault_types`, `planted_weaknesses`, `ground_truth`) across observation keys, feature tensors, and info metadata.
3. `test_t_s04_03_reward_formulation_and_safety`: Step-by-step mathematical recomputation of sparse ($R_1$), default ($R_2$), and shaped ($R_3$) reward values against recorded damage and duplicate action counters.
4. `test_t_s04_04_feature_dimensions_black_vs_gray_box`: Differential inspection of feature matrices verifying 16 dimensions per node in Black-Box mode versus 18 dimensions in Gray-Box mode.
5. `test_t_s04_05_observation_noise_robustness`: Injecting zero-mean Gaussian noise into telemetry features and asserting finite tensor bounds and valid step transitions.

## 4. Empirical Findings & Reproduction Results

The structural inspection confirms the observation and action specifications across operating modes:

| Observation Component | Feature Dimension (Black-Box) | Feature Dimension (Gray-Box) | Value Range / Domain | Information Leakage Scan | Audit Verification Status |
|---|---|---|---|---|---|
| **Node Telemetry Features** | 4 ($L_{\text{ratio}}, \text{Err}, \text{CPU}, \text{Rep}_{\text{frac}}$) | 4 ($L_{\text{ratio}}, \text{Err}, \text{CPU}, \text{Rep}_{\text{frac}}$) | $[0.0, 100.0]$ | Zero ground-truth leakage | **VERIFIED** |
| **Node Structural Features** | 5 ($\text{deg}_{\text{in}}, \text{deg}_{\text{out}}, \text{layer}, \text{reps}, \text{coloc}$) | 5 ($\text{deg}_{\text{in}}, \text{deg}_{\text{out}}, \text{layer}, \text{reps}, \text{coloc}$) | $[0.0, 1.0]$ | Normalized topology only | **VERIFIED** |
| **Node Exploration History** | 7 ($\text{count}_{\text{tot}}, \text{count}_{0..5}$) | 7 ($\text{count}_{\text{tot}}, \text{count}_{0..5}$) | $\mathbb{Z}_{\ge 0}$ | Internal episode state | **VERIFIED** |
| **Static Resilience Attributes** | 0 (Hidden) | 2 ($\text{Timeout}, \text{CB}_{\text{present}}$) | $[0.0, 1.0]$ | Architecture metadata | **VERIFIED** |
| **Total per-node features ($d$)** | **16 features / node** | **18 features / node** | Structured Vector | Zero labels revealed | **VERIFIED** |
| **Adjacency Matrix** | $N \times N$ matrix | $N \times N$ matrix | $\{0.0, 1.0\}$ | Directed dependency graph | **VERIFIED** |
| **Global Telemetry Features** | 5 scalars ($t_{\text{budget}}, \text{GW}_{p99}, \text{GW}_{\text{err}}, \text{Damage}, \text{Found}$) | 5 scalars ($t_{\text{budget}}, \text{GW}_{p99}, \text{GW}_{\text{err}}, \text{Damage}, \text{Found}$) | Dynamic Scalars | Aggregate telemetry | **VERIFIED** |
| **Discrete Action Catalog** | $18 \times N$ discrete actions | $18 \times N$ discrete actions | Valid integer $\in [0, 18N-1]$ | Mask blocks illegal calls | **VERIFIED** |

*Caption (Table A04-1):*
- **What the reader sees:** Detailed feature layout and dimensionality specifications for both Black-Box and Gray-Box observation modes in ChaosEnv.
- **What it implies:** Telemetry signals scale strictly as $\mathcal{O}(N)$ without leaking planted weakness identities or target service IDs.
- **Traceability link:** Environment class [ChaosEnv](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/env/chaos_env.py#L82-L91), feature constructor [_get_observation](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/env/chaos_env.py#L219-L260), and test [test_audit_s04_environment.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s04_environment.py#L85-L105).

The reward function analysis confirms that $R_2$ successfully enforces damage minimization:

| Reward Variant | Mathematical Definition | Discovery Incentive | Damage Penalty ($w_d$) | Repeat Penalty ($w_r$) | Shaping Signal | Alignment Verdict |
|---|---|---|---|---|---|---|
| **$R_1$ (Sparse)** | $R_1 = \Delta W_{\text{new}}$ | $+1.0$ per new weakness | None ($0.0$) | None ($0.0$) | None | Vulnerable to collateral damage |
| **$R_2$ (Default)** | $R_2 = \Delta W_{\text{new}} - w_d D_{\text{exp}} - w_r \mathbb{I}_{\text{repeat}}$ | $+1.0$ per new weakness | $0.05 \times D_{\text{exp}}$ | $0.02$ per duplicate action | None | **SAFE & ALIGNED (Default)** |
| **$R_3$ (Shaped)** | $R_3 = R_2 + 0.05 \min(1.0, \frac{p99}{500})$ | $+1.0$ per new weakness | $0.05 \times D_{\text{exp}}$ | $0.02$ per duplicate action | Pre-breach latency elevation | Dense exploration guidance |

*Caption (Table A04-2):*
- **What the reader sees:** Mathematical formulation and safety penalty terms across the three evaluated reward functions ($R_1$, $R_2$, $R_3$).
- **What it implies:** Default reward $R_2$ establishes a Pareto frontier by heavily penalizing destructive outages, preventing learned agents from collapsing into destructive brute-force denial-of-service behaviors.
- **Traceability link:** Environment reward logic [chaos_env.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/env/chaos_env.py#L175-L188), adversarial probe [probes.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/env/probes.py#L41-L95), and test [test_audit_s04_environment.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s04_environment.py#L55-L84).

## 5. Negative Controls & Stress Testing

Negative control procedures confirmed the sensitivity of each audit check:
- **Catalog Boundary Control:** Testing whether the action catalog size could be forged to an arbitrary constant (e.g. 500) fails immediately on Scale 100 ($18 \times 100 = 1800$).
- **Synthetic Token Leakage:** Injecting artificial `planted_weaknesses_targets` into metadata dictionaries triggered immediate assertion failure, proving zero-leakage test rigor.
- **Perturbed Reward Calculation:** Adding a $+10.0$ offset to the step return fails the hand-computed reward verification.
- **Feature Dimension Mismatch:** Expecting Black-Box mode to present 18 node features causes strict test failure.
- **NaN Feature Injection:** Inserting an unhandled `NaN` into telemetry causes immediate failure of the numerical stability assertions.

## 6. Discrepancy & Anomaly Analysis

- **Action Masking Design:** The action mask selectively sets `mask[idx] = 0` for container termination on the ingress gateway (service 0). This design decision prevents trivial shutdown of the ingress entrypoint, requiring agents to discover vulnerabilities within interior microservice dependency subgraphs.
- **Repeat Penalty Independence:** The repeat penalty ($w_r = 0.02$) is applied per episode whenever an agent executes a `(service_id, fault_type)` tuple that was previously tested in that episode, encouraging breadth of systematic testing.

## 7. Impact on Downstream Stages & System Safety

By verifying that the state observation space does not leak ground-truth information, we confirm that downstream RL agents in Stage 6 and evaluation benchmarks in Stage 9 cannot learn trivial identity-lookup shortcuts. Policy decisions are driven strictly by observable graph structure and dynamic telemetry.

## 8. Audit Recommendations & Proposed Action Items

1. **Gymnasium Vectorized Env Wrapper:** Implement a lightweight `SyncVectorEnv` wrapper to allow parallel multi-environment stepping for batched training.
2. **Explicit Observation Normalization Bounds:** Clamp all node features into $[0.0, 1.0]$ with an explicit `np.clip` prior to returning observations to ensure zero risk of floating-point overflow.

