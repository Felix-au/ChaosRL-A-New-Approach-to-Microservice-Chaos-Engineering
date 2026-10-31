# ChaosRL UI Automated Test Suite

## 1. Test Architecture

The UI test suite is automated via Vitest and Testing Library, guaranteeing zero regressions across data loading, mathematical calculations, and markdown rendering.

```
ui/tests/
  ├── data_integrity.test.ts          # Verifies public/data/*.json against facts.json
  ├── markdown_rendering.test.ts      # Tests KaTeX, Mermaid, tables, GitHub alerts
  └── fixtures/
      └── kitchen-sink.md             # Multi-syntax markdown fixture
ui/src/insight/__tests__/
  └── insight.test.ts                 # Tests InsightEngine rules, ratios, and metrics
```

---

## 2. Executed Test Suites & Results

All 12 automated unit and integration tests execute in <4 seconds:

1. **`src/insight/__tests__/insight.test.ts` (6 tests):**
   - Correct formatting of AUDC, Recall, Damage, p-values.
   - Preserves metric optimization directions (AUDC/Recall higher is better, Damage lower is better).
   - Method role categorization (learned, baseline, ensemble, expert, oracle).
   - Generates primary AUDC win rule for TreeRanker ($2.38\times$, $p=0.0037$, $n=30$).
   - Generates damage asymmetry context rule ($53.3\times$ safer than Random-All).

2. **`tests/data_integrity.test.ts` (5 tests):**
   - Verifies all 10 JSON data files exist in `ui/public/data/` and parse cleanly.
   - Matches `post_audit.json` numbers against `results/facts.json` ground truth.
   - Confirms `pre_audit.json` ($n=10$) has non-empty rows.
   - Validates `curves.json` contains step-by-step means and non-inverted confidence intervals ($\text{ci\_low} \le \text{mean} \le \text{ci\_high}$).
   - Ensures `docs_index.json` contains indexed sections with valid search snippets.

3. **`tests/markdown_rendering.test.ts` (1 test):**
   - Renders `kitchen-sink.md` containing KaTeX formulas, GitHub alerts (`[!NOTE]`, `[!WARNING]`, `[!IMPORTANT]`), code blocks, tables, and Mermaid diagram containers without throwing exceptions.

---

## 3. Running the Tests

```bash
cd ui
npm test
```

