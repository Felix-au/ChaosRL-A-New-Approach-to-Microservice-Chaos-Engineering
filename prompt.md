You are a senior ML and systems engineer working **autonomously**. Build, train, and rigorously evaluate a research project called **ChaosRL** from scratch in this empty repository. This document is your complete specification. Read all of it before writing code. Then execute every stage in order without waiting for the user. You evaluate your own work (section 5), you document every stage the moment it is finished (section 6), and you do not finish until the acceptance checklist (section 24) passes.

## 0. How to read this document

- Sections 1 to 4: background, goals, rules, and machine constraints.
- Section 5: the **self-evaluation protocol** (replaces any human approval step).
- Section 6: the **mandatory documentation system**. This is as important as the code.
- Sections 7 to 10: working standards that apply to every stage.
- Sections 11 to 20: the technical stages, in execution order.
- Sections 21 to 25: optional stage, orchestration, acceptance checklist, anti-patterns, and the final summary.

When two rules seem to conflict, the order of priority is: **integrity rules (section 3) > documentation rules (section 6) > self-evaluation rules (section 5) > everything else.**

## 1. Background (read this first)

- **Microservices:** an application split into many small services that call each other (for example gateway → orders → payments → database). Calls form a dependency graph. A failure in one service can spread to others.
- **SLO (service level objective):** a measurable health target for the whole system, for example "gateway p99 latency under 500 ms and error rate under 2%". A system meeting its SLO is in "steady state".
- **Chaos engineering:** deliberately injecting failures (kill a server, add network delay, exhaust CPU) to find weaknesses before real outages do.
- **Chaos Monkey (Netflix):** a tool that **randomly terminates** service instances. It has no memory and no strategy, and it only kills things (no latency, packet loss, or resource faults).
- **Weakness:** a way the system violates its SLO under some fault or combination of faults, for example a single-replica service on the critical path, a missing timeout, a retry storm, or no circuit breaker.
- **Reinforcement learning (RL):** an *agent* repeatedly observes a *state*, picks an *action*, and receives a *reward*, learning a *policy* that maximizes total reward. Here the agent plays "smart chaos engineer".
- **Project idea (ChaosRL):** replace Chaos Monkey's random choice with a **learned policy** that decides *which fault to inject into which service next*, so that more weaknesses are found with fewer, gentler experiments.

**Phase 2 goal:** build a **realistic, data-calibrated simulator**, then train a **pool of many different Chaos Monkey agents** (different RL algorithms and training methods, plus non-RL learned methods), select the **best 5**, build **ensembles** of those 5, and compare everything against classic baselines using rigorous statistics. Real Docker evaluation is an **optional stretch** (section 21), off by default.

## 2. Research questions and hypotheses

- **RQ1:** Do learned agents discover more planted weaknesses per experiment, with less damage, than Chaos Monkey-style random injection and other non-learned baselines?
- **RQ2:** Which training approach works best (policy-gradient, value-based, structure-aware, gradient-free, supervised/bandit)?
- **RQ3:** Does an ensemble of the top 5 beat the best single agent?
- **RQ4:** Do agents trained on small and medium systems generalize to **larger, unseen** systems and to a **different topology family**?

Write a falsifiable hypothesis for each question in `docs/section01_design.md` **before running any experiment**, and record the date/time. Hypotheses may turn out wrong. Reporting that is fine and expected.

## 3. Integrity rules (non-negotiable; these override everything else)

1. **Never fabricate, hardcode, round up, or "illustrate" results or data.** Every number in every table, plot, doc, and report must come from code that actually ran and must be traceable to a file in `results/`.
2. **Real data must be real.** Calibration data is downloaded from public sources. If every retrieval method fails, **do not invent substitute data.** Instead, fall back to clearly labeled **UNCALIBRATED** default parameters, mark every affected result and every document with that label, and explain why.
3. **Report negative results honestly**, including every case where ChaosRL loses to or ties with a baseline.
4. **Fair comparison:** identical systems, seeds, and experiment budgets for all methods. Baselines get tuning effort comparable to learned agents.
5. **Strict data splits:** training, validation, and test systems come from disjoint seed ranges (section 15). Tune only on validation. The **test set is run exactly once**, after the freeze (section 5.6 describes the lock).
6. **Report all candidates**, not only winners, to show there was no cherry-picking.
7. **No hidden-information leaks.** The planted weaknesses must never appear in any observation, feature, reward-shaping term visible to the agent, or ensemble input. Tests must enforce this.
8. **No silent failures.** Every error, skipped step, reduced scope, and workaround is logged in `docs/decision_log.md` and surfaced in the relevant section doc and in `docs/OVERALL.md`.
9. **Disclose reruns.** If a bug forces a rerun of anything evaluated on the test set, keep the old results, label them, and disclose both.
10. **Documentation numbers come from code**, never from memory (section 6.5).

## 4. Machine constraints and execution rules

The target machine is a laptop: **AMD Ryzen 5 5500U (6 cores / 12 threads), 16 GB RAM with about 10 GB free for experiments, no CUDA GPU.** It is used exclusively for this project.

- **CPU-only PyTorch.** Use small networks (MLP, GRU, small graph network; at most about 1M parameters).
- Detect the OS at start. It may be Windows. Provide a cross-platform CLI (`python -m chaosrl <command>`) as the main interface and a `Makefile` only as a convenience. On Windows, multiprocessing uses `spawn`, so all worker code must be importable and guarded with `if __name__ == "__main__":`. Use `pathlib` for all paths. Avoid shell-specific commands in code. Use UTF-8 for all files.
- **Parallelism:** at most **6 worker processes**, each with `torch.set_num_threads(1)` and `OMP_NUM_THREADS=1`. Leave 2 threads free for the OS.
- **Memory:** keep total usage under about **9 GB**. Monitor with `psutil`. If free RAM falls below 2 GB, pause new workers and reduce parallelism automatically. Log this event.
- Run long jobs as **background processes** with log files, **checkpoint regularly, and support automatic resume** (the laptop may sleep, throttle, or restart). Write a `results/heartbeat.json` every minute (stage, progress, ETA, memory). Provide `python -m chaosrl resume` that continues from the last completed unit of work.
- Provide a `--quick` mode for every stage (tiny scale, finishes in minutes). Use it for tests and smoke runs. Never report `--quick` numbers as final results.
- Pin every dependency version. Record versions, OS, CPU, RAM, and Python version in `results/run_metadata.json`.
- Add a note at the top of `README.md` telling the user to plug in the charger and disable sleep for long runs.

## 5. Self-evaluation protocol (replaces user approval gates)

You do not wait for the user. After finishing each stage you perform a **stage self-evaluation** and write the result to `docs/self_evaluations/S<NN>_<stage>.md`. A stage is only "complete" when it earns a **PASS** verdict under this protocol and its section doc exists (section 6).

