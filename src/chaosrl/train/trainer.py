"""Training harness for ChaosRL candidate models across multiple seeds."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch

from chaosrl.agents.candidates.registry import get_candidate
from chaosrl.env.chaos_env import ChaosEnv

torch.set_num_threads(1)


def train_single_candidate(
    candidate_id: str,
    train_seed: int,
    total_steps: int = 1500,
    train_scales: List[int] = [20, 50, 100],
    checkpoint_dir: Path = Path("results/checkpoints"),
    log_dir: Path = Path("results/training"),
    hyperparams: Optional[Dict[str, Any]] = None,
    reuse_existing: bool = True,
) -> Dict[str, Any]:
    """Train a single candidate agent for total_steps on training systems, or load existing checkpoint."""
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    hp = hyperparams or {}
    agent = get_candidate(candidate_id, **hp)

    ext = "pkl" if candidate_id in ["C11", "C12"] else "pt"
    suffix = "_tuned" if hyperparams else ""
    ckpt_path = checkpoint_dir / f"{candidate_id}_seed{train_seed}{suffix}.{ext}"
    if not ckpt_path.exists() and not suffix:
        ckpt_path = checkpoint_dir / f"{candidate_id}_seed{train_seed}.{ext}"

    # If checkpoint exists and reuse is allowed, load and return
    if reuse_existing and ckpt_path.exists():
        try:
            agent.load(ckpt_path)
            return {
                "candidate_id": candidate_id,
                "train_seed": train_seed,
                "total_steps": total_steps,
                "episodes": 10,
                "mean_reward": 0.0,
                "mean_weaknesses": 0.0,
                "checkpoint_path": str(ckpt_path),
                "agent": agent,
            }
        except Exception as e:
            print(f"Warning: failed to load existing checkpoint {ckpt_path}: {e}. Retraining...")

    rng = np.random.default_rng(train_seed)
    current_scale = train_scales[0]
    # Training seeds come from disjoint range: 0..99,999
    system_seed = int(train_seed * 1000 + rng.integers(0, 999))

    env = ChaosEnv(num_services=current_scale, experiment_budget=100, seed=system_seed)
    obs, _ = env.reset(seed=system_seed)
    agent.reset_episode()

    step_count = 0
    episode_count = 0
    ep_rewards: List[float] = []
    ep_weaknesses: List[int] = []

    current_ep_reward = 0.0
    trajectory: Dict[str, list] = {
        "obs": [],
        "actions": [],
        "rewards": [],
        "dones": [],
        "log_probs": [],
        "values": [],
    }

    metrics_log: List[Dict[str, float]] = []

    # For TreeRanker dataset collection
    tree_X: List[np.ndarray] = []
    tree_y: List[int] = []

    while step_count < total_steps:
        # Scale curriculum progression if supported
        if candidate_id == "C07" and step_count > 0 and step_count % 500 == 0:
            if hasattr(agent, "advance_stage"):
                current_scale = agent.advance_stage()
                system_seed = int(train_seed * 1000 + rng.integers(0, 999))
                env = ChaosEnv(num_services=current_scale, experiment_budget=100, seed=system_seed)
                obs, _ = env.reset(seed=system_seed)
                agent.reset_episode()

        action = agent.select_action(obs)
        if isinstance(action, (list, tuple)):
            action = int(action[0])

        if hasattr(agent, "evaluate_step"):
            lp, val, _ = agent.evaluate_step(obs, action)
        else:
            lp, val = 0.0, 0.0

        next_obs, reward, term, trunc, info = env.step(action)
        done = term or trunc
        step_count += 1
        current_ep_reward += reward

        # Record transition
        trajectory["obs"].append(obs)
        trajectory["actions"].append(action)
        trajectory["rewards"].append(reward)
        trajectory["dones"].append(float(done))
        trajectory["log_probs"].append(lp)
        trajectory["values"].append(val)

        # Collect TreeRanker features
        if candidate_id == "C12":
            svc_id = action // 18
            slot = action % 18
            ft_idx = slot // 3
            inten_idx = slot % 3
            ft_oh = np.zeros(6)
            ft_oh[ft_idx] = 1.0
            int_oh = np.zeros(3)
            int_oh[inten_idx] = 1.0
            vec = np.concatenate([obs["node_features"][svc_id], obs["global_features"], ft_oh, int_oh])
            tree_X.append(vec)
            tree_y.append(1 if reward > 0 else 0)

        # Agent-specific incremental updates
        if hasattr(agent, "update"):
            agent.update(action, obs, reward)
        elif hasattr(agent, "store_transition"):
            agent.store_transition(obs, action, reward, next_obs, done)
            if step_count % 4 == 0:
                agent.train_step()

        obs = next_obs

        # Trajectory updates for policy gradient methods (PPO, A2C, REINFORCE)
        if len(trajectory["rewards"]) >= 64 or done:
            if hasattr(agent, "update_on_trajectories"):
                up_metrics = agent.update_on_trajectories([trajectory], epochs=4)
                if up_metrics:
                    up_metrics["step"] = float(step_count)
                    up_metrics["ep_reward"] = float(current_ep_reward)
                    metrics_log.append(up_metrics)
            elif hasattr(agent, "update_episode") and done:
                ep_trans = list(zip(trajectory["obs"], trajectory["actions"], trajectory["rewards"]))
                up_metrics = agent.update_episode(ep_trans)
                if up_metrics:
                    up_metrics["step"] = float(step_count)
                    up_metrics["ep_reward"] = float(current_ep_reward)
                    metrics_log.append(up_metrics)

            trajectory = {"obs": [], "actions": [], "rewards": [], "dones": [], "log_probs": [], "values": []}

        if done:
            episode_count += 1
            ep_rewards.append(current_ep_reward)
            ep_weaknesses.append(env.weaknesses_found_count)
            current_ep_reward = 0.0

            # Reset environment with next training system
            scale_pick = rng.choice(train_scales)
            system_seed = int(train_seed * 1000 + rng.integers(0, 999))
            env = ChaosEnv(num_services=int(scale_pick), experiment_budget=100, seed=system_seed)
            obs, _ = env.reset(seed=system_seed)
            agent.reset_episode()

    # Final fit for tree ranker
    if candidate_id == "C12" and tree_X:
        agent.train_dataset(np.array(tree_X), np.array(tree_y))

    # Save model checkpoint
    ext = "pkl" if candidate_id in ["C11", "C12"] else "pt"
    ckpt_path = checkpoint_dir / f"{candidate_id}_seed{train_seed}.{ext}"
    agent.save(ckpt_path)

    # Save training metrics log
    metrics_path = log_dir / f"{candidate_id}_seed{train_seed}_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({
            "candidate_id": candidate_id,
            "train_seed": train_seed,
            "total_steps": step_count,
            "episodes": episode_count,
            "mean_reward": float(np.mean(ep_rewards)) if ep_rewards else 0.0,
            "mean_weaknesses": float(np.mean(ep_weaknesses)) if ep_weaknesses else 0.0,
            "metrics": metrics_log,
        }, f, indent=2)

    return {
        "candidate_id": candidate_id,
        "train_seed": train_seed,
        "total_steps": step_count,
        "episodes": episode_count,
        "mean_reward": float(np.mean(ep_rewards)) if ep_rewards else 0.0,
        "mean_weaknesses": float(np.mean(ep_weaknesses)) if ep_weaknesses else 0.0,
        "checkpoint_path": str(ckpt_path),
        "agent": agent,
    }


def evaluate_on_validation(
    agent: Any,
    val_seeds: List[int] = list(range(100000, 100010)),
    scale: int = 100,
    budget: int = 100,
    shuffle_obs: bool = False,
) -> Dict[str, float]:
    """Evaluate a trained agent exclusively on validation systems (seeds 100,000..100,009)."""
    audc_scores: List[float] = []
    recall_scores: List[float] = []
    damage_scores: List[float] = []

    for v_seed in val_seeds:
        env = ChaosEnv(num_services=scale, experiment_budget=budget, seed=v_seed)
        obs, _ = env.reset(seed=v_seed)
        agent.reset_episode()

        step_found: List[float] = []
        total_planted = max(1, len(env.system.ground_truth_weaknesses))

        done = False
        while not done:
            # Adversarial sanity check: shuffle observation features across nodes
            if shuffle_obs:
                shuffled_obs = {k: v.copy() for k, v in obs.items()}
                np.random.shuffle(shuffled_obs["node_features"])
                act = agent.select_action(shuffled_obs, deterministic=True)
            else:
                act = agent.select_action(obs, deterministic=True)

            if isinstance(act, (list, tuple)):
                act = int(act[0])

            obs, _, term, trunc, _ = env.step(act)
            step_found.append(env.weaknesses_found_count / total_planted)
            done = term or trunc

        audc_scores.append(float(np.mean(step_found)))
        recall_scores.append(float(step_found[-1]))
        damage_scores.append(float(env.cumulative_damage))

    return {
        "audc": float(np.mean(audc_scores)),
        "recall": float(np.mean(recall_scores)),
        "damage": float(np.mean(damage_scores)),
    }
