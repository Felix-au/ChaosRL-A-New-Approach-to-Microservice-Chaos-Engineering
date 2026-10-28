# Table A04-1: Gymnasium Observation & Action Space Dimensionality Audit

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

