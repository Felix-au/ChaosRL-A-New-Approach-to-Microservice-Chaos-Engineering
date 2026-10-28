# Table A03-2: Simulator Throughput & Scalability Benchmark Audit

| System Scale ($N$ services) | Documented Throughput (exp/min) | Audit Measured Throughput (exp/min) | Audit Measured Tick Rate (steps/sec) | Average Latency per Step (ms) | Scaling Order vs. Scale 20 | Audit Performance Status |
|---|---|---|---|---|---|---|
| **$N=20$** | 22,912.7 | 23,410.5 | 2,834.6 | 0.353 ms | $1.00\times$ (Baseline) | **PASS (Exceeds Spec)** |
| **$N=50$** | 12,450.0 | 12,180.2 | 1,479.7 | 0.676 ms | $1.92\times$ cost | **PASS (Consistent)** |
| **$N=100$** | 7,914.4 | 8,052.1 | 773.6 | 1.293 ms | $3.66\times$ cost | **PASS (Exceeds Spec)** |
| **$N=300$** | 2,479.7 | 2,544.8 | 261.8 | 3.820 ms | $10.82\times$ cost | **PASS (Exceeds Spec)** |

*Caption (Table A03-2):*
- **What the reader sees:** Simulator execution speed across microservice topologies spanning 20 to 300 nodes, comparing original documented throughput against independent audit benchmarks.
- **What it implies:** Vectorized NumPy propagation scales near-linearly ($\mathcal{O}(N)$ to $\mathcal{O}(N^{1.1})$), executing over 770 simulation steps per second even on 100-node microservice clusters on single-thread CPU.
- **Traceability link:** Original metrics in [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json), benchmark routine [benchmark_engine_throughput](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/simulator/engine.py#L102-L122), and audit test [test_audit_s03_simulator.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s03_simulator.py#L190-L225).

