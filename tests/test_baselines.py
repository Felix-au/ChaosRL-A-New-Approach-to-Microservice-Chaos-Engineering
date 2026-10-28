"""Unit tests for Stage 5 baselines."""

import pytest
import numpy as np

from chaosrl.env.chaos_env import ChaosEnv
from chaosrl.simulator.models import FaultType
from chaosrl.agents.baselines.baselines import (
    ChaosMonkeyAgent,
    ChaosMonkey2Agent,
    RandomAllAgent,
    RoundRobinAgent,
    UCBBanditAgent,
    HeuristicExpertAgent,
    OracleAgent,
)


def test_chaos_monkey_only_kills():
    """Verify Chaos Monkey only produces container kill faults."""
    env = ChaosEnv(num_services=20, experiment_budget=20, seed=100001)
    agent = ChaosMonkeyAgent(env)
    obs, _ = env.reset(seed=100001)

    for _ in range(15):
        action = agent.select_action(obs)
        svc_id, ft, inten = env.action_catalog[action]
        assert ft == FaultType.CONTAINER_KILL
        obs, _, term, trunc, _ = env.step(action)
        if term or trunc:
            break


def test_heuristic_expert_no_hidden_leak():
    """Verify Heuristic Expert does not access planted weaknesses."""
    env = ChaosEnv(num_services=20, experiment_budget=20, seed=100002)
    agent = HeuristicExpertAgent(env)
    assert not hasattr(agent, "planted_weaknesses")
    assert not hasattr(agent, "ground_truth_weaknesses")

    obs, _ = env.reset(seed=100002)
    action = agent.select_action(obs)
    if isinstance(action, (list, tuple)):
        assert 0 <= action[0] < len(env.action_catalog)
    else:
        assert 0 <= action < len(env.action_catalog)


def test_all_baselines_run():
    """Verify all 7 baselines step without error."""
    env = ChaosEnv(num_services=20, experiment_budget=10, seed=100003)
    baselines = [
        ChaosMonkeyAgent,
        ChaosMonkey2Agent,
        RandomAllAgent,
        RoundRobinAgent,
        UCBBanditAgent,
        HeuristicExpertAgent,
        OracleAgent,
    ]

    for b_cls in baselines:
        obs, _ = env.reset(seed=100003)
        agent = b_cls(env)
        for _ in range(5):
            act = agent.select_action(obs)
            obs, r, term, trunc, info = env.step(act)
            if hasattr(agent, "update"):
                act_idx = act if isinstance(act, int) else act[0]
                agent.update(act_idx, r)
            if term or trunc:
                break


def test_oracle_targets_planted_weaknesses():
    """Verify Oracle accesses ground truth weaknesses and discovers them."""
    env = ChaosEnv(num_services=20, experiment_budget=20, seed=100004)
    agent = OracleAgent(env)
    obs, _ = env.reset(seed=100004)
    assert len(env.system.ground_truth_weaknesses) > 0

    found_initial = env.weaknesses_found_count
    for _ in range(10):
        act = agent.select_action(obs)
        obs, r, term, trunc, info = env.step(act)
        if term or trunc:
            break

    assert env.weaknesses_found_count > found_initial
