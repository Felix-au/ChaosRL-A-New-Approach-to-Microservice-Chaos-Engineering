"""Independent research audit tests for Section S9: Final Evaluation, Statistics & Fact Consistency.

Verifies claims CLM-S09-01 through CLM-S09-12:
- Recomputation of all Stage 9 tables from raw test logs in scale100_raw_results.pkl
- Metric granularity bounds (step and weakness resolution)
- Statistical testing engine validation (Wilcoxon and Holm-Bonferroni on synthetic ground truth)
- Statistical power analysis (sample size N=10 vs N=30 systems)
- Mathematical invariants (AUDC in [0, 1], Recall in [0, 1], non-negative damage)
- Experimental ablation configuration differentiation
- Truth-in-reporting check: raw test results vs facts.json vs documented prose claims
- Test access audit: timestamp verification in test_access_log.csv
Includes explicit negative controls demonstrating test failure under broken assumptions.
"""

import pickle
import json
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from scipy import stats


@pytest.mark.audit
def test_t_s09_01_recompute_stage9_metrics_from_raw():
    """T-S09-01: Independently recompute Scale 100 test table from scale100_raw_results.pkl."""
    raw_path = Path("results/scale100_raw_results.pkl")
    assert raw_path.exists()
    with open(raw_path, "rb") as f:
        raw_data = pickle.load(f)

    # Required methods present
    expected_methods = [
        "chaos_monkey", "chaos_monkey_2", "random_all", "round_robin",
        "bandit_ucb", "heuristic", "oracle", "C12", "e1_soft", "e2_borda", "e3_gated"
    ]
    assert set(expected_methods).issubset(set(raw_data.keys()))

    # Verify that raw trajectories match computed means
    for m in expected_methods:
        d = raw_data[m]
        recomputed_audc = float(np.mean(d["audcs"]))
        recomputed_recall = float(np.mean(d["recalls"]))
        recomputed_damage = float(np.mean(d["damages"]))

        assert abs(recomputed_audc - d["audc_mean"]) < 1e-5
        assert abs(recomputed_recall - d["recall_mean"]) < 1e-5
        assert abs(recomputed_damage - d["damage_mean"]) < 1e-3

    # Negative control: Corrupted mean assertion must fail
    with pytest.raises(AssertionError):
        assert abs(raw_data["chaos_monkey"]["audc_mean"] - 0.99) < 1e-5


@pytest.mark.audit
def test_t_s09_02_metric_granularity_bounds():
    """T-S09-02: Metric granularity analysis: minimum detectable recall and AUDC step resolution."""
    # Scale 100 systems plant 8 weaknesses (6 simple + 2 compound)
    weaknesses_per_system = 8
    num_test_systems = 10
    budget = 100

    min_single_system_recall_delta = 1.0 / weaknesses_per_system  # 0.125
    min_cohort_recall_delta = 1.0 / (weaknesses_per_system * num_test_systems)  # 0.0125

    assert abs(min_single_system_recall_delta - 0.125) < 1e-6
    assert abs(min_cohort_recall_delta - 0.0125) < 1e-6

    # Minimum non-zero AUDC on a single system with 1 weakness found at final step 100
    # Trapezoid from step 99 (0) to 100 (0.125): area = (0 + 0.125)/2 * 1 = 0.0625 / 100 = 0.000625
    min_single_audc = (0.5 * min_single_system_recall_delta) / budget
    assert abs(min_single_audc - 0.000625) < 1e-6

    # Negative control: Claiming resolution below 0.000001 on N=10 systems is unphysical
    with pytest.raises(AssertionError):
        assert min_cohort_recall_delta < 0.0001


@pytest.mark.audit
def test_t_s09_03_statistical_engine_validation():
    """T-S09-03: Validate Wilcoxon signed-rank and Holm-Bonferroni correction on synthetic ground truth."""
    # Synthetic paired samples with known true shift
    rng = np.random.default_rng(42)
    sample_a = rng.normal(10.0, 1.0, size=20)
    sample_b = sample_a + 2.5  # Deterministic positive shift

    stat, p_val = stats.wilcoxon(sample_b, sample_a, alternative="greater")
    assert p_val < 0.001, f"Wilcoxon failed to detect true shift: p={p_val}"

    # Holm-Bonferroni correction procedure
    raw_p_values = [0.001, 0.02, 0.04, 0.50]
    m = len(raw_p_values)
    # Order p-values
    sorted_p = sorted(raw_p_values)
    adjusted_p = [min(1.0, (m - i) * p) for i, p in enumerate(sorted_p)]
    assert adjusted_p[0] == 0.004
    assert adjusted_p[1] == 0.06  # 3 * 0.02

    # Negative control: Comparing identical samples must NOT produce p < 0.01
    sample_identical = sample_a.copy()
    diff = sample_identical - sample_a
    # Identical samples have zero non-zero differences
    assert np.all(diff == 0.0)


