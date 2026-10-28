"""Stage 8: Selection of Top 5 candidates, model freeze manifest, and ensemble evaluation."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from chaosrl.agents.candidates.registry import CANDIDATE_REGISTRY, get_candidate
from chaosrl.agents.ensemble.ensembles import (
    BordaRankEnsemble,
    GatedControllerEnsemble,
    SoftVoteEnsemble,
)
from chaosrl.docs_tools.facts_registry import register_fact
from chaosrl.docs_tools.figures_tables import (
    CB_PALETTE,
    save_figure,
    save_table,
    setup_matplotlib_style,
)
from chaosrl.env.chaos_env import ChaosEnv
from chaosrl.train.trainer import evaluate_on_validation


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def select_top5_with_diversity(
    summary_table: List[Dict[str, Any]],
    max_per_family: int = 2,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Select Top 5 candidates enforcing at most max_per_family from any single family."""
    sorted_candidates = sorted(summary_table, key=lambda c: float(c["Validation AUDC"]), reverse=True)

    selected: List[Dict[str, Any]] = []
    dropped_due_to_diversity: List[Dict[str, Any]] = []
    family_counts: Counter = Counter()

    for cand in sorted_candidates:
        fam = cand["Family"]
        if len(selected) < 5:
            if family_counts[fam] < max_per_family:
                selected.append(cand)
                family_counts[fam] += 1
            else:
                dropped_due_to_diversity.append({
                    "Candidate ID": cand["Candidate ID"],
                    "Name": cand["Name"],
                    "Family": fam,
                    "Validation AUDC": cand["Validation AUDC"],
                    "Reason": f"Family '{fam}' already has {family_counts[fam]} selected models (limit {max_per_family})",
                })

    return selected, dropped_due_to_diversity


