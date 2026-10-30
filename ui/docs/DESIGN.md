# ChaosRL Presentation UI Design System

## 1. Visual Theme & Color Palette

The interface utilizes a modern, dark-first technical aesthetic inspired by high-end developer tools (Linear, Vercel, Grafana) optimized for readability in auditor reviews, conference stages, and executive demos.

### Palette Tokens:
- **Base Background:** `slate-950` (`#0a0f1d`) — Deep obsidian black.
- **Card Surfaces:** `slate-900/60` (`#0f172a` with blur) with `border-slate-800` (`#1e293b`).
- **Brand Primary (TreeRanker / Wins):** `brand-500` (`#22c55e`) — Vibrant emerald green symbolizing success and discovery efficiency.
- **Benchmark Accent (Heuristic Expert):** `amber-400` (`#fbbf24`) — Warm gold highlighting domain expert benchmarks.
- **Baseline Warning (Chaos Monkey):** `rose-500` (`#f43f5e`) — High-visibility rose marking baseline comparisons.
- **Secondary Baseline (Random-All):** `purple-500` (`#a855f7`) — Highlighting unconstrained random exploration.
- **Ensemble Accent (Soft Vote):** `sky-400` (`#38bdf8`) — Crisp cyan for multi-model consensus.

---

## 2. Typography

- **Headings & Interface:** `Inter`, `-apple-system`, `sans-serif` (weights 400, 500, 600, 700, 800).
- **Metrics, Hashes & Code:** `JetBrains Mono`, `Fira Code`, `monospace` for tabular data, confidence intervals, p-values, and hashes.

---

## 3. Interactive Motion & Feedback

- **Transitions:** Smooth 200ms cubic-bezier transitions for card hovers, button clicks, and modal appearances.
- **Confetti Celebration:** Canvas-confetti triggered upon completing the guided tour.
- **Chart Crosshairs:** Synchronized ECharts tooltips with high-contrast badge styling.
- **Accessible Data Tables:** Every chart includes a toggle to view the raw data table for accessibility.

