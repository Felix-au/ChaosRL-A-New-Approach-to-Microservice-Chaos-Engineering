# ChaosRL Decision & Deviation Log

This ledger documents architectural choices, deviations from default configurations, and rationale for all decisions made autonomously during the research lifecycle.

---

### [D01] 2026-10-28 12:15 UTC — Architecture & Runtime Environment
- **Context:** Target machine has an AMD Ryzen 5 5500U (6 physical cores, 12 threads) with 14 GB RAM and no CUDA GPU. Windows 11 host operating system running Python 3.14.
- **Decision:** Use CPU-only PyTorch with small, lightweight network architectures (MLP, GRU, compact plain-PyTorch GNN < 1M parameters). Restrict PyTorch and OpenMP internal thread pools to 1 thread per worker (`torch.set_num_threads(1)`, `OMP_NUM_THREADS=1`) and bound parallel execution to at most 6 worker processes.
- **Rationale:** Prevents CPU thread oversubscription and memory thrashing, leaving 2 threads and at least 2 GB RAM headroom for the host OS.

---

### [D02] 2026-10-28 12:22 UTC — MSVC Runtime Resolution for PyTorch
- **Context:** Loading `c10.dll` on Windows 11 under Python 3.14 initially failed with `WinError 1114` due to outdated system MSVC runtime DLLs (VS 2019 version 14.24 vs. required VS 2022 version 14.38+).
- **Decision:** Extracted official signed Microsoft Visual C++ 2015-2022 redistributable binaries (`msvcp140.dll`, `vcruntime140*.dll`, `msvcp140_atomic_wait.dll`) and placed them directly inside `torch/lib`.
- **Rationale:** Fully satisfies DLL dependencies without requiring administrative privilege elevation or compromising host security. Verified `torch 2.14.1+cpu` successfully initializes.

---

### [D03] 2026-10-28 12:28 UTC — Windows Smart App Control Handling for Tabular Data
- **Context:** Windows Smart App Control policy blocked `_cyutility.cp314-win_amd64.pyd` from newly installed `pandas 3.1.0`.
- **Decision:** Implemented a robust, native tabular export engine in `chaosrl.docs_tools.figures_tables` using Python's standard `csv` module and `numpy`.
- **Rationale:** Guarantees 100% deterministic, zero-dependency CSV and Markdown table generation across all Windows and POSIX environments without triggering enterprise code integrity blocks.

---

### [D04] 2026-10-28 12:32 UTC — Strict Seed Range Partitioning
- **Context:** Section 3 Integrity Rule 5 requires non-overlapping splits for training, validation, and test systems.
- **Decision:** Enforced three disjoint seed ranges in `configs/seeds.yaml`:
  - Training: `0` to `99,999`
  - Validation: `100,000` to `100,099` (100 systems)
  - Test: `200,000` to `200,199` (200 systems across scales 20, 100, 300, 500 and families L and M)
- **Rationale:** Eliminates data leakage and guarantees generalization testing occurs strictly out-of-distribution.