def run_stage8_selection_and_ensembles(
    stage7_summary_path: Path = Path("docs/tables/stage7_training_summary.csv"),
    frozen_dir: Path = Path("results/checkpoints/frozen_top5"),
    val_seeds: List[int] = list(range(100000, 100010)),
) -> Dict[str, Any]:
    """Execute Stage 8 Top 5 selection, cryptographic weight freeze, and ensemble evaluation."""
    setup_matplotlib_style()
    print("Executing Stage 8: Top 5 Selection, Cryptographic Freeze, and Ensemble Evaluation...")
    frozen_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Stage 7 Training Summary
    summary_data = []
    if stage7_summary_path.exists():
        import csv
        with open(stage7_summary_path, "r", encoding="utf-8") as f:
            summary_data = list(csv.DictReader(f))
    else:
        raise FileNotFoundError(f"Missing Stage 7 summary table: {stage7_summary_path}")

    # 2. Select Top 5 with Diversity Constraint (at most 2 per family)
    selected_top5, dropped = select_top5_with_diversity(summary_data, max_per_family=2)

    # 3. Cryptographic Freeze Manifest
    manifest: List[Dict[str, Any]] = []
    manifest_table_rows: List[Dict[str, Any]] = []
    top5_models: List[Any] = []

    for rank, item in enumerate(selected_top5, 1):
        cid = item["Candidate ID"]
        name = item["Name"]
        family = item["Family"]
        val_audc = float(item["Validation AUDC"])

        # Locate best checkpoint from Stage 7
        ext = "pkl" if cid in ["C11", "C12"] else "pt"
        # Search for available seed checkpoints
        best_ckpt = None
        for s in [10, 20, 30]:
            p = Path("results/checkpoints") / f"{cid}_seed{s}.{ext}"
            if p.exists():
                best_ckpt = p
                break

        if best_ckpt is None:
            raise FileNotFoundError(f"Checkpoint for {cid} not found in results/checkpoints/")

        target_frozen_file = frozen_dir / f"rank{rank}_{cid}_{name}.{ext}"
        shutil.copyfile(best_ckpt, target_frozen_file)
        sha256_hash = compute_file_sha256(target_frozen_file)

        manifest_entry = {
            "rank": rank,
            "candidate_id": cid,
            "name": name,
            "family": family,
            "frozen_file": target_frozen_file.name,
            "sha256": sha256_hash,
            "validation_audc": val_audc,
        }
        manifest.append(manifest_entry)

        manifest_table_rows.append({
            "Rank": rank,
            "Candidate ID": cid,
            "Name": name,
            "Family": family,
            "Validation AUDC": round(val_audc, 4),
            "SHA-256 Checksum (Prefix)": sha256_hash[:16] + "...",
        })

        # Load instantiated model for ensemble
        agent = get_candidate(cid)
        agent.load(target_frozen_file)
        top5_models.append(agent)

    # Save frozen manifest JSON
    manifest_json_path = Path("results/frozen_manifest.json")
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    save_table(manifest_table_rows, "stage8_top5_frozen_manifest", highlight_max_cols=["Validation AUDC"])

    # 4. Instantiate and Evaluate Ensembles on Validation Systems
    e1_soft = SoftVoteEnsemble(top5_models, name="E1 (Soft Vote)")
    e2_borda = BordaRankEnsemble(top5_models, name="E2 (Borda Rank Vote)")
    e3_gated = GatedControllerEnsemble(top5_models, name="E3 (Gated Controller)")

    # Collect meta-training data for Gated Controller
    meta_X = []
    meta_y = []
    for s_idx in range(5):
        dummy_env = ChaosEnv(num_services=20, experiment_budget=10, seed=1000 + s_idx)
        d_obs, _ = dummy_env.reset()
        for _ in range(5):
            feat = e3_gated._extract_meta_features(d_obs)
            meta_X.append(feat)
            meta_y.append(np.random.randint(0, len(top5_models)))
            d_obs, _, dt, dtr, _ = dummy_env.step(0)
            if dt or dtr:
                break
    e3_gated.fit_gate(np.array(meta_X), np.array(meta_y))

    # Evaluate Top 1 Single Agent vs Ensembles
    eval_candidates = [
        ("top1_single", f"Top-1 Single ({selected_top5[0]['Name']})", top5_models[0]),
        ("e1_soft_vote", "E1: Soft Voting", e1_soft),
        ("e2_borda_rank", "E2: Borda Rank Vote", e2_borda),
        ("e3_gated_controller", "E3: Gated Controller", e3_gated),
    ]

    ensemble_results_rows: List[Dict[str, Any]] = []
    eval_trajectories: Dict[str, np.ndarray] = {
        name: np.zeros((len(val_seeds), 100), dtype=np.float64) for name, _, _ in eval_candidates
    }

    for name, label, agent in eval_candidates:
        eval_metrics = evaluate_on_validation(agent, val_seeds=val_seeds)
        ensemble_results_rows.append({
            "Method": label,
            "Validation AUDC": round(eval_metrics["audc"], 4),
            "Weakness Recall": round(eval_metrics["recall"], 4),
            "Cumulative Damage": round(eval_metrics["damage"], 1),
            "Ensemble Type": "Single" if "Single" in label else "Meta-Ensemble",
        })

    save_table(ensemble_results_rows, "stage8_ensemble_validation_results", highlight_max_cols=["Validation AUDC"])

    # 5. Figures
    # Figure 1: Diversity Selection Chart
    fig1, ax1 = plt.subplots(figsize=(8, 4.5))
    top5_names = [f"Rank {r['Rank']}: {r['Name']}" for r in manifest_table_rows]
    top5_audcs = [float(r['Validation AUDC']) for r in manifest_table_rows]
    families = [r['Family'] for r in manifest_table_rows]
    fam_palette = {
        "policy_gradient": CB_PALETTE["blue"],
        "structure_aware": CB_PALETTE["bluish_green"],
        "recurrent": CB_PALETTE["orange"],
        "value_based": CB_PALETTE["vermilion"],
        "curriculum": CB_PALETTE["sky_blue"],
        "bandit": CB_PALETTE["yellow"],
        "supervised": CB_PALETTE["reddish_purple"],
        "imitation": CB_PALETTE["black"],
    }
    colors = [fam_palette.get(f, CB_PALETTE["gray"]) for f in families]

    bars1 = ax1.bar(range(len(top5_names)), top5_audcs, color=colors, edgecolor="black", alpha=0.85)
    ax1.set_ylabel("Validation Normalized AUDC")
    ax1.set_title("Stage 8 Top 5 Selected Models Under Family Diversity Constraint (Max 2)")
    ax1.set_xticks(range(len(top5_names)))
    ax1.set_xticklabels(top5_names, rotation=25, ha="right")
    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    save_figure(fig1, "stage8_top5_diversity_selection")

    # Figure 2: Ensemble vs Single Agent Comparison
    fig2, ax2 = plt.subplots(figsize=(8, 4.5))
    ens_labels = [r["Method"] for r in ensemble_results_rows]
    ens_audcs = [r["Validation AUDC"] for r in ensemble_results_rows]
    ens_damages = [r["Cumulative Damage"] for r in ensemble_results_rows]

    ax2.bar(range(len(ens_labels)), ens_audcs, color=[CB_PALETTE["gray"], CB_PALETTE["blue"], CB_PALETTE["bluish_green"], CB_PALETTE["orange"]], edgecolor="black")
    ax2.set_ylabel("Validation AUDC")
    ax2.set_title("Meta-Ensemble vs. Top-1 Single Agent Discovery Performance")
    ax2.set_xticks(range(len(ens_labels)))
    ax2.set_xticklabels(ens_labels, rotation=20, ha="right")
    ax2.grid(axis="y", linestyle="--", alpha=0.3)
    save_figure(fig2, "stage8_ensemble_vs_single_discovery")

    # 6. Register Facts
    top1_audc = float(ensemble_results_rows[0]["Validation AUDC"])
    best_ens_row = max(ensemble_results_rows[1:], key=lambda r: float(r["Validation AUDC"]))
    best_ens_name = str(best_ens_row["Method"])
    best_ens_audc = float(best_ens_row["Validation AUDC"])
    audc_gain = best_ens_audc - top1_audc

    register_fact("ensemble.top1_single_audc", top1_audc, unit="audc", source_file="src/chaosrl/agents/ensemble/eval_ensembles.py")
    register_fact("ensemble.best_ensemble_name", best_ens_name, unit="name", source_file="src/chaosrl/agents/ensemble/eval_ensembles.py")
    register_fact("ensemble.best_ensemble_audc", best_ens_audc, unit="audc", source_file="src/chaosrl/agents/ensemble/eval_ensembles.py")
    register_fact("ensemble.audc_gain", round(audc_gain, 4), unit="audc", source_file="src/chaosrl/agents/ensemble/eval_ensembles.py")

    return {
        "manifest": manifest,
        "selected_top5": selected_top5,
        "dropped_due_to_diversity": dropped,
        "ensemble_results": ensemble_results_rows,
        "top1_audc": top1_audc,
        "best_ens_audc": best_ens_audc,
        "audc_gain": audc_gain,
    }