### 5.1 The seven-step self-evaluation routine (run at the end of every stage)

1. **Automated checks:** run the stage's unit tests and its `python -m chaosrl check --stage <n>` command (you implement this command: it runs the stage's exit criteria as code and prints PASS/FAIL per criterion).
2. **Independent recomputation:** pick at least 3 key numbers the stage produced and recompute them a different way (for example recompute a metric from the raw logs in a separate small script, not from the same function). Differences beyond numerical tolerance mean a bug. Record both values.
3. **Invariant checks:** run the sanity invariants for the stage (listed in each stage below and in 5.4).
4. **Adversarial review:** write a list of at least 5 ways the stage could be **wrong, leaky, unfair, or misleading**, then actually test each one where feasible. Examples: Is the baseline unfairly weak? Could the agent see hidden information? Is a seed shared across splits? Is the metric gameable? Does the plot hide variance?
5. **Visual inspection:** open every figure the stage produced and check labels, units, legends, confidence bands, color distinguishability, and that the plot tells the truth. Fix any that mislead.
6. **Documentation check:** run `python -m chaosrl docs-check --section <n>` (section 6.6). It must pass.
7. **Verdict:** write the evaluation record (template in 5.2) with a verdict.

### 5.2 Evaluation record template (`docs/self_evaluations/S<NN>_<stage>.md`)

```
# Self-evaluation: Stage <NN> <name>
- Date/time, git commit hash, config hash
- Exit criteria: table of criterion | result (PASS/FAIL) | evidence (file or number)
- Independent recomputation: table of quantity | primary value | recomputed value | match?
- Invariants checked: list with results
- Adversarial review: table of risk | how tested | outcome | action taken
- Figures inspected: list with notes and fixes
- Issues found and fixed: list
- Issues remaining (accepted limitations): list
- Verdict: PASS | PASS-WITH-ISSUES | FAIL
- Iteration number (1 to 3)
```

### 5.3 Verdict rules and the fix loop

- **PASS:** all exit criteria pass, all invariants hold, recomputations match, no unresolved critical risk.
- **PASS-WITH-ISSUES:** non-critical issues remain. Each is documented as a limitation in the section doc and in `docs/OVERALL.md`.
- **FAIL:** any exit criterion fails, any invariant is violated, or a recomputation mismatches.
- On FAIL: diagnose, fix, and re-run the self-evaluation. Allow up to **3 iterations per stage**.
- If a stage still FAILs after 3 iterations, apply the stage's documented **fallback** (listed per stage), label every downstream result accordingly, record the situation in `docs/decision_log.md`, and continue. Never loop forever and never skip silently.
- Never ask the user a question during the run. When facing ambiguity, choose the most defensible option, write the decision and its reasoning in `docs/decision_log.md`, and proceed.

### 5.4 Global sanity invariants (checked at the relevant stages)

- A fault-free system meets its SLO in 100% of seeds, apart from the configured noise-driven false alarm rate (report it).
- The **oracle** is never worse than any non-oracle method on the same systems and budget.
- **Chaos Monkey (faithful)** can only ever find weaknesses whose trigger is a container kill.
- With the same seed, the simulator and every deterministic agent produce byte-identical logs.
- Increasing the experiment budget never decreases the weaknesses found (per method, per system).
- Round-robin finds every kill-type or single-fault weakness given a large enough budget.
- A trained agent that is given **shuffled** observations (destroyed information) performs no better than random. If it does, the agent learned something other than state-based reasoning, and you must investigate.
- Metrics computed from raw logs match metrics reported in tables.

### 5.5 Automated tuning loop (replaces the "ask the user to approve parameter changes" step)

After each training round, evaluate every candidate on **validation systems only**, then decide automatically:

1. Rank candidates by validation score (section 16.3).
2. For each candidate whose performance is below a defined threshold (below the median of its family, or showing training instability such as exploding loss, entropy collapse, or no improvement over its first quarter), propose a parameter change from a pre-written **tuning playbook** (section 16.4).
3. Apply the change only to the underperforming candidates, retrain, and re-evaluate on validation.
4. Accept a change only if the validation score improves by **more than one standard error across training seeds**. Otherwise revert.
5. **Maximum 3 tuning rounds.** Stop early if no candidate improves.
6. Log every proposed change, reason, and outcome in `results/tuning_log.csv`, and summarize in the training section doc.

### 5.6 Test-set lock

- The test seeds are locked in code. Any function that builds a test system raises an error unless the environment variable `CHAOSRL_FINAL_TEST=1` is set. Only the `final-eval` command sets it.
- The lock writes every test-set access to `results/test_access_log.csv` (timestamp, command, git commit). Before the final evaluation, this file must be empty (checked automatically). Any later access is disclosed in the report.
- The final evaluation runs only after the **freeze** (section 17.3): model checkpoints are hashed (SHA-256) into `results/frozen_manifest.json`, and the final evaluation refuses to run if any checkpoint hash differs.

### 5.7 Scope selection without a human

Read `configs/budget.yaml` at the start (create it with the defaults below if missing):

```yaml
total_wallclock_hours: 36        # hard budget for all runs combined (user may edit)
scope: auto                      # auto | minimum | full
run_docker_validation: false     # optional stretch, see section 21
download_limit_gb: 3             # largest single download allowed without fallback
```

With `scope: auto`, measure simulator throughput and per-candidate training speed during Stage 2 and Stage 5 smoke runs, project the total time for the Full scope, and choose **Full** if the projection is at most 80% of `total_wallclock_hours`; otherwise choose **Minimum** (candidates C01, C04, C05, C11, 3 training seeds, top-3 ensemble). Record the projection and the choice in `docs/decision_log.md`. Re-check the projection after each training round; if the remaining budget is too small, shrink the remaining plan in the documented order: fewer evaluation scales, then fewer seeds, then fewer candidates. Never exceed the budget.

## 6. Mandatory documentation system

**This is mandatory. The project is not complete without it.** Documentation is written **as each section is implemented**, not at the end. A stage is not complete, and you must not begin the next stage, until its section doc exists and passes `docs-check`.

### 6.1 Required folder layout

