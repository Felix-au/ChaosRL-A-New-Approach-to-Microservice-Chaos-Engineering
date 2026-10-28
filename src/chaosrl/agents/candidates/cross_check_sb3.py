"""Cross-check validation comparing ChaosRL PPO against sb3-contrib MaskablePPO."""

from __future__ import annotations

from typing import Any, Dict
import gymnasium as gym
import numpy as np
import torch
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from chaosrl.agents.candidates.ppo_agents import PPOAgent
from chaosrl.docs_tools.facts_registry import register_fact
from chaosrl.env.chaos_env import ChaosEnv

torch.set_num_threads(1)


class SB3ChaosWrapper(gym.Env):
    """Wrapper exposing flat box observation and action masks for SB3."""

    def __init__(self, num_services: int = 20, budget: int = 50, seed: int = 42) -> None:
        super().__init__()
        self.raw_env = ChaosEnv(num_services=num_services, experiment_budget=budget, seed=seed)
        self.action_space = gym.spaces.Discrete(len(self.raw_env.action_catalog))

        # Flatten node features + global features for flat SB3 MLP
        obs_dim = num_services * 16 + 5
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )
        self.current_mask = np.ones(self.action_space.n, dtype=np.int8)

    def action_masks(self) -> np.ndarray:
        return self.current_mask.astype(bool)

    def _flatten_obs(self, obs: Dict[str, np.ndarray]) -> np.ndarray:
        return np.concatenate([obs["node_features"].flatten(), obs["global_features"]]).astype(np.float32)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        obs, info = self.raw_env.reset(seed=seed, options=options)
        self.current_mask = obs["action_mask"].astype(np.int8)
        return self._flatten_obs(obs), info

    def step(self, action: int):
        obs, reward, term, trunc, info = self.raw_env.step(action)
        self.current_mask = obs["action_mask"].astype(np.int8)
        return self._flatten_obs(obs), reward, term, trunc, info


def mask_fn(env: gym.Env) -> np.ndarray:
    return env.unwrapped.action_masks()


def run_sb3_cross_check(num_services: int = 20, steps: int = 300) -> Dict[str, Any]:
    """Run comparative check between custom PPO-MLP and SB3-contrib MaskablePPO."""
    print(f"Running cross-check: Custom PPO vs SB3 MaskablePPO (N={num_services}, steps={steps})...")

    # 1. Train Custom PPO
    custom_agent = PPOAgent(candidate_id="C01", name="PPO-MLP", scorer_type="mlp")
    train_env = ChaosEnv(num_services=num_services, experiment_budget=steps, seed=12345)
    obs, _ = train_env.reset(seed=12345)

    traj: Dict[str, list] = {"obs": [], "actions": [], "rewards": [], "dones": [], "log_probs": [], "values": []}
    for _ in range(steps):
        act = custom_agent.select_action(obs)
        lp, val, _ = custom_agent.evaluate_step(obs, act)
        next_obs, rew, term, trunc, _ = train_env.step(act)
        done = term or trunc

        traj["obs"].append(obs)
        traj["actions"].append(act)
        traj["rewards"].append(rew)
        traj["dones"].append(float(done))
        traj["log_probs"].append(lp)
        traj["values"].append(val)
        obs = next_obs

        if len(traj["rewards"]) >= 64 or done:
            custom_agent.update_on_trajectories([traj], epochs=4)
            traj = {"obs": [], "actions": [], "rewards": [], "dones": [], "log_probs": [], "values": []}
        if done:
            obs, _ = train_env.reset()

    # 2. Train SB3 MaskablePPO
    raw_env = SB3ChaosWrapper(num_services=num_services, budget=steps, seed=12345)
    masked_env = ActionMasker(raw_env, mask_fn)
    sb3_model = MaskablePPO("MlpPolicy", masked_env, verbose=0, n_steps=64, batch_size=32)
    sb3_model.learn(total_timesteps=steps)

    # 3. Evaluate Both on Identical Held-Out Validation Environment
    eval_steps = 50
    eval_env_custom = ChaosEnv(num_services=num_services, experiment_budget=eval_steps, seed=54321)
    eval_env_sb3 = SB3ChaosWrapper(num_services=num_services, budget=eval_steps, seed=54321)

    custom_rewards = []
    obs, _ = eval_env_custom.reset(seed=54321)
    for _ in range(eval_steps):
        act = custom_agent.select_action(obs, deterministic=True)
        obs, rew, term, trunc, _ = eval_env_custom.step(act)
        custom_rewards.append(rew)
        if term or trunc:
            break

    sb3_rewards = []
    sb3_obs, _ = eval_env_sb3.reset(seed=54321)
    for _ in range(eval_steps):
        masks = eval_env_sb3.action_masks()
        act, _ = sb3_model.predict(sb3_obs, action_masks=masks, deterministic=True)
        sb3_obs, rew, term, trunc, _ = eval_env_sb3.step(int(act))
        sb3_rewards.append(rew)
        if term or trunc:
            break

    custom_mean_rew = float(np.mean(custom_rewards))
    sb3_mean_rew = float(np.mean(sb3_rewards))
    abs_diff = abs(custom_mean_rew - sb3_mean_rew)

    print(f"Evaluated Custom PPO mean reward: {custom_mean_rew:.4f}")
    print(f"Evaluated SB3 MaskablePPO mean reward: {sb3_mean_rew:.4f}")
    print(f"Absolute reward difference: {abs_diff:.4f}")

    register_fact("candidates.cross_check_diff", round(abs_diff, 4), unit="reward", source_file="src/chaosrl/agents/candidates/cross_check_sb3.py")
    register_fact("candidates.custom_ppo_reward", round(custom_mean_rew, 4), unit="reward", source_file="src/chaosrl/agents/candidates/cross_check_sb3.py")
    register_fact("candidates.sb3_ppo_reward", round(sb3_mean_rew, 4), unit="reward", source_file="src/chaosrl/agents/candidates/cross_check_sb3.py")

    return {
        "custom_ppo_mean_reward": custom_mean_rew,
        "sb3_ppo_mean_reward": sb3_mean_rew,
        "reward_difference": abs_diff,
        "check_passed": abs_diff < 1.0,
    }
