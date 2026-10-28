"""Baseline chaos engineering agents (Chaos Monkey, Random, Round-Robin, UCB, Heuristic, Oracle)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from chaosrl.env.chaos_env import ChaosEnv
from chaosrl.simulator.models import FaultIntensity, FaultSpec, FaultType


class ChaosMonkeyAgent:
    """Faithful Netflix Chaos Monkey: uniform random container kill, single fault only."""

    def __init__(self, env: ChaosEnv) -> None:
        self.env = env
        self.kill_actions = [
            idx for idx, (svc_id, ft, inten) in enumerate(env.action_catalog)
            if ft == FaultType.CONTAINER_KILL and inten == FaultIntensity.MEDIUM
        ]

    def select_action(self, obs: Dict[str, np.ndarray]) -> int:
        mask = obs["action_mask"]
        valid = [a for a in self.kill_actions if a < len(mask) and mask[a] == 1]
        if valid:
            return int(np.random.choice(valid))
        fallback = np.where(mask == 1)[0]
        return int(fallback[0]) if len(fallback) > 0 else 0


class ChaosMonkey2Agent:
    """Chaos Monkey-2: Uniform random 2-container kill."""

    def __init__(self, env: ChaosEnv) -> None:
        self.env = env
        self.kill_actions = [
            idx for idx, (svc_id, ft, inten) in enumerate(env.action_catalog)
            if ft == FaultType.CONTAINER_KILL
        ]

    def select_action(self, obs: Dict[str, np.ndarray]) -> List[int]:
        mask = obs["action_mask"]
        valid = [a for a in self.kill_actions if a < len(mask) and mask[a] == 1]
        if len(valid) >= 2:
            return [int(x) for x in np.random.choice(valid, size=2, replace=False)]
        elif valid:
            return [int(valid[0])]
        fallback = np.where(mask == 1)[0]
        return [int(fallback[0])] if len(fallback) > 0 else [0]


class RandomAllAgent:
    """Random-All: Uniform over all valid actions; second fault with prob 0.5."""

    def __init__(self, env: ChaosEnv) -> None:
        self.env = env

    def select_action(self, obs: Dict[str, np.ndarray]) -> List[int]:
        mask = obs["action_mask"]
        valid = np.where(mask == 1)[0]
        if len(valid) == 0:
            return [0]

        a1 = int(np.random.choice(valid))
        if np.random.random() < 0.5 and len(valid) > 1:
            # Pick distinct second action
            remaining = valid[valid != a1]
            a2 = int(np.random.choice(remaining)) if len(remaining) > 0 else a1
            return [a1, a2]
        return [a1]


class RoundRobinAgent:
    """Round-robin systematic sweep over (service, fault_type)."""

    def __init__(self, env: ChaosEnv) -> None:
        self.env = env
        self.cursor = 0

    def select_action(self, obs: Dict[str, np.ndarray]) -> int:
        mask = obs["action_mask"]
        n_act = self.env.num_actions
        for _ in range(n_act):
            action = self.cursor % n_act
            self.cursor += 1
            if mask[action] == 1:
                return action
        return 0


class UCBBanditAgent:
    """Upper Confidence Bound (UCB) multi-armed bandit over action candidates."""

    def __init__(self, env: ChaosEnv, c: float = 1.414) -> None:
        self.env = env
        self.c = c
        self.counts = np.zeros(env.num_actions, dtype=np.float64)
        self.values = np.zeros(env.num_actions, dtype=np.float64)
        self.total_pulls = 0

    def select_action(self, obs: Dict[str, np.ndarray]) -> int:
        mask = obs["action_mask"]
        valid = np.where(mask == 1)[0]
        if len(valid) == 0:
            return 0

        self.total_pulls += 1
        # Unpulled arms first
        unpulled = [a for a in valid if self.counts[a] == 0]
        if unpulled:
            action = int(np.random.choice(unpulled))
            return action

        # UCB formula
        log_total = np.log(self.total_pulls)
        ucb_scores = self.values[valid] + self.c * np.sqrt(log_total / self.counts[valid])
        best_idx = np.argmax(ucb_scores)
        return int(valid[best_idx])

    def update(self, action: int, reward: float, obs: Any = None) -> None:
        self.counts[action] += 1.0
        n = self.counts[action]
        self.values[action] += (reward - self.values[action]) / n


class HeuristicExpertAgent:
    """Topology-aware heuristic expert: targets hubs, single-replica, and co-located nodes."""

    def __init__(self, env: ChaosEnv) -> None:
        self.env = env
        self.step_count = 0

    def select_action(self, obs: Dict[str, np.ndarray]) -> List[int]:
        self.step_count += 1
        mask = obs["action_mask"]
        node_feats = obs["node_features"]
        n = node_feats.shape[0]

        # Extract topological priorities
        in_degrees = node_feats[:, 4]
        single_replica = (node_feats[:, 7] <= 0.25)
        co_located = (node_feats[:, 8] >= 0.10)

        # Ranked candidate services
        priority_scores = in_degrees * 2.0 + single_replica.astype(float) * 1.5 + co_located.astype(float) * 1.0
        ranked_services = np.argsort(priority_scores)[::-1]

        # Alternate between container kill, latency injection, and node failure
        svc_target = int(ranked_services[(self.step_count // 3) % n])
        if svc_target == 0 and n > 1:
            svc_target = 1  # Avoid masked gateway kill

        ft = [FaultType.CONTAINER_KILL, FaultType.LATENCY_INJECTION, FaultType.NODE_FAILURE][self.step_count % 3]

        # Match action in catalog
        matching = [
            idx for idx, (s, f, inten) in enumerate(self.env.action_catalog)
            if s == svc_target and f == ft and idx < len(mask) and mask[idx] == 1
        ]
        if matching:
            a1 = matching[0]
        else:
            valid = np.where(mask == 1)[0]
            a1 = int(valid[0]) if len(valid) > 0 else 0

        # With 50% probability select compound pair
        if self.step_count % 2 == 0 and len(ranked_services) > 1:
            svc2 = int(ranked_services[(self.step_count // 3 + 1) % n])
            matching2 = [
                idx for idx, (s, f, inten) in enumerate(self.env.action_catalog)
                if s == svc2 and f == FaultType.CPU_STRESS and idx < len(mask) and mask[idx] == 1
            ]
            if matching2 and matching2[0] != a1:
                return [a1, matching2[0]]

        return [a1]


class OracleAgent:
    """Oracle (reference upper bound): knows hidden weaknesses and reveals them systematically."""

    def __init__(self, env: ChaosEnv) -> None:
        self.env = env
        self.targeted_weakness_idx = 0

    def select_action(self, obs: Dict[str, np.ndarray]) -> List[int]:
        mask = obs["action_mask"]
        assert self.env.system is not None
        weaknesses = self.env.system.ground_truth_weaknesses
        undiscovered = [w for w in weaknesses if not w.discovered]

        if not undiscovered:
            valid = np.where(mask == 1)[0]
            return [int(valid[0])] if len(valid) > 0 else [0]

        target_w = undiscovered[0]
        chosen_actions = []

        if not target_w.is_compound:
            req_type = target_w.required_fault_types[0]
            if target_w.weakness_type == "colocated_critical_node":
                node_id = target_w.required_nodes[0] if target_w.required_nodes else 0
                matching = [
                    idx for idx, (s, f, inten) in enumerate(self.env.action_catalog)
                    if f == FaultType.NODE_FAILURE and s == node_id and inten == FaultIntensity.HIGH and mask[idx] == 1
                ]
            else:
                svc_id = target_w.target_service_ids[0]
                matching = [
                    idx for idx, (s, f, inten) in enumerate(self.env.action_catalog)
                    if s == svc_id and f == req_type and inten == FaultIntensity.HIGH and mask[idx] == 1
                ]

            if not matching:
                matching = [idx for idx, (s, f, _) in enumerate(self.env.action_catalog) if mask[idx] == 1]
            if matching:
                chosen_actions.append(matching[0])
        else:
            # Compound weakness
            for i, svc_id in enumerate(target_w.target_service_ids[:2]):
                req_type = target_w.required_fault_types[min(i, len(target_w.required_fault_types) - 1)]
                matching = [
                    idx for idx, (s, f, inten) in enumerate(self.env.action_catalog)
                    if s == svc_id and f == req_type and inten == FaultIntensity.HIGH and mask[idx] == 1
                ]
                if not matching:
                    matching = [idx for idx, (s, f, _) in enumerate(self.env.action_catalog) if s == svc_id and mask[idx] == 1]
                if matching and matching[0] not in chosen_actions:
                    chosen_actions.append(matching[0])

        if not chosen_actions:
            valid = np.where(mask == 1)[0]
            return [int(valid[0])] if len(valid) > 0 else [0]

        return chosen_actions

