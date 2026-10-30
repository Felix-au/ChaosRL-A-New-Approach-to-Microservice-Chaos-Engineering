# ChaosRL UI Architecture Specification

## 1. Overview & Core Philosophy

The ChaosRL presentation layer is built as an autonomous, high-performance, browser-facing web application that brings the entire ChaosRL research repository to life.

### Key Architectural Tenets:
1. **Total Isolation in `ui/`:** Zero files outside `ui/` are modified or created.
2. **Absolute Grounding (No Hand-Typed Numbers):** Every metric, p-value, and table cell originates from repository datasets via `ui/scripts/build_data.py`.
3. **Dual-Run Provenance:** Supports both the pre-audit original cohort ($n=10$) and the post-audit extended cohort ($n=30$) via an instant header switcher.
4. **Pure Dynamic Insight Engine:** Highlighting and narrative summaries are computed at runtime from raw rows rather than hardcoded string templates.

---

## 2. Component Hierarchy & Data Flow

```
                      +-----------------------------+
                      |   build_data.py (Python)    |
                      |  Pulls results/, audit/,    |
                      |  figures/, docs/, facts.json|
                      +--------------+--------------+
                                     |
                                     v
                        ui/public/data/*.json
                        ui/public/figures/*
                        ui/public/docs/*
                                     |
                                     v
                        +---------------------------+
                        |   useChaosData (React)    |
                        | Caches & manages dataset  |
                        | switcher (post vs pre)    |
                        +-------------+-------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
|  InsightEngine   |         |    ECharts &     |         | MarkdownRenderer |
| Evaluates rules, |         |  TanStack Table  |         | KaTeX, Mermaid,  |
| ratios, p-values |         |  Area CI bands,  |         | GitHub alerts,   |
| & damage context |         |  CSV export, sort|         | copy code blocks |
+------------------+         +------------------+         +------------------+
         |                            |                            |
         +----------------------------+----------------------------+
                                      |
                                      v
                             +------------------+
                             |     AppShell     |
                             |  10 Tab Panes,   |
                             |  Command Palette,|
                             |  Presentation &  |
                             |   Guided Tour    |
                             +------------------+
```

---

## 3. The 10 Interactive Tabs

1. **Overview Tab (`OverviewTab.tsx`):**
   - High-level pitch and core problem visualization.
   - Interactive Failure-Cascade Simulator demonstrating multi-tier cascading timeouts.
   - 7-stage research architecture pipeline.
2. **Approach Tab (`ApproachTab.tsx`):**
   - Empirical trace calibration on Sock-Shop and Train-Ticket traces.
   - 12,000 steps/sec Gymnasium vector environment.
   - Multi-fault action space (4 dimensions) vs. Chaos Monkey's 1-fault limitation.
3. **Methods Tab (`MethodsTab.tsx`):**
   - 15 evaluated algorithms across 5 paradigms.
   - Top-5 Pareto-optimal selection and cryptographic SHA-256 freeze manifest.
   - Interactive parameter and hyperparameter inspection drawer.
4. **Results Tab (`ResultsTab.tsx`):**
   - Dynamic headline wins strip (AUDC $+138\%$, $7.0\times$ low-budget speedup, $53.3\times$ safety).
   - Continuous discovery curve explorer with 95% bootstrap confidence bands and step hover crosshairs.
   - Full scale-100 benchmark leaderboard powered by TanStack Table.
   - Rigorous statistical hypothesis testing table ($p = 0.0037$, Cohen's $d = 0.703$, power = $96.1\%$).
5. **Efficiency & Generalization Tab (`EfficiencyTab.tsx`):**
   - Budget sweep ($B=25$ to $B=200$) demonstrating $7.0\times$ faster low-budget vulnerability exposure.
   - Multi-scale system scaling ($N=20$ to $N=500$) showing small-scale $N=20$ advantage and hyper-scale robustness.
   - Family M service mesh zero-shot transfer evaluation.
6. **Safety & Cost Tab (`SafetyTab.tsx`):**
   - Damage metric asymmetry contextualization explaining why Chaos Monkey's damage is artificially low.
   - Discovery vs. collateral damage Pareto frontier scatter chart.
   - Compute economics, training durations, and inference latencies.
7. **Original vs. Audited Tab (`OriginalVsAuditedTab.tsx`):**
   - Side-by-side reconciliation of pre-audit ($n=10$) vs post-audit ($n=30$).
   - Statistical power leap from $33.6\%$ ($p=0.121$) to $96.1\%$ ($p=0.0037$).
8. **Insights Tab (`InsightsTab.tsx`):**
   - Deep dive: Why did tabular trees beat deep reinforcement learning in microservice graphs?
   - Permutation feature importance analysis showing topological centrality dominance ($67.5\%$).
   - Stage 9 feature and reward function ablations.
9. **Rigor & Reproducibility Tab (`RigorTab.tsx`):**
   - Animated rigor metrics: 104 passing tests, 1,240 test access audit entries, 0 data leakage violations, 72 verified claims.
   - Cryptographic freeze manifest and test-access separation log.
   - Copyable CLI reproduction commands.
10. **Docs Tab (`DocsTab.tsx`):**
    - Searchable markdown document library with categorized tree sidebar.
    - Full reading pane with math (KaTeX) and diagram (Mermaid) support.
    - Instant markdown file download.

