# Table A04-2: Reward Function Formulation & Safety Invariant Audit

| Reward Variant | Mathematical Definition | Discovery Incentive | Damage Penalty ($w_d$) | Repeat Penalty ($w_r$) | Shaping Signal | Alignment Verdict |
|---|---|---|---|---|---|---|
| **$R_1$ (Sparse)** | $R_1 = \Delta W_{\text{new}}$ | $+1.0$ per new weakness | None ($0.0$) | None ($0.0$) | None | Vulnerable to collateral damage |
| **$R_2$ (Default)** | $R_2 = \Delta W_{\text{new}} - w_d D_{\text{exp}} - w_r \mathbb{I}_{\text{repeat}}$ | $+1.0$ per new weakness | $0.05 \times D_{\text{exp}}$ | $0.02$ per duplicate action | None | **SAFE & ALIGNED (Default)** |
| **$R_3$ (Shaped)** | $R_3 = R_2 + 0.05 \min(1.0, \frac{p99}{500})$ | $+1.0$ per new weakness | $0.05 \times D_{\text{exp}}$ | $0.02$ per duplicate action | Pre-breach latency elevation | Dense exploration guidance |

*Caption (Table A04-2):*
- **What the reader sees:** Mathematical formulation and safety penalty terms across the three evaluated reward functions ($R_1$, $R_2$, $R_3$).
- **What it implies:** Default reward $R_2$ establishes a Pareto frontier by heavily penalizing destructive outages, preventing learned agents from collapsing into destructive brute-force denial-of-service behaviors.
- **Traceability link:** Environment reward logic [chaos_env.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/env/chaos_env.py#L175-L188), adversarial probe [probes.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/env/probes.py#L41-L95), and test [test_audit_s04_environment.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s04_environment.py#L55-L84).
