# Audit Decision Log

This log records every architectural, methodological, and scoping decision made autonomously during the independent verification and research audit.

| Decision ID | Date/Time | Category | Ambiguity / Context | Decision Taken | Rationale & Justification |
|---|---|---|---|---|---|
| AUD-D01 | 2026-10-29T01:20:00+05:30 | Setup | Preservation Scope | Preserve full `results/` and `docs/` trees with SHA-256 manifest in `results/original_run/` | Ensures zero loss of original research artifacts and cryptographic audit trail before running tests |
| AUD-D02 | 2026-10-29T01:20:00+05:30 | Methodology | Test Isolation | Write all audit-generated test code into `tests/audit/` with `@pytest.mark.audit` | Prevents polluting existing unit tests while making audit tests permanent and regression-verifiable |
| AUD-D03 | 2026-10-29T01:20:00+05:30 | Evaluation | Sizing for Extended Test | Measure single-episode latency across scales to calibrate feasible sample size | Guarantees test evaluation fits strictly within the P5 time allocation without violating machine memory constraints |

