"""Unit tests for Gymnasium ChaosEnv environment compliance and leak prevention."""

import numpy as np
import pytest

from chaosrl.env.chaos_env import ChaosEnv, ObservationMode, RewardVariant


def test_gym_api_compliance():
    """Verify Gymnasium API compliance: reset, step, shapes, and terminated flag."""
    env = ChaosEnv(num_services=20, experiment_budget=15, seed=42)
    obs, info = env.reset(seed=42)

    assert "node_features" in obs
    assert "adjacency" in obs
    assert "global_features" in obs
    assert "action_mask" in obs
    assert obs["node_features"].shape == (20, 16)
    assert obs["adjacency"].shape == (20, 20)
    assert obs["global_features"].shape == (5,)
    assert obs["action_mask"].shape == (env.num_actions,)

    # Run 15 steps
    for step in range(15):
        mask = obs["action_mask"]
        valid_actions = np.where(mask == 1)[0]
        action = int(np.random.choice(valid_actions))
        obs, reward, terminated, truncated, info = env.step(action)
        assert isinstance(reward, float)
        assert isinstance(info, dict)
        if step == 14:
            assert terminated, "Episode must terminate after exact budget"
        else:
            assert not terminated


def test_no_hidden_information_leak():
    """CRITICAL TEST: Verify planted weaknesses never leak into observation or info."""
    env = ChaosEnv(num_services=30, seed=777)
    obs, info = env.reset(seed=777)

    # Check reset obs and info
    for key, val in obs.items():
        assert "weakness" not in key.lower()
        assert "ground_truth" not in key.lower()
    for key, val in info.items():
        assert "target_service_ids" not in key
        assert "required_fault_types" not in key
        assert "planted_weaknesses" not in key

    # Check step obs and info
    obs, r, term, trunc, info = env.step(0)
    for key in info.keys():
        assert "ground_truth" not in key.lower()
        assert "target_services" not in key.lower()

    # Verify that node_features contain only normalized physical telemetry
    node_feats = obs["node_features"]
    assert np.all(np.isfinite(node_feats))
    # In black-box mode, static flags must NOT appear
    assert node_feats.shape[1] == 16


def test_action_mask_validity():
    """Verify action mask correctly blocks illegal actions (e.g., gateway kill)."""
    env = ChaosEnv(num_services=20, seed=101)
    mask = env.get_action_mask()
    assert mask.shape[0] == env.num_actions

    # Verify service 0 (gateway) container_kill is masked out
    for idx, (svc_id, ft, _) in enumerate(env.action_catalog):
        if svc_id == 0 and ft.value == "container_kill":
            assert mask[idx] == 0, f"Action {idx} (gateway kill) must have mask 0"


def test_observation_scaling_linear():
    """Verify observation node features scale exactly as O(N)."""
    for n in [10, 50, 100]:
        env = ChaosEnv(num_services=n, seed=42)
        obs, _ = env.reset(seed=42)
        assert obs["node_features"].shape == (n, 16)
        assert obs["node_features"].size == 16 * n


def test_random_policy_stability():
    """Assert a random policy runs multiple episodes without error."""
    env = ChaosEnv(num_services=15, experiment_budget=10, seed=999)
    for ep in range(10):
        obs, _ = env.reset(seed=999 + ep)
        done = False
        while not done:
            mask = obs["action_mask"]
            action = int(np.random.choice(np.where(mask == 1)[0]))
            obs, r, term, trunc, info = env.step(action)
            done = term or trunc

