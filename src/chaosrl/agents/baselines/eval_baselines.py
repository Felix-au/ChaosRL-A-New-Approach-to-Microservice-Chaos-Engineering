"""Evaluation suite for non-learned baselines on validation systems."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from chaosrl.agents.baselines.baselines import (
    ChaosMonkeyAgent,
    ChaosMonkey2Agent,
    HeuristicExpertAgent,
    OracleAgent,
    RandomAllAgent,
    RoundRobinAgent,
    UCBBanditAgent,
)
from chaosrl.docs_tools.figures_tables import (
    save_figure,
    save_table,
    setup_matplotlib_style,
    CB_PALETTE,
    METHOD_COLORS,
)
from chaosrl.docs_tools.facts_registry import register_fact
from chaosrl.env.chaos_env import ChaosEnv, RewardVariant


def bootstrap_ci(data: List[float], n_resamples: int = 2000, ci: float = 0.95) -> Tuple[float, float]:
    """Compute 95% bootstrap confidence interval over systems."""
    if len(data) == 0:
        return 0.0, 0.0
    if len(data) == 1:
        return data[0], data[0]

    arr = np.array(data)
    boot_means = []
    rng = np.random.default_rng(42)
    for _ in range(n_resamples):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boot_means.append(np.mean(sample))

    alpha = (1.0 - ci) / 2.0
    low = float(np.percentile(boot_means, alpha * 100.0))
    high = float(np.percentile(boot_means, (1.0 - alpha) * 100.0))
    return low, high


def run_baseline_validation_suite(
    val_seeds: List[int] = list(range(100000, 100020)),
    scale: int = 100,
    budget: int = 100,
) -> Dict[str, Any]:
    """Evaluate all 7 baselines across validation systems."""
    setup_matplotlib_style()

    agents_to_test = [
        ("chaos_monkey", "Chaos Monkey (Faithful)", ChaosMonkeyAgent),
        ("chaos_monkey_2", "Chaos Monkey-2", ChaosMonkey2Agent),
        ("random_all", "Random-All", RandomAllAgent),
        ("round_robin", "Round-Robin Sweep", RoundRobinAgent),
        ("bandit_ucb", "Bandit UCB", UCBBanditAgent),
        ("heuristic", "Heuristic Expert", HeuristicExpertAgent),
        ("oracle", "Oracle (Upper Bound)", OracleAgent),
    ]

    metrics_by_agent: Dict[str, Dict[str, List[float]]] = {
        name: {
            "found_frac": [],
            "audc": [],
            "damage": [],
            "simple_found": [],
            "compound_found": [],
        }
        for name, _, _ in agents_to_test
    }

    discovery_trajectories: Dict[str, np.ndarray] = {
        name: np.zeros((len(val_seeds), budget), dtype=np.float64)
        for name, _, _ in agents_to_test
    }

    # Evaluate each agent across validation systems
    for s_idx, seed in enumerate(val_seeds):
        for name, label, agent_cls in agents_to_test:
            env = ChaosEnv(num_services=scale, experiment_budget=budget, seed=seed)
            agent = agent_cls(env)

            obs, _ = env.reset(seed=seed)
            step_found = []
            done = False
            total_planted = len(env.system.ground_truth_weaknesses)

            while not done:
                action = agent.select_action(obs)
                obs, r, term, trunc, info = env.step(action)
                if hasattr(agent, "update"):
                    act_to_update = action if isinstance(action, int) else action[0]
                    agent.update(act_to_update, r)

                step_found.append(env.weaknesses_found_count / max(1, total_planted))
                done = term or trunc

            # Trajectory
            discovery_trajectories[name][s_idx, :] = np.array(step_found)

            # Metrics
            final_frac = float(step_found[-1])
            audc_val = float(np.mean(step_found))
            metrics_by_agent[name]["found_frac"].append(final_frac)
            metrics_by_agent[name]["audc"].append(audc_val)
            metrics_by_agent[name]["damage"].append(env.cumulative_damage)

            # Weakness breakdown
            simples = len([w for w in env.system.ground_truth_weaknesses if not w.is_compound and w.discovered])
            compounds = len([w for w in env.system.ground_truth_weaknesses if w.is_compound and w.discovered])
            metrics_by_agent[name]["simple_found"].append(simples)
            metrics_by_agent[name]["compound_found"].append(compounds)

    # Compile validation results table with 95% bootstrap CIs
    results_rows = []
    breakdown_rows = []

    for name, label, _ in agents_to_test:
        ff = metrics_by_agent[name]["found_frac"]
        audc_vals = metrics_by_agent[name]["audc"]
        dam_vals = metrics_by_agent[name]["damage"]

        ff_low, ff_high = bootstrap_ci(ff)
        audc_low, audc_high = bootstrap_ci(audc_vals)
        dam_low, dam_high = bootstrap_ci(dam_vals)

        results_rows.append({
            "Method": label,
            "Mean Weakness Recall": float(np.mean(ff)),
            "Recall 95% CI": f"[{ff_low:.3f}, {ff_high:.3f}]",
            "Normalized AUDC": float(np.mean(audc_vals)),
            "AUDC 95% CI": f"[{audc_low:.3f}, {audc_high:.3f}]",
            "Mean Cumulative Damage": float(np.mean(dam_vals)),
            "Damage 95% CI": f"[{dam_low:.1f}, {dam_high:.1f}]",
        })

        breakdown_rows.append({
            "Method": label,
            "Mean Simple Weaknesses Found": float(np.mean(metrics_by_agent[name]["simple_found"])),
            "Mean Compound Weaknesses Found": float(np.mean(metrics_by_agent[name]["compound_found"])),
            "Total Planted (Scale 100)": 8.0,
        })

    save_table(results_rows, "stage5_baseline_validation_results", highlight_max_cols=["Normalized AUDC"])
    save_table(breakdown_rows, "stage5_weakness_breakdown_by_baseline", highlight_max_cols=["Mean Compound Weaknesses Found"])

    # Figure 1: Weakness Discovery Curves
    fig, ax = plt.subplots(figsize=(9, 5))
    x_axis = np.arange(1, budget + 1)

    for name, label, _ in agents_to_test:
        trajs = discovery_trajectories[name]
        mean_traj = np.mean(trajs, axis=0)
        std_traj = np.std(trajs, axis=0)
        color = METHOD_COLORS.get(name, CB_PALETTE["gray"])
        ls = ":" if name == "oracle" else ("--" if "chaos_monkey" in name else "-")

        ax.plot(x_axis, mean_traj, label=label, color=color, lw=2.0, ls=ls)
        ax.fill_between(x_axis, np.maximum(0, mean_traj - 0.5 * std_traj), np.minimum(1.0, mean_traj + 0.5 * std_traj), color=color, alpha=0.1)

    ax.set_xlabel("Experiment Injections Budget (B)")
    ax.set_ylabel("Fraction of Planted Weaknesses Found")
    ax.set_title(f"Baseline Weakness Discovery Curves on Validation Systems (N={scale}, n={len(val_seeds)} systems)")
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="lower right", fontsize=8)
    save_figure(fig, "stage5_baseline_discovery_curves")

    # Figure 2: Damage vs. Discovery Scatter
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    for name, label, _ in agents_to_test:
        mean_ff = float(np.mean(metrics_by_agent[name]["found_frac"]))
        mean_dam = float(np.mean(metrics_by_agent[name]["damage"]))
        color = METHOD_COLORS.get(name, CB_PALETTE["gray"])
        marker = "*" if name == "oracle" else "o"
        size = 140 if name == "oracle" else 90

        ax2.scatter(mean_dam, mean_ff, label=label, color=color, s=size, marker=marker, edgecolors="black", zorder=4)
        ax2.annotate(label, (mean_dam + 1.5, mean_ff - 0.02), fontsize=8)

    ax2.set_xlabel("Cumulative Severity-Weighted Damage (Safety)")
    ax2.set_ylabel("Weakness Discovery Fraction (Efficiency)")
    ax2.set_title("Safety vs. Discovery Trade-off Across Baselines")
    ax2.grid(True, alpha=0.3, ls="--")
    save_figure(fig2, "stage5_baseline_damage_vs_discovery")

    # Register facts in registry
    register_fact("baseline.oracle.audc", float(np.mean(metrics_by_agent["oracle"]["audc"])), unit="audc", source_file="src/chaosrl/agents/baselines/eval_baselines.py")
    register_fact("baseline.chaos_monkey.audc", float(np.mean(metrics_by_agent["chaos_monkey"]["audc"])), unit="audc", source_file="src/chaosrl/agents/baselines/eval_baselines.py")
    register_fact("baseline.random_all.audc", float(np.mean(metrics_by_agent["random_all"]["audc"])), unit="audc", source_file="src/chaosrl/agents/baselines/eval_baselines.py")
    register_fact("baseline.heuristic.audc", float(np.mean(metrics_by_agent["heuristic"]["audc"])), unit="audc", source_file="src/chaosrl/agents/baselines/eval_baselines.py")
    register_fact("baseline.heuristic.recall", float(np.mean(metrics_by_agent["heuristic"]["found_frac"])), unit="recall", source_file="src/chaosrl/agents/baselines/eval_baselines.py")

    return {
        "results_table": results_rows,
        "breakdown_table": breakdown_rows,
        "metrics_by_agent": metrics_by_agent,
    }