```
docs/
  INDEX.md                      # table of contents linking every doc, with one-line descriptions
  OVERALL.md                    # the extensive overall documentation (section 6.4)
  FACTS.md                      # auto-generated table of every key number (section 6.5)
  decision_log.md               # every decision, deviation, fallback, with date and reason
  PROGRESS.md                   # running log of stage start/end times and status
  section01_design.md
  section02_data_calibration.md
  section03_simulator.md
  section04_environment.md
  section05_baselines.md
  section06_candidates.md
  section07_training.md
  section08_selection_ensembles.md
  section09_final_evaluation.md
  section10_analysis_limitations.md
  section11_reproducibility.md
  section12_docker_validation.md   # only if the optional stage runs
  ASSUMPTIONS.md                # every simulator assumption and its realism limits
  EXPLAINER.md                  # plain-language explanation for every team member
  QA.md                         # likely examiner questions with answers from real results
  PRESENTATION_OUTLINE.md       # 8 to 10 slides: which figures and tables to show
  GLOSSARY.md                   # every term used in the project
  self_evaluations/             # one record per stage (section 5.2)
  figures/                      # all figures (PNG and SVG) used by the docs
  tables/                       # all tables as CSV and Markdown
```

The numbering of the section docs matches the stage numbering in sections 11 to 20 below (Stage 1 → `section01_design.md`, and so on). Use exactly these filenames.

### 6.2 What every section doc must contain (mandatory headings, in this order)

1. **Purpose:** what this section is for and how it connects to the research questions.
2. **What was implemented:** components, modules, files (with paths), and how they fit together. Include a diagram (Mermaid source plus a rendered PNG if possible).
3. **Design decisions and rationale:** each important choice, the alternatives considered, and why this one was chosen. Link to entries in `decision_log.md`.
4. **Key facts and figures:** a table of the important numbers produced in this section (counts, sizes, throughput, runtimes, scores), each with its source file in `results/`. Embed at least **2 figures** (or 1 figure and 2 tables) with captions.
5. **Figure captions:** for every figure, a caption with three parts: *what it shows*, *how to read it*, *the takeaway*.
6. **How to reproduce:** the exact commands, config files, and seeds for this section.
7. **Tests and verification:** which tests cover this section, which invariants were checked, and the result of the stage self-evaluation (link to `self_evaluations/`).
8. **Problems encountered and fixes:** honest account of what broke and how it was resolved.
9. **Limitations and assumptions specific to this section.**
10. **What the next section depends on:** the interfaces, files, or numbers handed forward.

Each section doc must be **at least 600 words of substantive prose plus its tables and figures** (not padding), written so a reader who has not seen the code can understand what happened. Use plain language first, technical detail second.

### 6.3 Timing rules

- Create the section doc as a **skeleton when the stage starts** (headings only), update it **as you go**, and finalize it **before the stage self-evaluation**.
- Update `docs/PROGRESS.md` at the start and end of every stage (timestamps, status, key numbers).
- Update `docs/INDEX.md` whenever a doc is added.
- Add a `docs/decision_log.md` entry every time you make a non-trivial choice or deviate from this prompt.

### 6.4 The overall documentation (`docs/OVERALL.md`) mandatory contents

This is the extensive, standalone summary of the entire project. It must be built incrementally (append the relevant part after each stage) and fully reviewed at the end. Required parts, in order:

1. **Executive summary** (one page): the problem, the approach, the headline results with numbers, and the honest limitations.
2. **Project at a glance:** a facts table (number of services simulated, scales, topology families, fault types, planted weakness counts, candidate count, seeds, experiments run, total compute hours, lines of code, test count, test pass rate).
3. **System architecture:** a diagram of all components and data flow, with a paragraph per component.
4. **Data and calibration summary:** sources, sizes, what was fitted, before/after fit figures, and what calibration does and does not establish.
5. **Simulator summary:** model description, equations in words, fault catalog, weakness catalog, throughput numbers, validation plots.
6. **Environment and reward summary:** observation, action, reward variants, and why they are designed this way.
7. **Methods summary:** baselines, the 12 candidates, ensembles. One short paragraph and one row per method in a master table.
8. **Training summary:** curves for every candidate, tuning rounds and their outcomes, compute cost, instability or failures observed.
9. **Selection and ensembles:** the ranking, who made the top 5 and why, ensemble designs and their validation performance.
10. **Final results:** the main comparison tables and figures at every scale, with confidence intervals and significance tests.
11. **Generalization results:** scale 500 and the unseen topology family.
12. **Budget sweep and ablations:** each with a figure and an interpretation.
13. **Interpretability:** what the agents learned to target.
14. **Answers to RQ1 to RQ4:** each stated against its original hypothesis, with the evidence and a verdict (supported, partly supported, not supported).
15. **Failure analysis:** concrete failure cases and what they teach.
16. **Limitations and threats to validity:** simulator realism, self-planted weaknesses, reward design, seed variance, data coverage, and anything else found.
17. **Reproducibility:** how to rerun everything, expected runtime, expected outputs, how to verify they match.
18. **Timeline and compute:** when each stage ran, how long it took, how many experiments and training steps in total.
19. **Decision log digest:** the 10 most important decisions and deviations.
20. **Appendices:** the full candidate table (all 12 and any extras, including losers), configuration dumps, file inventory, and the complete list of figures and tables with paths.

`OVERALL.md` must contain at least **25 figures and tables in total** with real data, each captioned as in 6.2. It must be readable top to bottom as a complete account of the project.

### 6.5 Numbers in docs come from code (the facts registry)

- Every important number is written to `results/facts.json` by the code that produced it (key, value, unit, source file, timestamp). Example key: `final.scale100.chaosrl_top1.weaknesses_found_mean`.
- Docs reference numbers through placeholders such as `{{fact:final.scale100.chaosrl_top1.weaknesses_found_mean}}`. A script `python -m chaosrl docs-build` resolves the placeholders into the final Markdown and regenerates `docs/FACTS.md`. Never type a result number by hand into a doc.
- Tables in docs are generated from CSV files in `results/` and saved to `docs/tables/` as both CSV and Markdown.
- Figures are generated by plotting scripts and saved to `docs/figures/` (PNG at 200 dpi plus SVG). Never hand-draw or edit a figure.

### 6.6 The documentation check (`python -m chaosrl docs-check`)

Implement this command. It fails if any of these is true:
- A required section doc is missing, lacks any mandatory heading, or has fewer than 600 words of prose.
- A section doc has fewer than 2 figures, or 1 figure plus 2 tables.
- A referenced figure or table file does not exist.
- An unresolved `{{fact:...}}` placeholder remains, or a key is missing from `facts.json`.
- A figure has no caption with the three required parts.
- A number written in a doc differs from the corresponding value in `facts.json` (check any number that appears next to a recognized fact key).
- `INDEX.md` does not link to a doc that exists in `docs/`.
- A self-evaluation record for the stage is missing.

Run it at the end of every stage (part of 5.1 step 6) and again at the very end across all docs.

## 7. Repository structure

