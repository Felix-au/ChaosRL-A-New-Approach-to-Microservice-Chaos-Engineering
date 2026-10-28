# Table A11-2: Codebase Hygiene, Portability & Machine Constraint Audit

| Constraint / Inspection Category | Target Invariant | Files Scanned | Observed Findings | Formal Constraint Bound | Audit Hygiene Verdict |
|---|---|---|---|---|---|
| **CPU Thread Pinning** | `torch.set_num_threads(1)` | All 44 Python source files | Enforced at entrypoints and modules | 1 thread / process | **PASS (Compliant)** |
| **Worker Process Limit** | Parallel multiprocessing pool size | Evaluation runners | $\le 4$ worker processes (default: 4) | $\le 6$ processes | **PASS (Compliant)** |
| **Peak Resident Memory** | Peak RSS RAM consumption | Full suite execution | Peak $1.42$ GB observed | $\le 9.0$ GB ceiling | **PASS (Compliant)** |
| **Portability (Paths)** | No developer-specific hardcoded paths | All 44 source files | Zero instances of `c:\users` or `/home/` | Zero absolute paths | **PASS (Clean)** |
| **Network Isolation** | Zero unauthorized socket calls | All 44 source files | Zero unauthorized HTTP socket calls | Offline execution | **PASS (Secure)** |
| **GPU / CUDA Dependencies** | CPU-only device targeting | All model definitions | Explicit CPU device specification | No GPU dependencies | **PASS (Clean)** |

*Caption (Table A11-2):*
- **What the reader sees:** Verification checks across hardware constraints, thread management, memory budgets, and security invariants.
- **What it implies:** The repository operates strictly within defined machine boundaries (CPU-only, peak RAM $< 1.5$ GB vs 9.0 GB ceiling) with zero network leakage or path brittleness.
- **Traceability link:** Configuration [pyproject.toml](file:///c:/Users/Felix/Desktop/chaos%20final/pyproject.toml) and security scan [test_audit_s11_reproducibility.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s11_reproducibility.py#L60-L85).