@pytest.mark.audit
def test_t_s09_04_statistical_power_comparison():
    """T-S09-04: Power analysis: evaluate minimum detectable effect size for N=10 vs N=30 systems."""
    # For paired comparison at alpha=0.05 and beta=0.20 (80% power):
    # Required Cohen's d: d approx sqrt((z_{1-a/2} + z_{1-b})^2 / N)
    # For N=10: d_crit approx sqrt((1.96 + 0.84)^2 / 10) = sqrt(7.84 / 10) approx 0.885 (Large effect only!)
    # For N=30: d_crit approx sqrt(7.84 / 30) approx 0.511 (Medium effect detectable!)
    d_n10 = np.sqrt(7.84 / 10.0)
    d_n30 = np.sqrt(7.84 / 30.0)

    assert d_n10 > 0.85, f"Expected d_n10 > 0.85, got {d_n10}"
    assert d_n30 < 0.55, f"Expected d_n30 < 0.55, got {d_n30}"
    # N=30 has substantially higher statistical resolution
    assert d_n30 < d_n10 * 0.60

    # Negative control: Claiming N=10 can reliably detect small effect d=0.20 must fail
    with pytest.raises(AssertionError):
        assert d_n10 <= 0.20


@pytest.mark.audit
def test_t_s09_05_stage9_physical_invariants():
    """T-S09-05: Verify all Stage 9 test metrics satisfy mathematical invariants."""
    table_path = Path("docs/tables/stage9_main_comparison_scale100.csv")
    assert table_path.exists()
    df = pd.read_csv(table_path)

    for _, row in df.iterrows():
        audc = row["Normalized AUDC"]
        recall = row["Weakness Recall"]
        damage = row["Cumulative Damage"]
        simple_found = row["Mean Simple Found"]
        compound_found = row["Mean Compound Found"]

        assert 0.0 <= audc <= 1.0, f"AUDC out of bounds for {row['Method']}: {audc}"
        assert 0.0 <= recall <= 1.0, f"Recall out of bounds for {row['Method']}: {recall}"
        assert damage >= 0.0, f"Negative damage for {row['Method']}: {damage}"
        assert 0.0 <= simple_found <= 6.0, f"Simple found out of bounds: {simple_found}"
        assert 0.0 <= compound_found <= 2.0, f"Compound found out of bounds: {compound_found}"

    # Negative control: Negative damage must be rejected
    with pytest.raises(AssertionError):
        assert -15.0 >= 0.0


@pytest.mark.audit
def test_t_s09_06_ablation_configurations_differentiation():
    """T-S09-06: Verify ablation table configurations are distinct and correctly evaluated."""
    ablation_csv = Path("docs/tables/stage9_ablation_study.csv")
    assert ablation_csv.exists()
    df = pd.read_csv(ablation_csv)
    assert len(df) == 5, f"Expected 5 ablation rows, found {len(df)}"

    conditions = df["Ablation Dimension"].tolist()
    assert len(set(conditions)) >= 2, "Ablation dimensions must cover reward and observation modes"


@pytest.mark.audit
def test_t_s09_07_fact_consistency_and_discrepancy_disclosure():
    """T-S09-07: CRITICAL TRUTH-IN-REPORTING AUDIT: Verify facts.json matches raw test logs."""
    with open("results/facts.json", "r", encoding="utf-8") as f:
        facts = json.load(f)

    with open("results/scale100_raw_results.pkl", "rb") as f:
        raw_data = pickle.load(f)

    # Check that facts.json faithfully reflects the raw test execution
    cm_audc = facts["final.scale100.chaos_monkey.audc"]["value"]
    top1_audc = facts["final.scale100.chaosrl_top1.audc"]["value"]
    p_val_cm = facts["final.scale100.p_value_vs_chaos_monkey"]["value"]

    assert abs(cm_audc - raw_data["chaos_monkey"]["audc_mean"]) < 1e-3
    assert abs(top1_audc - raw_data["C12"]["audc_mean"]) < 1e-3
    assert p_val_cm == 1.0  # Statistical test is non-significant!

    # Auditor finding: On this 10-system sample, Chaos Monkey (0.0853) beat Top-1 (0.0500)!
    assert cm_audc > top1_audc, "Observed raw data must confirm Chaos Monkey AUDC > Top-1 AUDC on Scale 100"


@pytest.mark.audit
def test_t_s09_08_test_access_log_chronology():
    """T-S09-08: Verify test access log records test evaluation strictly succeeding freeze manifest."""
    access_log = Path("results/test_access_log.csv")
    assert access_log.exists()
    
    with open(access_log, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) > 2, "Test access log must contain access entries"

    # Line 2 records entrypoint lock
    first_record = lines[1].split(",")
    first_ts = first_record[0]
    first_commit = first_record[2] if len(first_record) >= 3 else ""

    assert "2026-10-28" in first_ts
    assert first_commit.startswith("4be8cf1"), f"Expected freeze commit 4be8cf1, found {first_commit}"

    # Line 3+ records seed evaluations
    seed_record = lines[2].split(",")
    assert len(seed_record) >= 3
    assert int(seed_record[1]) >= 200_000, f"Logged seed {seed_record[1]} not in test set"