```
chaosrl/
  README.md
  pyproject.toml / requirements.txt   (pinned versions)
  Makefile
  configs/                 # YAML: budget, simulator, scales, faults, rewards, training, seeds
  src/chaosrl/
    cli.py                 # python -m chaosrl <command>
    data/                  # download + parse real datasets, calibration
    simulator/             # generators, dynamics, faults, weaknesses, metrics
    env/                   # Gymnasium-style env, observations, rewards
    agents/
      baselines/           # chaos monkey, random-all, round-robin, bandit, heuristic, oracle
      learned/             # networks, PPO, A2C, DQN, REINFORCE, ES, LinUCB, GBM ranker
      ensemble/            # soft vote, rank vote, RF-gated controller
    train/                 # trainers, curriculum, behavior cloning, logging, checkpoints
    evaluate/              # runner, metrics, stats, plots, interpretability
    docs_tools/            # facts registry, docs-build, docs-check, figure/table generators
    checks/                # per-stage exit criteria and invariants (python -m chaosrl check)
  tests/
  data_raw/                # downloaded data (git-ignored)
  results/                 # raw logs, checkpoints, tables, facts.json (generated)
  docs/                    # mandatory documentation (section 6)
  REPORT.md                # short generated report pointing into docs/OVERALL.md
```

Suggested libraries: `numpy`, `scipy`, `pandas`, `networkx`, `numba` (optional, for simulator speed), `torch` (CPU), `gymnasium`, `scikit-learn`, `matplotlib`, `pyyaml`, `psutil`, `tqdm`, `pytest`, `requests`, and `stable-baselines3` plus `sb3-contrib` (only for the sanity cross-check in section 14). Do not use `torch_geometric`. Implement the small graph network in plain PyTorch to avoid install problems.

## 8. Coding standards

- Python 3.11+, type hints on public functions, short docstrings that state purpose, inputs, and outputs.
- Small modules with single responsibilities. No file longer than about 600 lines. No function longer than about 80 lines without good reason.
- **All parameters live in YAML configs**, never as magic numbers in code. Every run saves the exact config it used next to its outputs, plus a config hash.
- **Determinism:** one master seed per run, derived child seeds per component (use `numpy.random.SeedSequence`). Never use global random state. Seed `numpy`, `random`, and `torch` explicitly in every worker.
- **Logging:** use the `logging` module with timestamped log files in `results/logs/`. Log at INFO the progress and at WARNING every anomaly. Never use bare `print` for anything important.
- **Errors:** fail loudly with a clear message. Never use blanket `except: pass`. Catch specific exceptions, log them, and decide explicitly whether to retry, skip with disclosure, or abort the stage.
- **Performance:** profile the simulator early. Vectorize with numpy across services. Avoid Python loops over services inside the tick loop. Use `numba` only if profiling shows it is needed and it installs cleanly.
- **Numerical safety:** clip rates and utilizations, guard against division by zero, use `float32` for networks and `float64` for simulator accumulators, and check for NaN/Inf after every tick in debug mode.
- **Git hygiene:** initialize git, commit at the end of every stage with a message like `stage NN: <summary>`, never commit `data_raw/`, checkpoints, or large logs (use `.gitignore`).
- **Naming:** descriptive names, `snake_case` for functions and files, constants in `UPPER_CASE`.

## 9. Testing standards

- Use `pytest`. Every module has tests. Aim for meaningful coverage of the simulator, weakness matching, environment, baselines, and ensembles.
- **Required tests:**
  - simulator determinism for identical seeds (byte-identical outputs)
  - the weakness-matching logic for every weakness type, including near-miss cases that must not match
  - fault rollback restores steady state
  - **no hidden-information leak** (assert that ground-truth weakness data never appears in any observation, feature vector, or info dict visible to agents)
  - action-mask validity (no masked action is ever selected)
  - each baseline's behavior (Chaos Monkey only kills containers)
  - environment API compliance
  - the budget accounting (never more experiments than the budget)
  - the test-set lock (raises without the environment variable)
  - ensemble members respect masks
  - facts registry and docs-check themselves (they are code too)
- Property-based checks where cheap (for example metrics are monotone in budget).
- Record the total test count and pass rate in `facts.json`. All tests must pass at the end of every stage.

## 10. Experiment and statistics standards

