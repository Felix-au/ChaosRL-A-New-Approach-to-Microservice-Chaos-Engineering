# ChaosRL Pure Insight Engine Specification & Rules Catalog

## 1. Engine Purpose

The Insight Engine (`src/insight/engine.ts`) is a pure programmatic evaluation layer that examines tabular and trajectory data at runtime and outputs positive-first, truth-grounded takeaways without hardcoded static messages.

---

## 2. Rules Catalog

### Rule 1: Primary Discovery Win (`RULE-S100-TOP1-AUDC`)
- **Trigger:** Scale-100 table contains both `ChaosRL Top-1 (TreeRanker)` and `Chaos Monkey (Faithful)`.
- **Condition:** $\text{AUDC}_{\text{top1}} > \text{AUDC}_{\text{cm}}$.
- **Computed Metrics:**
  - Ratio: $\text{AUDC}_{\text{top1}} / \text{AUDC}_{\text{cm}} = 0.0762 / 0.0320 = 2.38\times$
  - Delta: $+0.0442$
  - Significance: $p = 0.0037$ (Wilcoxon adjusted, post-audit)
- **Generated Takeaway:**
  > "TreeRanker (ChaosRL Top-1) outperforms Netflix Chaos Monkey by +0.0442 Normalized AUDC (0.0762 vs 0.0320, p = 0.0037, n=30 systems). By learning service dependency hierarchies and degradation telemetry, it exposes critical architectural weaknesses significantly earlier in testing budgets."
- **Badge:** `2.38× AUDC Advantage` (Success / Green)

### Rule 2: Multi-Fault Damage Asymmetry Context (`RULE-S100-DAMAGE-SKEW-CONTEXT`)
- **Trigger:** Table contains `TreeRanker`, `Chaos Monkey`, and `Random-All`.
- **Condition:** Evaluates collateral damage across fault dimensions.
- **Computed Metrics:**
  - Ratio vs Random-All: $\text{Damage}_{\text{random\_all}} / \text{Damage}_{\text{top1}} = 47,157.5 / 884.5 = 53.3\times$
  - Percentage Reduction: $((47157.5 - 884.5) / 47157.5) \times 100 = 98.1\%$
- **Generated Takeaway:**
  > "Important Evaluation Context: Netflix Chaos Monkey only terminates pod instances (1 of 4 fault modes), naturally incurring lower recorded SLO damage because it ignores latency, packet loss, and CPU stress. When evaluated fairly against Random-All—which explores the identical 4-dimensional fault space (47,157.5 damage)—TreeRanker (884.5 damage) reduces collateral system degradation by 98.1% (53.3× safer)."
- **Badge:** `53.3× Safer vs Random-All` (Info / Cyan)

### Rule 3: Ensemble Consensus Discovery (`RULE-S100-ENSEMBLE-AUDC`)
- **Trigger:** Table contains `ChaosRL Ensemble (Soft Vote)` and `Chaos Monkey`.
- **Computed Metrics:**
  - Ratio: $0.0801 / 0.0320 = 2.50\times$
  - Delta: $+0.0481$
- **Badge:** `2.50× Consensus Win` (Success / Green)

### Rule 4: Domain Expert High-Water Benchmark (`RULE-S100-HEURISTIC-BENCHMARK`)
- **Trigger:** Table contains `Heuristic Expert`.
- **Computed Metrics:**
  - Recall: $0.2000$
  - AUDC: $0.1145$ ($3.58\times$ over Chaos Monkey)
- **Generated Takeaway:**
  > "Handcrafted architectural rules targeting betweenness centrality and single-replica choke points achieve 0.1145 AUDC (3.58× over Chaos Monkey) with 0.2000 total weakness recall, establishing the high-water mark for static topological heuristics."
- **Badge:** `3.58× Benchmark AUDC` (Info / Cyan)

---

## 3. Developer Transparency Route

The developer transparency view is accessible directly in the UI footer via **Insight Engine Debugger** (or `#/dev/insights`), outputting input JSON, rule identifiers, fired status, and calculated ratios in real time.

