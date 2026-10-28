"""Candidate model registry mapping candidate IDs C01..C12 to factory functions."""

from __future__ import annotations

from typing import Any, Callable, Dict, Type

from chaosrl.agents.candidates.base_candidate import BaseCandidateAgent
from chaosrl.agents.candidates.ppo_agents import (
    BCPPOAgent,
    CurriculumPPOAgent,
    PPOAgent,
    PPORNDAgent,
)
from chaosrl.agents.candidates.classic_rl_agents import (
    A2CAgent,
    DQNAgent,
    REINFORCEAgent,
)
from chaosrl.agents.candidates.alternative_agents import (
    ESAgent,
    LinUCBBanditAgent,
    SupervisedRankerAgent,
)


CANDIDATE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "C01": {
        "id": "C01",
        "name": "PPO-MLP",
        "family": "policy_gradient",
        "factory": lambda **kw: PPOAgent(candidate_id="C01", name="PPO-MLP", scorer_type="mlp", **kw),
        "description": "Proximal Policy Optimization with per-node MLP scorer",
    },
    "C02": {
        "id": "C02",
        "name": "PPO-GNN",
        "family": "structure_aware",
        "factory": lambda **kw: PPOAgent(candidate_id="C02", name="PPO-GNN", scorer_type="gnn", **kw),
        "description": "Proximal Policy Optimization with 2-layer Graph Convolutional Network",
    },
    "C03": {
        "id": "C03",
        "name": "PPO-GRU",
        "family": "recurrent",
        "factory": lambda **kw: PPOAgent(candidate_id="C03", name="PPO-GRU", scorer_type="gru", **kw),
        "description": "Recurrent PPO with GRU cell tracking injection history",
    },
    "C04": {
        "id": "C04",
        "name": "A2C",
        "family": "policy_gradient",
        "factory": lambda **kw: A2CAgent(**kw),
        "description": "Synchronous Advantage Actor-Critic",
    },
    "C05": {
        "id": "C05",
        "name": "DQN-Dueling",
        "family": "value_based",
        "factory": lambda **kw: DQNAgent(**kw),
        "description": "Dueling Double Deep Q-Network with replay buffer",
    },
    "C06": {
        "id": "C06",
        "name": "REINFORCE",
        "family": "policy_gradient",
        "factory": lambda **kw: REINFORCEAgent(**kw),
        "description": "Monte Carlo Policy Gradient with learned baseline",
    },
    "C07": {
        "id": "C07",
        "name": "Curriculum-PPO",
        "family": "curriculum",
        "factory": lambda **kw: CurriculumPPOAgent(**kw),
        "description": "Curriculum learning transferring from scale 20 to 100",
    },
    "C08": {
        "id": "C08",
        "name": "BC-PPO",
        "family": "imitation",
        "factory": lambda **kw: BCPPOAgent(**kw),
        "description": "Behavioral Cloning warm-start on Heuristic Expert + PPO",
    },
    "C09": {
        "id": "C09",
        "name": "PPO-RND",
        "family": "exploration",
        "factory": lambda **kw: PPORNDAgent(**kw),
        "description": "PPO with Random Network Distillation novelty bonus",
    },
    "C10": {
        "id": "C10",
        "name": "ES-Policy",
        "family": "gradient_free",
        "factory": lambda **kw: ESAgent(**kw),
        "description": "Natural Evolutionary Strategy parameter optimization",
    },
    "C11": {
        "id": "C11",
        "name": "LinUCB-Contextual",
        "family": "bandit",
        "factory": lambda **kw: LinUCBBanditAgent(**kw),
        "description": "Contextual Linear Bandit with per-fault ridge regression",
    },
    "C12": {
        "id": "C12",
        "name": "TreeRanker",
        "family": "supervised",
        "factory": lambda **kw: SupervisedRankerAgent(**kw),
        "description": "Random Forest ranking model predicting weakness discovery",
    },
}


def get_candidate(candidate_id: str, **kwargs: Any) -> BaseCandidateAgent:
    """Instantiate a candidate by ID."""
    if candidate_id not in CANDIDATE_REGISTRY:
        raise KeyError(f"Unknown candidate ID: {candidate_id}. Registered: {list(CANDIDATE_REGISTRY.keys())}")
    return CANDIDATE_REGISTRY[candidate_id]["factory"](**kwargs)
