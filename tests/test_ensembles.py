"""Unit tests for Stage 8 meta-ensembles."""

import numpy as np
import pytest

from chaosrl.agents.candidates.registry import get_candidate
from chaosrl.agents.ensemble.ensembles import (
    BordaRankEnsemble,
    GatedControllerEnsemble,
    SoftVoteEnsemble,
)
from chaosrl.env.chaos_env import ChaosEnv


@pytest.fixture
def mock_candidates():
    c01 = get_candidate("C01")
    c02 = get_candidate("C02")
    c05 = get_candidate("C05")
    c10 = get_candidate("C10")
    c11 = get_candidate("C11")
    return [c01, c02, c05, c10, c11]


def test_soft_vote_respects_mask(mock_candidates):
    """Verify Soft Vote ensemble only selects valid actions."""
    env = ChaosEnv(num_services=20, experiment_budget=10, seed=101)
    obs, _ = env.reset(seed=101)
    ensemble = SoftVoteEnsemble(mock_candidates)

    for _ in range(5):
        act = ensemble.select_action(obs, deterministic=True)
        assert obs["action_mask"][act] == 1
        obs, _, term, trunc, _ = env.step(act)
        if term or trunc:
            break


def test_borda_rank_respects_mask(mock_candidates):
    """Verify Borda Rank ensemble only selects valid actions."""
    env = ChaosEnv(num_services=20, experiment_budget=10, seed=102)
    obs, _ = env.reset(seed=102)
    ensemble = BordaRankEnsemble(mock_candidates, top_k=15)

    for _ in range(5):
        act = ensemble.select_action(obs, deterministic=True)
        assert obs["action_mask"][act] == 1
        obs, _, term, trunc, _ = env.step(act)
        if term or trunc:
            break


def test_gated_controller_execution(mock_candidates):
    """Verify Gated Controller routes and selects valid actions."""
    env = ChaosEnv(num_services=20, experiment_budget=10, seed=103)
    obs, _ = env.reset(seed=103)
    ensemble = GatedControllerEnsemble(mock_candidates)

    # Fit gate with dummy data
    X_meta = np.random.randn(20, 21)
    y_gate = np.random.randint(0, len(mock_candidates), 20)
    ensemble.fit_gate(X_meta, y_gate)

    for _ in range(5):
        act = ensemble.select_action(obs, deterministic=True)
        assert obs["action_mask"][act] == 1
        obs, _, term, trunc, _ = env.step(act)
        if term or trunc:
            break


def test_ensemble_topology_invariance(mock_candidates):
    """Verify ensembles seamlessly scale from N=20 to N=100 without modification."""
    ensemble = SoftVoteEnsemble(mock_candidates)
    for n in [20, 100]:
        env = ChaosEnv(num_services=n, experiment_budget=5, seed=200)
        obs, _ = env.reset(seed=200)
        act = ensemble.select_action(obs)
        assert 0 <= act < len(env.action_catalog)
        assert obs["action_mask"][act] == 1
