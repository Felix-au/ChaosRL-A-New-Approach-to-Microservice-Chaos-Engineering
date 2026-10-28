# Table A10-2: Empirical Failure Mode Taxonomy & Systems Root Cause Analysis

| Failure Mode Identifier | Manifestation in Simulator | Affected Algorithmic Families | Underlying Systems Root Cause | Empirical Severity on Scale 100 | Mitigation / Proposed Remedy |
|---|---|---|---|---|---|
| **FM1: Decoy Distraction** | Policies repeatedly probe fortified single-replica leaf services that absorb faults without violating SLO | Tabular heuristics, PPO-MLP (C01), LinUCB (C11) | High local structural prominence (e.g. low replica count) without downstream critical-path impact | High ($\approx 35\%$ of wasted experiments) | Contrastive loss weighting against non-critical leaf nodes |
| **FM2: Upstream Cascading Blindness** | Injecting an early upstream failure trips circuit breakers, preventing observation of deeper latent bugs | High-intensity policies (Chaos Monkey-2, Random-All) | Circuit breaker isolation sheds traffic, masking downstream timeout vulnerabilities | Critical (causes $> 150\text{k}$ collateral damage) | Introduce sequential low-intensity fault ramping before node kill |
| **FM3: Action Space Dilution** | Flat action exploration is overwhelmed as catalog expands ($18N$ actions: 360 at $N=20 \to 9,000$ at $N=500$) | Flat value-based RL (C05 DQN), ES (C10) | Exponential combinatorial explosion of valid action space dilutes policy gradient signals | Severe at $N \ge 300$ ($N=500$ AUDC dropped to $0.0007$) | Hierarchical two-tier policy: select target service $u$, then select fault modality |
| **FM4: Conservative Under-Injection** | RL policies avoid multi-fault compound injections due to risk-averse damage penalty $w_d$ | Safety-penalized PPO (C01, C04) | Default $R_2$ penalty dominates sparse compound discovery bonus ($+1.0$ vs $-0.05 \times \text{Damage}$) | Moderate (Zero compound weaknesses found by Top-1) | Dynamic curiosity shaping bonus for multi-target exploration |

*Caption (Table A10-2):*
- **What the reader sees:** Taxonomy of four empirical failure modes observed during test evaluations, detailing manifestation, affected families, root causes, and mitigations.
- **What it implies:** Performance degradation at large scales ($N=500$) and compound weakness blindness stem from action space dilution and reward-risk trade-offs rather than software bugs.
- **Traceability link:** Failure mode analysis in [section10_analysis_limitations.md](file:///c:/Users/Felix/Desktop/chaos%20final/docs/section10_analysis_limitations.md#L14-L20) and audit test [test_audit_s10_analysis.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s10_analysis.py#L48-L70).

