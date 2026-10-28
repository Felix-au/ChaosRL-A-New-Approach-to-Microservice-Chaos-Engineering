"""Automated tuning loop, multi-seed training suite, and Stage 7 artifact generator."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from chaosrl.agents.candidates.registry import CANDIDATE_REGISTRY, get_candidate
from chaosrl.docs_tools.facts_registry import register_fact
from chaosrl.docs_tools.figures_tables import (
    CB_PALETTE,
    METHOD_COLORS,
    save_figure,
    save_table,
    setup_matplotlib_style,
)
from chaosrl.train.trainer import evaluate_on_validation, train_single_candidate


# Tuning playbook definitions per Section 17.2
TUNING_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "C01": {"lr": 1e-4, "entropy_coef": 0.03},
    "C02": {"lr": 2e-4, "entropy_coef": 0.02},
    "C03": {"lr": 1e-4, "entropy_coef": 0.02},
    "C04": {"lr": 3e-4, "entropy_coef": 0.03},
    "C05": {"lr": 5e-4, "epsilon_decay": 0.99},
    "C06": {"lr": 5e-4},
    "C07": {"lr": 2e-4, "entropy_coef": 0.02},
    "C08": {"lr": 1e-4, "entropy_coef": 0.02},
    "C09": {"intrinsic_weight": 0.2},
    "C10": {"sigma": 0.08, "lr": 0.03},
    "C11": {"alpha": 0.8},
    "C12": {"n_estimators": 80},
}


def run_stage7_training_suite(
    train_seeds: List[int] = [10, 20, 30],
    steps_per_run: int = 1200,
    max_tuning_rounds: int = 2,
    val_seeds: List[int] = list(range(100000, 100004)),
) -> Dict[str, Any]:
    """Execute Stage 7 multi-seed training, automated tuning loop, and validation benchmarks."""
    setup_matplotlib_style()
    print("Starting Stage 7 Multi-Seed Training & Automated Tuning...")

    tuning_log_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []

    candidate_results: Dict[str, Dict[str, Any]] = {}
    round1_audcs: Dict[str, List[float]] = {}
    best_agents: Dict[str, Any] = {}

    # -------------------------------------------------------------
    # Round 1: Baseline Training across all 12 Candidates x 3 Seeds
    # -------------------------------------------------------------
    print("--- Round 1: Training Initial Candidates Across 3 Seeds ---")
    for cid in CANDIDATE_REGISTRY:
        meta = CANDIDATE_REGISTRY[cid]
        name = meta["name"]
        family = meta["family"]
        print(f"Training {cid} ({name}) across seeds {train_seeds}...")

        seed_audcs: List[float] = []
        seed_recalls: List[float] = []
        seed_damages: List[float] = []
        agents_by_seed: Dict[int, Any] = {}

        for s in train_seeds:
            train_res = train_single_candidate(
                candidate_id=cid,
                train_seed=s,
                total_steps=steps_per_run,
            )
            agent = train_res["agent"]
            agents_by_seed[s] = agent

            # Evaluate on validation systems
            val_res = evaluate_on_validation(agent, val_seeds=val_seeds)
            seed_audcs.append(val_res["audc"])
            seed_recalls.append(val_res["recall"])
            seed_damages.append(val_res["damage"])

        round1_audcs[cid] = seed_audcs
        mean_audc = float(np.mean(seed_audcs))
        best_seed_idx = int(np.argmax(seed_audcs))
        best_agents[cid] = agents_by_seed[train_seeds[best_seed_idx]]

        candidate_results[cid] = {
            "name": name,
            "family": family,
            "audc_mean": mean_audc,
            "audc_std": float(np.std(seed_audcs)),
            "recall_mean": float(np.mean(seed_recalls)),
            "damage_mean": float(np.mean(seed_damages)),
            "hyperparams": {},
            "tuning_status": "Initial",
        }

    # -------------------------------------------------------------
    # Round 2: Automated Tuning for Underperforming Candidates
    # -------------------------------------------------------------
    print("--- Round 2: Automated Tuning Playbook Execution ---")
    # Rank candidates by AUDC
    sorted_cids = sorted(candidate_results.keys(), key=lambda c: candidate_results[c]["audc_mean"], reverse=True)
    median_audc = float(np.median([candidate_results[c]["audc_mean"] for c in candidate_results]))

    for cid in sorted_cids:
        curr_audc = candidate_results[cid]["audc_mean"]
        curr_se = candidate_results[cid]["audc_std"] / np.sqrt(len(train_seeds))

        # Underperforming criteria: below median AUDC or candidate targeted in playbook
        if curr_audc <= median_audc and cid in TUNING_PLAYBOOK:
            hp_proposal = TUNING_PLAYBOOK[cid]
            reason = f"AUDC {curr_audc:.4f} <= median {median_audc:.4f}; applying playbook tuning"
            print(f"Tuning {cid}: {hp_proposal} ({reason})...")

            tuned_audcs = []
            tuned_recalls = []
            tuned_damages = []
            tuned_agents = {}

            for s in train_seeds:
                train_res = train_single_candidate(
                    candidate_id=cid,
                    train_seed=s,
                    total_steps=steps_per_run,
                    hyperparams=hp_proposal,
                )
                agent = train_res["agent"]
                tuned_agents[s] = agent
                val_res = evaluate_on_validation(agent, val_seeds=val_seeds)
                tuned_audcs.append(val_res["audc"])
                tuned_recalls.append(val_res["recall"])
                tuned_damages.append(val_res["damage"])

            tuned_mean = float(np.mean(tuned_audcs))
            improvement = tuned_mean - curr_audc
            # Acceptance rule: improves by > 1 standard error
            accepted = improvement > curr_se

            tuning_log_rows.append({
                "Candidate ID": cid,
                "Name": candidate_results[cid]["name"],
                "Round": 2,
                "Proposed Parameter Change": str(hp_proposal),
                "Reason for Change": reason,
                "Pre-Tuning AUDC": round(curr_audc, 4),
                "Post-Tuning AUDC": round(tuned_mean, 4),
                "Improvement": round(improvement, 4),
                "Standard Error": round(curr_se, 4),
                "Decision": "ACCEPTED" if accepted else "REVERTED",
            })

            if accepted:
                candidate_results[cid]["audc_mean"] = tuned_mean
                candidate_results[cid]["audc_std"] = float(np.std(tuned_audcs))
                candidate_results[cid]["recall_mean"] = float(np.mean(tuned_recalls))
                candidate_results[cid]["damage_mean"] = float(np.mean(tuned_damages))
                candidate_results[cid]["hyperparams"] = hp_proposal
                candidate_results[cid]["tuning_status"] = "Tuned (Accepted)"
                best_seed_idx = int(np.argmax(tuned_audcs))
                best_agents[cid] = tuned_agents[train_seeds[best_seed_idx]]
            else:
                candidate_results[cid]["tuning_status"] = "Tuned (Reverted)"

    # Save tuning log to CSV and markdown
    tuning_csv_path = Path("results/tuning_log.csv")
    with open(tuning_csv_path, "w", newline="", encoding="utf-8") as f:
        if tuning_log_rows:
            writer = csv.DictWriter(f, fieldnames=list(tuning_log_rows[0].keys()))
            writer.writeheader()
            writer.writerows(tuning_log_rows)

    save_table(tuning_log_rows, "stage7_tuning_log")

    # -------------------------------------------------------------
    # Shuffled Observation Sanity Invariant Check
    # -------------------------------------------------------------
    # Pick the top candidate and evaluate on shuffled observations
    top_cid = sorted(candidate_results.keys(), key=lambda c: candidate_results[c]["audc_mean"], reverse=True)[0]
    top_agent = best_agents[top_cid]
    shuffled_eval = evaluate_on_validation(top_agent, val_seeds=val_seeds, shuffle_obs=True)
    normal_top_audc = candidate_results[top_cid]["audc_mean"]
    shuffled_audc = shuffled_eval["audc"]
    audc_drop = normal_top_audc - shuffled_audc

    print(f"Top candidate ({top_cid}) Normal AUDC: {normal_top_audc:.4f}, Shuffled AUDC: {shuffled_audc:.4f} (Drop: {audc_drop:.4f})")

    # -------------------------------------------------------------
    # Compile Master Summary Table
    # -------------------------------------------------------------
    for cid in sorted(candidate_results.keys()):
        res = candidate_results[cid]
        summary_rows.append({
            "Candidate ID": cid,
            "Name": res["name"],
            "Family": res["family"],
            "Validation AUDC": round(res["audc_mean"], 4),
            "AUDC Std": round(res["audc_std"], 4),
            "Validation Recall": round(res["recall_mean"], 4),
            "Cumulative Damage": round(res["damage_mean"], 1),
            "Tuning Status": res["tuning_status"],
        })

    save_table(summary_rows, "stage7_training_summary", highlight_max_cols=["Validation AUDC"])

    # -------------------------------------------------------------
    # Figures Generation
    # -------------------------------------------------------------
    # Figure 1: Training Validation Ranking
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    cids_sorted = sorted(candidate_results.keys(), key=lambda c: candidate_results[c]["audc_mean"])
    y_pos = np.arange(len(cids_sorted))
    audcs = [candidate_results[c]["audc_mean"] for c in cids_sorted]
    errs = [candidate_results[c]["audc_std"] for c in cids_sorted]
    bar_colors = [CB_PALETTE["blue"] if "GNN" in candidate_results[c]["name"] or "PPO" in candidate_results[c]["name"] else CB_PALETTE["vermilion"] for c in cids_sorted]

    bars = ax1.barh(y_pos, audcs, xerr=errs, color=bar_colors, edgecolor="black", alpha=0.85, capsize=3)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"{c}: {candidate_results[c]['name']}" for c in cids_sorted], fontsize=9)
    ax1.set_xlabel("Validation Normalized AUDC (Area Under Discovery Curve)")
    ax1.set_title("Stage 7 Candidate Validation Performance Across 3 Training Seeds")
    ax1.grid(axis="x", linestyle="--", alpha=0.3)
    save_figure(fig1, "stage7_training_curves")

    # Figure 2: Tuning Progress Delta
    fig2, ax2 = plt.subplots(figsize=(9, 4.5))
    if tuning_log_rows:
        tuned_cids = [r["Candidate ID"] for r in tuning_log_rows]
        pre_scores = [r["Pre-Tuning AUDC"] for r in tuning_log_rows]
        post_scores = [r["Post-Tuning AUDC"] for r in tuning_log_rows]
        x_idx = np.arange(len(tuned_cids))
        width = 0.35

        ax2.bar(x_idx - width/2, pre_scores, width, label="Pre-Tuning AUDC", color=CB_PALETTE["gray"], edgecolor="black")
        ax2.bar(x_idx + width/2, post_scores, width, label="Post-Tuning AUDC", color=CB_PALETTE["bluish_green"], edgecolor="black")
        ax2.set_xticks(x_idx)
        ax2.set_xticklabels(tuned_cids)
        ax2.set_ylabel("Validation AUDC")
        ax2.set_title("Automated Hyperparameter Tuning AUDC Delta")
        ax2.legend()
        ax2.grid(axis="y", linestyle="--", alpha=0.3)
    save_figure(fig2, "stage7_tuning_progress")

    # -------------------------------------------------------------
    # Register Stage 7 Facts
    # -------------------------------------------------------------
    register_fact("training.best_candidate_id", top_cid, unit="candidate", source_file="src/chaosrl/train/tuning.py")
    register_fact("training.best_candidate_audc", round(normal_top_audc, 4), unit="audc", source_file="src/chaosrl/train/tuning.py")
    register_fact("training.tuning_rounds_completed", len(tuning_log_rows), unit="rounds", source_file="src/chaosrl/train/tuning.py")
    register_fact("training.shuffled_obs_audc", round(shuffled_audc, 4), unit="audc", source_file="src/chaosrl/train/tuning.py")
    register_fact("training.shuffled_control_drop", round(audc_drop, 4), unit="audc", source_file="src/chaosrl/train/tuning.py")

    return {
        "candidate_results": candidate_results,
        "tuning_log": tuning_log_rows,
        "summary": summary_rows,
        "top_candidate": top_cid,
        "shuffled_drop": audc_drop,
    }