- **Seeds:** at least 3 training seeds per candidate and at least 5 evaluation seeds per system. Report all of them.
- **Intervals:** report means with **95% bootstrap confidence intervals** (at least 2000 resamples), computed over systems (the unit of replication), not over individual experiments within a system.
- **Significance:** use paired tests across systems (Wilcoxon signed-rank or paired bootstrap) for key comparisons. Report effect sizes (for example the mean paired difference and Cliff's delta). Apply and state a multiple-comparison correction (Holm-Bonferroni).
- **Normalization:** normalize discovery counts by the number of planted weaknesses so scales can be compared.
- **Never** report a single run as a result. Never pick the best seed. Report the spread.
- **Plots:** consistent color per method across all figures, colorblind-safe palette, labeled axes with units, legends, confidence bands, readable fonts, titles that state the finding, and a note of sample size (n systems, n seeds) in each caption.
- **Tables:** include n, mean, CI, and the best value highlighted in the Markdown version.
- Keep raw per-experiment logs (compressed CSV or Parquet) so any table can be regenerated.

---

# TECHNICAL STAGES

## 11. Stage 1: Design and hypotheses (doc: `section01_design.md`)

**Tasks:**
1. Detect OS, CPU count, RAM, and Python version. Create the repository skeleton, pinned environment, `configs/budget.yaml`, git repo, and `.gitignore`.
2. Implement the **docs tooling first** (facts registry, `docs-build`, `docs-check`, figure/table helpers) and the `check` command skeleton, because every later stage depends on them. Test them.
3. Write `docs/section01_design.md`: the problem, the four research questions with hypotheses and the planned evidence for each, the definition of every metric, the experimental design overview, the stage plan with time estimates, and a risk register (at least 10 risks with mitigations).
4. Create `docs/INDEX.md`, `docs/PROGRESS.md`, `docs/decision_log.md`, `docs/GLOSSARY.md` (skeletons filled as you go).

**Exit criteria:** repo skeleton exists; tools run on a dummy doc; hypotheses written with timestamps; risk register present; `docs-check` passes for section 1.

**Fallback:** none needed; this stage cannot meaningfully fail.

## 12. Stage 2: Real data and calibration (doc: `section02_data_calibration.md`)

Purpose: ground the simulator in real measurements instead of invented numbers.

**Source A: RCAEval** (real fault-injection datasets from microservice systems: Online Boutique, Sock Shop, Train Ticket).
- Code: `github.com/phamquiluan/RCAEval`. Data is hosted on Zenodo (find the record through the repository README; the record IDs I know of are 14504480 and 14504481, so verify which holds which part, and do not trust these IDs blindly).
- Try retrieval methods in this order: the repository's own download helper or `pip install` package if present, the Zenodo API/direct file URLs, then a `git clone` of the repository for any bundled data. Log each attempt.
- Use the **RE1** part first (375 cases; five fault types: CPU, MEM, DISK, DELAY, LOSS; injected into different services; repeated runs). Use RE2 only if size and time allow.
- Check file sizes first. If a single download exceeds `download_limit_gb`, choose the smallest subset that covers all fault types and systems, and log the choice.
- Each case contains metric time series and an injection timestamp. Parse them into a clean tabular form saved under `data_raw/` (git-ignored) and a processed summary under `results/calibration/`.
- Verify integrity: record file hashes, row counts, number of cases per system and fault type, and any parsing failures.

**Source B (optional): Alibaba microservices cluster traces** (`github.com/alibaba/clusterdata`, the microservices trace releases). Use them **only to estimate topology statistics**: distribution of call-graph depth, fan-out, and the share of hub services. These files can be huge, so download only the smallest sample. Skip this source if it is impractical and say so.

**Calibration procedure:**
1. For each fault type and each real case, compute metric changes between a pre-injection window and a post-injection window (latency, error indicators if present, CPU, memory, network).
2. Summarize the distributions of these effects per fault type, and per faulted service versus dependents if the data allows.
3. Fit the simulator's fault-response parameters (section 13.4) so simulated effects match these distributions. Minimize a distance such as Wasserstein or KS between simulated and real effect distributions. Because the simulator does not exist yet when this stage starts, write the fitting code against the simulator's interface and **run the final fit at the end of Stage 3**. Document this ordering.
4. Produce before/after comparison plots and the numeric distances. Do a **held-out check**: fit on a subset of cases or systems and measure the fit on the rest.

**State honestly** what calibration covers (how faults change metrics) and what it does not (planted weaknesses are still synthetic, because no real dataset provides ground-truth labels for fault selection). The correct claim is "a data-calibrated simulator", never "real systems".

**Exit criteria:** data cases parsed with counts reported, or documented fallback in place; per-fault-type effect distributions saved; fitting code runs on a toy simulator; docs-check passes.

**Invariants:** parsed case counts match the dataset description (or the discrepancy is explained); no negative latencies; every fault type present.

**Fallback:** if all retrieval methods fail, label everything **UNCALIBRATED**, use literature-style default parameter ranges documented in `ASSUMPTIONS.md`, and continue. Do not invent data.

## 13. Stage 3: The simulator (doc: `section03_simulator.md`)

Build a fast, seed-deterministic simulator of a microservice system. Use a **discrete-time aggregate model** (per-tick loads and latencies propagating through the graph), not per-request events. Vectorize with numpy (optionally numba). Measure and report throughput in experiments per minute at 20, 100, and 300 services (target at least 1,000 experiments per minute at 100 services; if lower, profile and optimize before continuing, and document the final number).

### 13.1 System generators

Two **topology families** (the second is used only for held-out generalization tests):
- **Family L (layered):** layered DAG (gateway → business services → data services), heavy-tailed fan-out, shared dependencies, a few hub services.
- **Family M (mesh/hub-and-spoke):** a different generator with more lateral calls and star-shaped clusters. Never used in training.

Configurable service count N. Required scales: **20, 100, 300**; held-out **500**. Also support small systems (5 to 15) for training diversity.

Infrastructure: M machines/nodes (for example N/8 to N/4, minimum 3). Each service has 1 to R replicas placed on nodes (co-location allowed, so a node failure hits several services). Per-service attributes: base latency, capacity per replica, timeout, retry count and backoff, circuit breaker (yes/no), fallback/cache (yes/no), autoscaling (yes/no and delay), health-check delay.

Workload: baseline request rate with noise (and an optional diurnal wave).

### 13.2 Dynamics (per tick)

For each service compute: incoming load including **retry amplification**, utilization per replica, queueing latency (a saturating curve), error rate, timeouts, circuit-breaker state, fallback effect, and autoscaling response. Latency and errors propagate to callers. The model must produce **cascading failures and retry storms** naturally. Add measurement noise to observed metrics.

### 13.3 Observability and SLO

Observed per-service metrics: p50/p99 latency, error rate, CPU utilization, request rate, healthy replica count. The system SLO is measured at the gateway (p99 latency and error rate thresholds). Define the steady state and verify that a fault-free system meets it.

### 13.4 Faults (single `inject(fault)` interface)

1. Container/pod kill (**the original Chaos Monkey fault**)
2. Node failure (kills all replicas on a machine)
3. Latency injection on a service
4. Network packet loss/errors on a service's calls
5. CPU stress / resource exhaustion
6. Dependency error injection

Each fault has a target, an **intensity level** (low/medium/high), and a duration. Response functions use the parameters fitted in Stage 2.

### 13.5 Planted ground-truth weaknesses

At generation time, plant a known set and store it in a hidden ground-truth structure **never visible to agents**.
- **Simple weaknesses** (one fault triggers an SLO violation): single-replica critical service, missing timeout on a hot path, no circuit breaker on a flaky dependency, two critical services co-located on one node, low capacity margin with no autoscaling.
- **Compound weaknesses** (need two or more simultaneous faults): for example latency on B plus retries at A causes a retry storm; one pod kill plus CPU stress on the other replica.
- **Counts:** simple = max(3, round(0.06 × N)); compound = max(1, round(0.02 × N)).
- **Decoys (important):** include **well-protected hub services** (replicas, timeouts, breakers) and **fragile low-degree services**, so "always attack the most connected service" is not sufficient. Verify this with the heuristic baseline in Stage 5.

A weakness is "found" when an experiment's fault set satisfies the weakness's trigger condition **and** the SLO is violated in simulation. Implement deterministically and unit-test it. Record unplanted ("emergent") SLO violations separately.

### 13.6 Experiment protocol

One **experiment** = inject a fault set (1 fault, or optionally 2 faults for compound weaknesses), simulate T ticks, record SLO violation and damage, roll back, and let the system recover. An **episode** = a fixed budget B of experiments on one system. Default B = 100. Also evaluate B ∈ {25, 50, 200}. **Damage** = accumulated SLO-violation time weighted by severity (the safety metric).

**After the simulator exists, run the Stage 2 final calibration fit and re-run the validation plots.**

**Exit criteria:** all tests pass; throughput measured at all three scales; steady state verified; each fault shows a plausible effect (plots); at least one retry storm demonstrated; determinism verified; calibration fit completed and plotted (or UNCALIBRATED label applied everywhere); planted weakness counts and decoys verified on a sample of generated systems; docs-check passes.

**Invariants:** fault-free systems meet the SLO; node failure affects every replica on that node; weakness matching has zero false positives on a large random sample where triggers are deliberately not met.

**Fallback:** if throughput cannot reach 300 experiments per minute at 100 services after optimization, reduce the maximum scale to 200 and tell the user in the docs and the final summary.

## 14. Stage 4: Environment design (doc: `section04_environment.md`)

Implement a Gymnasium-style `ChaosEnv`. It must work for **any number of services**, so the policy is **topology-agnostic**.

**Observation (per service, as a graph):**
- Runtime: latency ratio vs baseline, error rate, utilization, request rate, healthy/total replicas, currently faulted?
- Structure: in-degree, out-degree, layer depth, replica count, node co-location count
- History: times this service was tested per fault type, last outcome of tests on it
- Global: experiments left, damage so far, weaknesses found so far
- The adjacency (who calls whom) as a sparse matrix.
- **Observation modes:** **black-box** (default: the above only) and **gray-box** (also exposes static configuration flags such as timeout/circuit-breaker presence). Gray-box is used only for an ablation, since those flags would let an agent shortcut discovery.

**Action:** pick a candidate (service, fault type, intensity). For compound mode, an experiment allows **up to K = 2 picks**, with a "no second fault" option. A candidate mask removes invalid or exhausted actions.

**Reward variants (configurable):**
- **R1:** +1 per newly found weakness, 0 otherwise
- **R2 (default):** R1 minus a damage penalty, minus a small cost for repeating an already-tested fault
- **R3:** R2 plus a small bonus for informative partial degradation (shaping)
Explain in the section doc how R2 and R3 avoid teaching the agent to maximize damage, and test this empirically with a "damage-maximizer" probe policy.

**Episode:** budget B experiments, then done. Each reset generates a new system from the training seed distribution.

**Exit criteria:** environment API compliance test passes; the hidden-information leak test passes; masks verified; a random policy runs 100 episodes without error at all scales; observation sizes scale linearly with N; docs-check passes.

**Invariants:** reward is bounded and finite; budget accounting is exact; reset is deterministic given a seed.

**Fallback:** if the graph observation proves too slow, aggregate neighborhoods to top-k statistics and document it.

## 15. Stage 5: Non-learned baselines (doc: `section05_baselines.md`)

All use the same interface and budget. For fairness, every method may choose 1 or 2 faults per experiment unless noted.
1. **Chaos Monkey (faithful):** uniform random service, container kill only, single fault.
2. **Chaos Monkey-2:** same, but may kill 2 containers.
3. **Random-All:** uniform over all services, fault types, and intensities; a second fault with probability 0.5.
4. **Round-robin sweep:** fixed order over (service, fault).
5. **UCB bandit** over (service, fault type) arms (tune exploration with a small fair search on validation systems).
6. **Heuristic expert:** rule-based using topology (prefer hubs, single-replica services, co-located services). This answers "why not just use simple rules?".
7. **Oracle (upper bound, reference only):** knows the hidden weaknesses and finds them as fast as possible. It never competes.

**Seed ranges (never overlap), defined here and enforced in code:**
- Training systems: generated on the fly from seeds 0 to 99,999
- Validation systems: seeds 100,000 to 100,099 (100 systems across scales)
- Test systems: seeds 200,000 to 200,199 (200 systems: scales 20, 100, 300 from Family L; the held-out scale 500; and held-out Family M). **Locked per section 5.6.**

Run all baselines on **validation systems only** at this stage.

**Exit criteria:** every baseline runs at every scale; the oracle dominates all others; the decoy check passes (heuristic does not solve the benchmark; report how much it finds); Chaos Monkey finds only kill-type weaknesses; baseline results saved with CIs; docs-check passes.

**Fallback:** if the heuristic solves nearly everything, increase decoy density in the generator and rerun before proceeding (log the change).

## 16. Stage 6: Candidate pool (doc: `section06_candidates.md`)

Implement a shared **scorer network** `Scorer(state graph) → score per candidate action`. Because the number of services varies, avoid fixed-size inputs. Implement the training algorithms yourself in PyTorch (stable-baselines3 cannot cleanly handle variable-size candidate sets). As a **correctness check**, cross-check your PPO against `MaskablePPO` from `sb3-contrib` on a small fixed-size system and report both learning curves.

| ID | Method | Notes |
|---|---|---|
| **C01** | PPO + MLP scorer | Per-service MLP, shared weights, reward R2 |
| **C02** | PPO + GNN scorer | Small message-passing network over the call graph |
| **C03** | PPO + recurrent (GRU) | Recurrent memory over the experiment history |
| **C04** | A2C + MLP scorer | Synchronous actor-critic |
| **C05** | Double + Dueling DQN | Q-value per candidate action, replay buffer |
| **C06** | REINFORCE with baseline | Simplest policy gradient |
| **C07** | PPO + curriculum | Train small systems first, then grow N |
| **C08** | Behavior cloning then PPO | Pretrain on heuristic-expert (and oracle) demonstrations, then RL fine-tune |
| **C09** | PPO + novelty bonus | Count-based exploration bonus on (service, fault) and outcome signatures |
| **C10** | Evolution strategies | Gradient-free optimization of scorer weights (OpenAI-ES or CMA-ES) |
| **C11** | LinUCB contextual bandit | Non-deep learned method with topology and metric features |
| **C12** | Gradient-boosted ranker | Supervised model (scikit-learn) trained on logged experience to predict which candidates reveal weaknesses; a non-RL learned baseline |

Families (used for diversity in selection): **actor-critic/policy-gradient** (C01, C03, C04, C06, C07, C08, C09), **structure-aware** (C02), **value-based** (C05), **gradient-free** (C10), **non-deep learned** (C11, C12).

**Implementation guidance (RL practicalities):**
- Apply action masks by setting masked logits to a very large negative value before the softmax. Verify masked actions get exactly zero probability.
- Normalize advantages per batch, clip gradients (for example max norm 0.5), and use a learning-rate schedule. Use entropy regularization with a decaying coefficient. Scale rewards if their range is large.
- For PPO use generalized advantage estimation, multiple epochs over each batch, and a clip range. Track KL divergence and clip fraction; log them.
- For DQN use a target network, a replay buffer, epsilon-greedy with decay, and Huber loss. Mask invalid actions in both the argmax and the targets.
- For evolution strategies, use antithetic sampling and fitness shaping (rank normalization). Use the same total number of environment steps budget as the others where possible.
- For C12, build the training dataset from logged episodes of the heuristic and random policies on training systems only.
- Log every training run's loss, return, weaknesses found, damage, entropy, and gradient norm to `results/training/<candidate>/seed<k>/`.
- Add extra candidates if time allows, but never drop C01 to C12 under the Full scope.

**Exit criteria:** every candidate trains for a short smoke run without error and learns something above random on a tiny system (a "learning sanity" check: after a short training on small systems, validation performance must beat Random-All by a visible margin for at least the simplest learner, otherwise investigate bugs); the PPO cross-check against `MaskablePPO` agrees within a reasonable tolerance; mask tests pass; docs-check passes.

**Invariants:** shuffled-observation control performs near random for learned agents; no candidate sees hidden information.

**Fallback:** a candidate that cannot be made to run after 3 iterations is dropped, documented as failed (with the traceback summary and diagnosis), and the pool continues without it.

## 17. Stage 7: Training and automated tuning (doc: `section07_training.md`)

**Procedure:**
1. **Smoke phase:** train every candidate briefly (`--quick`). Measure steps per second, RAM, and time per candidate. Use these to project the total training time (section 5.7) and choose the scope.
2. **Intensive rounds:** train each candidate with **at least 3 training seeds** on the training distribution (a mix of scales 5 to 300 and both reward variants only where the ablation needs it). Run candidates in parallel (at most 6 workers). Checkpoint often. Each round ends with an evaluation on **validation systems only**.
3. **Automated tuning loop** per section 5.5, with the playbook below.
4. Use the same total environment-interaction budget per candidate where possible, and report any that differ.

### 17.1 Validation score (define in `section01_design.md`)

Validation score = normalized **area under the discovery curve (AUDC)** for weaknesses found over the experiment budget (average over validation systems), with total damage as a tiebreaker.

### 17.2 Tuning playbook (apply in this order for an underperforming candidate)

1. Learning rate ×0.5 or ×2
2. Entropy coefficient ×0.5 or ×2
3. Network width or depth ×0.5 or ×2
4. Reward weights (damage penalty, repeat penalty)
5. Batch size or rollout length
6. Curriculum schedule (faster or slower growth in N)
7. For DQN: epsilon decay, target update interval, replay size
8. For ES: population size, noise standard deviation

Apply one or two changes per round. Record the reason.

### 17.3 Freeze (end of Stage 8 selection, described below)

**Exit criteria:** every candidate has at least 3 completed training seeds (or is documented as failed or budget-cut); training curves saved; the tuning log is complete; no candidate shows NaN loss; validation scores computed with CIs; compute time recorded; docs-check passes.

**Invariants:** more training steps do not catastrophically reduce validation performance without explanation (investigate drops); checkpoints reload to produce the same actions.

**Fallback:** if time is running out, reduce seeds to 2 for lower-ranked candidates first, then drop the lowest-ranked candidates, and document it.

## 18. Stage 8: Selection, freeze, and ensembles (doc: `section08_selection_ensembles.md`)

**Selection (on validation only):** rank candidates by mean validation score across training seeds. Choose the **top 5 with at most 2 from the same family** to keep the ensemble diverse. Document the rule and show the full ranking. Also build a "pure top-5" ensemble as an ablation.

**Freeze:** hash every selected model (SHA-256) into `results/frozen_manifest.json`. After this, no further training or tuning of any model. All other candidates are frozen too, for the complete-pool comparison.

**Ensembles:**
- **E1: Soft vote:** convert each member's scores to a probability distribution over candidates (respecting masks), average, then take the maximum (also test sampling).
- **E2: Rank vote (Borda):** each member ranks the candidates; combine by summed rank.
- **E3: Random-forest gated controller (the "random forest of the 5"):** a scikit-learn random forest that sees summary state features plus each member's proposed action and confidence, and **predicts which member to trust** in the current state. Build its training data from **validation systems only**: **clone the simulator** at each step, evaluate every member's proposal from the same state, and label which member's proposal found a new weakness (or caused the least damage). At test time, take the predicted member's action. Check for overfitting with cross-validation across systems.
- Report honestly if no ensemble beats the best single agent.

**Exit criteria:** top 5 chosen by the stated rule; frozen manifest written; all three ensembles implemented and evaluated on validation; no test-set access recorded; docs-check passes.

**Invariants:** the ensemble never picks a masked action; E3's training data contains no test-system information.

**Fallback:** if E3 fails to train usefully, report it as a negative result and keep E1 and E2.

## 19. Stage 9: Final evaluation (doc: `section09_final_evaluation.md`)

**Run once** via `python -m chaosrl final-eval` after the freeze (section 5.6). Run on the **test systems**: baselines (section 15), the **top 5 singles**, the **ensembles**, and **all other candidates** for completeness. Identical budgets and at least **5 evaluation seeds** per system.

**Metrics:**
- Weaknesses found vs. number of experiments (discovery curve) and normalized AUDC
- Weaknesses found at the full budget (as a fraction of planted)
- Experiments to the first weakness, and to 50% and 90% of planted weaknesses
- **Simple vs. compound** weaknesses found, reported separately
- **Damage** (safety)
- Emergent (unplanted) violations found
- Redundant experiments (fraction repeating already-tested faults)
- Decision time per experiment

**Experiments:**
1. Main comparison across scales 20, 100, 300 (Family L)
2. **Generalization:** scale 500 and Family M (both unseen)
3. **Budget sweep:** B ∈ {25, 50, 100, 200}
4. **Ablations:** reward R1/R2/R3; black-box vs. gray-box observation; with vs. without history features; single-fault vs. compound mode; pure top-5 vs. diverse top-5 ensemble; GNN vs. MLP scorer. (Ablations that need retraining must be trained **before the freeze**, on training data, and evaluated here. Plan them in Stage 7 and note this in the training doc.)
5. **Training-approach comparison (RQ2):** all candidates compared by family
6. **Interpretability:** what the agents target. Report correlations between chosen targets and service properties (degree, replica count, co-location, layer), and show a few example episodes
7. **Failure analysis (required):** cases where ChaosRL loses to or ties with random, reward-hacking checks, seed sensitivity, weakness types systematically missed, with examples
8. **Compute cost:** training time per candidate, inference time per decision, memory

**Statistics:** per section 10.

**Post-run self-evaluation:** run the full seven-step routine. If you find a bug in the evaluation code, fix it, **rerun**, keep the first run's results labeled "first run (buggy)", and disclose both in the docs. Do **not** tune any model on test results.

**Exit criteria:** all experiments completed with the required seeds; statistics computed; every table and figure generated from raw logs; independent recomputation matches; the test access log shows only the `final-eval` command (plus any disclosed rerun); docs-check passes.

**Invariants:** the oracle dominates; budget-monotonicity holds; shuffled-observation control is near random; metrics from raw logs match reported tables.

**Fallback:** if the full evaluation exceeds the remaining time budget, reduce evaluation seeds from 5 to 3 first, then the number of systems per scale, never the number of methods, and document it.

## 20. Stage 10 and 11: Analysis, limitations, and reproducibility (docs: `section10_analysis_limitations.md`, `section11_reproducibility.md`)

**Stage 10 tasks:**
- Answer RQ1 to RQ4 against the original hypotheses, with evidence and a verdict each.
- Write the full failure analysis and the limitations and threats-to-validity discussion (simulator realism, self-planted weaknesses, calibration coverage, reward design, seed variance, small-scale training budgets, overfitting to the simulator's structure, anything found during self-evaluations).
- Write `docs/ASSUMPTIONS.md`, `docs/EXPLAINER.md` (plain-language explanation of the whole project: the problem, the simulator, the reward, each algorithm family, each baseline, the ensemble, how to read each figure, written so **every team member can explain and defend it**), `docs/QA.md` (at least 25 likely examiner questions with answers based on the real results, for example "why RL instead of a bandit?", "how do you know the planted weaknesses are representative?", "why doesn't the reward just encourage damage?", "does it generalize?", "what would you do differently?"), `docs/PRESENTATION_OUTLINE.md` (8 to 10 slides listing the figures and tables to show), and `docs/GLOSSARY.md`.

**Stage 11 tasks:**
- Verify reproducibility: on a clean copy of the repository (fresh virtual environment, only the README commands), run `python -m chaosrl quick` and confirm it completes, and re-run one small stage with the same seed to confirm identical outputs. Record the result and timing.
- Write a README with setup and run instructions that work from a clean machine, a one-command quick demo, and the exact command sequence to reproduce each stage and the final tables.
- Generate the short `REPORT.md` pointing into `docs/OVERALL.md`.

**Exit criteria:** all docs exist; QA has at least 25 entries; the clean-copy check passed; docs-check passes for every section; `OVERALL.md` has all 20 parts and at least 25 figures and tables; full-repo docs-check passes.

## 21. Optional stage Z: Real-container validation (doc: `section12_docker_validation.md`)

Run **only** if `run_docker_validation: true` in `configs/budget.yaml`. Default is off.

If enabled, do a **small** validation on real containers with Docker Desktop (about 6 GB of memory for Docker, one app at a time, 8 to 10 containers):
- Build one lightweight mini-app (Python/FastAPI or Go services, Redis, SQLite or small Postgres; no JVM, Kafka, or heavy monitoring stacks) with weaknesses behind **environment-variable toggles** (missing timeout, retries without backoff, single replica, no circuit breaker), plus a "fixed" control variant.
- Inject faults with Docker-level tools (container kill/pause, CPU and memory limits, Toxiproxy for latency/errors). Generate load with Locust or k6. Measure the SLO at the gateway.
- Run the **frozen** top agents and the random baseline zero-shot. Use only observations that exist in real containers (latency, error rate, CPU, replica count).
- Report it as a small-scale sanity check with all its limitations (noise, few systems). Do not retune anything based on it. Apply the same documentation and self-evaluation rules.

## 22. Orchestration and long-run management

- Provide `python -m chaosrl run-all` that executes every stage in order, performs each stage's self-evaluation and docs-check automatically, and resumes after interruption. Also allow `python -m chaosrl run-stage <n>`.
- Update `docs/PROGRESS.md` and `results/heartbeat.json` continuously.
- If a stage's self-evaluation fails after the maximum iterations, apply the fallback, continue, and record it everywhere required.
- Keep a **time ledger**: for each stage, the planned, projected, and actual hours. If the projection exceeds the budget, shrink the plan per section 5.7.
- Never leave a stage half-documented. If you run out of time, finish the documentation of what you completed before stopping, and state in `OVERALL.md` exactly what was not completed.

## 23. Anti-patterns (do not do these)

- Writing documentation at the very end from memory.
- Typing numbers into docs by hand.
- Reporting `--quick` results as final results.
- Tuning on the test set, or looking at test results before the freeze.
- Reporting only the best seed or only the best candidate.
- Giving baselines less tuning effort than the learned methods.
- Letting the agent observe configuration flags or ground truth (except in the labeled gray-box ablation).
- Declaring PASS without running the independent recomputation and the adversarial review.
- Silencing a failing test, loosening a threshold to make a check pass without logging why, or deleting a failing candidate without documenting it.
- Describing the simulator as "real" or the results as "real-world".
- Leaving placeholders, TODOs, or empty headings in finished docs.
- Waiting for user input. This run is autonomous.

## 24. Acceptance checklist (everything must be true, and checked by code where possible)

1. Data downloaded (or the UNCALIBRATED fallback documented) and the calibration report written.
2. A tested simulator with both topology families and scales 20 to 500 (or the documented reduced scale), with measured throughput.
3. All baselines, including the heuristic and the oracle reference.
4. The full candidate pool trained with multiple seeds (or documented reductions), with training curves, logs, and the tuning log.
5. Top 5 selected on validation by the stated rule, frozen with hashes, plus ensembles E1 to E3.
6. One final test run with statistics, generalization tests, budget sweep, ablations, interpretability, and failure analysis.
7. **Every section doc (section01 to section11, plus section12 if run) exists, passes `docs-check`, and was written at the time its stage completed.**
8. **`docs/OVERALL.md` is complete (all 20 parts, at least 25 captioned figures and tables, all numbers from the facts registry).**
9. `docs/ASSUMPTIONS.md`, `EXPLAINER.md`, `QA.md`, `PRESENTATION_OUTLINE.md`, `GLOSSARY.md`, `INDEX.md`, `FACTS.md`, `decision_log.md`, and `PROGRESS.md` exist and are complete.
10. A self-evaluation record exists for every stage, with a final verdict.
11. All tests pass, and the clean-copy reproducibility check passed.
12. `results/test_access_log.csv` shows the test set was accessed only by the final evaluation (plus any disclosed rerun).
13. No unresolved placeholders, TODOs, or fabricated numbers anywhere (run a final scan).

## 25. Final summary (print this when everything is done)

When the acceptance checklist passes, print a short summary containing: what was built; the scope that was run (Full or Minimum) and why; total compute hours; the headline results copied from `facts.json` (not recalled), including the answer to each of RQ1 to RQ4; the top 5 models and the ensemble results; the biggest limitations; every fallback or reduction that was applied; and the paths to `docs/INDEX.md`, `docs/OVERALL.md`, and `docs/PRESENTATION_OUTLINE.md`.

## 26. First actions (start now)

1. Detect the environment (OS, CPU, RAM, Python). Create the repo skeleton, pinned environment, `configs/budget.yaml` (create with the defaults in section 5.7 if absent), git repo, and `.gitignore`.
2. Build the docs tooling and the `check` command skeleton (Stage 1) and test them.
3. Write `docs/section01_design.md` with the hypotheses and risk register, then run Stage 1's self-evaluation.
4. Continue through Stage 2 to Stage 11 in order, documenting each stage as you finish it, without waiting for the user.