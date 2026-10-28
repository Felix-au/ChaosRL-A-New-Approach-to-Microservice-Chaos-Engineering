"""Unit tests for Stage 6 Candidate Pool (C01 through C12)."""

import tempfile
from pathlib import Path
import numpy as np
import pytest
import torch

from chaosrl.agents.candidates.registry import CANDIDATE_REGISTRY, get_candidate
from chaosrl.env.chaos_env import ChaosEnv


def test_candidate_registry_completeness():
    """Verify all 12 specified candidates are registered."""
    assert len(CANDIDATE_REGISTRY) == 12
    for i in range(1, 13):
        cid = f"C{i:02d}"
        assert cid in CANDIDATE_REGISTRY


@pytest.mark.parametrize("cid", [f"C{i:02d}" for i in range(1, 13)])
def test_candidate_select_valid_action(cid: str):
    """Verify each candidate selects valid actions obeying action mask."""
    env = ChaosEnv(num_services=20, experiment_budget=10, seed=42)
    agent = get_candidate(cid)
    obs, _ = env.reset(seed=42)

    action = agent.select_action(obs)
    if isinstance(action, (list, tuple)):
        action = action[0]

    assert isinstance(action, (int, np.integer))
    assert 0 <= action < len(env.action_catalog)
    assert obs["action_mask"][action] == 1


def test_topology_invariance():
    """Verify scorer models run without modification across different system sizes."""
    agent_mlp = get_candidate("C01")
    agent_gnn = get_candidate("C02")

    for n in [20, 50, 100]:
        env = ChaosEnv(num_services=n, experiment_budget=5, seed=100)
        obs, _ = env.reset(seed=100)

        act_mlp = agent_mlp.select_action(obs)
        act_gnn = agent_gnn.select_action(obs)

        assert 0 <= act_mlp < len(env.action_catalog)
        assert 0 <= act_gnn < len(env.action_catalog)


def test_candidate_save_and_load():
    """Verify candidate save and load cycle preserves parameters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = get_candidate("C01")
        save_path = Path(tmpdir) / "c01_test.pt"
        agent.save(save_path)
        assert save_path.exists()

        new_agent = get_candidate("C01")
        new_agent.load(save_path)

        # Check actor weights match
        for p1, p2 in zip(agent.actor.parameters(), new_agent.actor.parameters()):
            assert torch.allclose(p1, p2)
