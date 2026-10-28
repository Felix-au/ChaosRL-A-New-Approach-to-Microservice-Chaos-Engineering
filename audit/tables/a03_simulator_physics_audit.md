# Table A03-1: Discrete-Event Simulator Invariants & Physical Integrity

| Physical Law / Invariant | Verification Procedure | Evaluated Sample Size | Observed Value / Range | Formal Bound | Audit Verification Verdict |
|---|---|---|---|---|---|
| **Steady-State False Alarms** | Unperturbed baseline simulation | 50 seeds ($N=20$) | 0.000 (0 / 50 breaches) | $\le 0.02$ (2% threshold) | **PASS (100% compliant)** |
| **Ingress Load Monotonicity** | Ingress step ($50 \to 200$ RPS) | Microservice $N=20$ | $+63.4$ ms latency spike | $\Delta \text{Latency} \ge 0$ | **PASS (Monotonic)** |
| **Fault Rollback Fidelity** | 15 recovery ticks post-fault | $N=25$ (Container Kill) | All replicas restored, CBs closed | $\Delta_{\text{state}} == 0$ | **PASS (Exact Restoration)** |
| **Physical Conservation Bounds** | 100 consecutive step ticks | $N=30$ services | Utilization $[0.0, 98.4\%]$, Err $[0, 1]$ | $[0.0, 1.0]$, finite | **PASS (Finite & Bounded)** |
| **Micro-System Reachability** | Brute-force targeted faults | $N=6$ (4 planted weaknesses) | 4 / 4 discovered (100%) | Recall $== 1.0$ | **PASS (Zero Unreachable)** |
| **Seed Determinism** | Seed 12345 execution twin | Two independent engines | $\Delta \text{Damage} == 0.0$, $\Delta \text{p99} == 0.0$ | Bit-for-bit identical | **PASS (Deterministic)** |

*Caption (Table A03-1):*
- **What the reader sees:** Verification results across six fundamental physical invariants of the discrete-time simulator engine.
- **What it implies:** The simulation environment satisfies physical conservation laws, zero unprovoked steady-state false alarms, and 100% reachability of planted faults.
- **Traceability link:** Code paths [engine.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/simulator/engine.py#L24-L60), [dynamics.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/simulator/dynamics.py#L66-L113), and test suite [test_audit_s03_simulator.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s03_simulator.py#L25-L160).
