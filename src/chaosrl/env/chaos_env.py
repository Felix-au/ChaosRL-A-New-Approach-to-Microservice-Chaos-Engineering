"""Gymnasium-compliant Chaos Engineering Environment (ChaosEnv)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import gymnasium as gym
from gymnasium import spaces
import numpy as np

from chaosrl.simulator.engine import SimulatorEngine
from chaosrl.simulator.generator import MicroserviceSystem
from chaosrl.simulator.models import (
    FaultIntensity,
    FaultSpec,
    FaultType,
    TopologyFamily,
)


class ObservationMode(str, Enum):
    BLACK_BOX = "black_box"  # Default: Telemetry + Topology + History
    GRAY_BOX = "gray_box"    # Ablation: Also exposes timeouts and circuit breaker presence


class RewardVariant(str, Enum):
    R1 = "R1"  # Sparse: +1 per newly found weakness
    R2 = "R2"  # Default: R1 - damage penalty - repeat penalty
    R3 = "R3"  # Shaped: R2 + partial degradation bonus


class ChaosEnv(gym.Env):
    """Gymnasium environment for autonomous microservice vulnerability discovery."""

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        num_services: int = 20,
        family: TopologyFamily = TopologyFamily.LAYERED,
        experiment_budget: int = 100,
        obs_mode: ObservationMode = ObservationMode.BLACK_BOX,
        reward_variant: RewardVariant = RewardVariant.R2,
        seed: Optional[int] = 42,
        damage_penalty_weight: float = 0.05,
        repeat_penalty_weight: float = 0.02,
        compound_mode: bool = True,
    ) -> None:
        super().__init__()
        self.num_services = num_services
        self.family = family
        self.experiment_budget = experiment_budget
        self.obs_mode = obs_mode
        self.reward_variant = reward_variant
        self.damage_penalty_weight = damage_penalty_weight
        self.repeat_penalty_weight = repeat_penalty_weight
        self.compound_mode = compound_mode

        self.current_seed = seed if seed is not None else 42
        self.rng = np.random.default_rng(self.current_seed)

        # Pre-build action mapping: target * fault_types * intensities
        self.fault_types = [
            FaultType.CONTAINER_KILL,
            FaultType.NODE_FAILURE,
            FaultType.LATENCY_INJECTION,
            FaultType.PACKET_LOSS,
            FaultType.CPU_STRESS,
            FaultType.DEPENDENCY_ERROR,
        ]
        self.intensities = [FaultIntensity.LOW, FaultIntensity.MEDIUM, FaultIntensity.HIGH]

        self.action_catalog: List[Tuple[int, FaultType, FaultIntensity]] = []
        for svc_id in range(self.num_services):
            for ft in self.fault_types:
                for inten in self.intensities:
                    self.action_catalog.append((svc_id, ft, inten))

        self.num_actions = len(self.action_catalog)
        self.action_space = spaces.Discrete(self.num_actions)

        # Observation space definition
        # Node features: 16 features per node (18 in gray-box)
        num_node_features = 18 if self.obs_mode == ObservationMode.GRAY_BOX else 16
        self.observation_space = spaces.Dict({
            "node_features": spaces.Box(low=0.0, high=100.0, shape=(self.num_services, num_node_features), dtype=np.float32),
            "adjacency": spaces.Box(low=0.0, high=1.0, shape=(self.num_services, self.num_services), dtype=np.float32),
            "global_features": spaces.Box(low=0.0, high=1000.0, shape=(5,), dtype=np.float32),
            "action_mask": spaces.Box(low=0, high=1, shape=(self.num_actions,), dtype=np.int8),
        })

        # History and accounting state
        self.system: Optional[MicroserviceSystem] = None
        self.engine: Optional[SimulatorEngine] = None
        self.current_step = 0
        self.cumulative_damage = 0.0
        self.weaknesses_found_count = 0
        self.history_tested_counts = np.zeros((self.num_services, len(self.fault_types)), dtype=np.float32)
        self.tested_action_history: set[Tuple[int, FaultType]] = set()

        self.reset(seed=self.current_seed)

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """Reset environment to a fresh system and episode."""
        if seed is not None:
            self.current_seed = seed
        else:
            self.current_seed = int(self.rng.integers(0, 100000))

        super().reset(seed=self.current_seed)
        self.system = MicroserviceSystem(
            num_services=self.num_services,
            family=self.family,
            seed=self.current_seed,
        )
        self.engine = SimulatorEngine(self.system)

        self.current_step = 0
        self.cumulative_damage = 0.0
        self.weaknesses_found_count = 0
        self.history_tested_counts.fill(0.0)
        self.tested_action_history.clear()

        obs = self._get_observation()
        info = {
            "num_services": self.num_services,
            "benchmark_total": len(self.system.ground_truth_weaknesses),
            "experiments_left": self.experiment_budget,
        }
        return obs, info

    def step(
        self,
        action: Union[int, List[int]],
    ) -> Tuple[Dict[str, np.ndarray], float, bool, bool, Dict[str, Any]]:
        """Execute one experiment (1 or 2 faults), observe outcome, and compute reward."""
        if self.current_step >= self.experiment_budget:
            raise RuntimeError("Episode already finished. Call reset().")

        # Parse action(s)
        if isinstance(action, (int, np.integer)):
            action_indices = [int(action)]
        else:
            action_indices = [int(a) for a in action][:2]

        fault_specs = []
        is_repeated = False

        for act_idx in action_indices:
            svc_id, ft, inten = self.action_catalog[act_idx]
            fault_specs.append(FaultSpec(fault_type=ft, target_id=svc_id, intensity=inten))

            # Track history and repeat penalty
            ft_idx = self.fault_types.index(ft)
            self.history_tested_counts[svc_id, ft_idx] += 1.0

            if (svc_id, ft) in self.tested_action_history:
                is_repeated = True
            self.tested_action_history.add((svc_id, ft))

        # Execute experiment in simulator
        assert self.engine is not None
        result = self.engine.run_experiment(fault_specs, duration_ticks=15, recovery_ticks=5)

        self.current_step += 1
        self.cumulative_damage += result.cumulative_damage
        num_new_weaknesses = len(result.discovered_weakness_ids)
        self.weaknesses_found_count += num_new_weaknesses

        # Compute Reward
        if self.reward_variant == RewardVariant.R1:
            reward = float(num_new_weaknesses)
        elif self.reward_variant == RewardVariant.R2:
            damage_pen = self.damage_penalty_weight * result.cumulative_damage
            repeat_pen = self.repeat_penalty_weight if is_repeated else 0.0
            reward = float(num_new_weaknesses) - float(damage_pen) - float(repeat_pen)
        else:  # R3: Shaped
            damage_pen = self.damage_penalty_weight * result.cumulative_damage
            repeat_pen = self.repeat_penalty_weight if is_repeated else 0.0
            # Shaping: small bonus for partial latency elevation without full breach
            deg_signal = min(1.0, result.gateway_p99_latency_ms / 500.0) if not result.slo_violated else 0.0
            reward = float(num_new_weaknesses) - float(damage_pen) - float(repeat_pen) + 0.05 * float(deg_signal)

        terminated = self.current_step >= self.experiment_budget
        truncated = False

        obs = self._get_observation()

        # Sanity check: Assert NO ground truth weaknesses leaked in info
        info = {
            "slo_violated": result.slo_violated,
            "newly_found_count": num_new_weaknesses,
            "total_found": self.weaknesses_found_count,
            "cumulative_damage": self.cumulative_damage,
            "experiment_damage": result.cumulative_damage,
            "gateway_p99_ms": result.gateway_p99_latency_ms,
            "gateway_error_rate": result.gateway_error_rate,
            "emergent_violation": result.emergent_violation,
            "step": self.current_step,
            "is_repeated": is_repeated,
        }

        return obs, float(reward), terminated, truncated, info

    def get_action_mask(self) -> np.ndarray:
        """Return boolean mask: 1 for valid actions, 0 for invalid/exhausted actions."""
        mask = np.ones(self.num_actions, dtype=np.int8)
        # Gateway (service 0) cannot be killed directly to avoid trivializing benchmark
        for idx, (svc_id, ft, _) in enumerate(self.action_catalog):
            if svc_id == 0 and ft == FaultType.CONTAINER_KILL:
                mask[idx] = 0
        return mask

    def _get_observation(self) -> Dict[str, np.ndarray]:
        """Construct graph-structured observation without leaking hidden weakness labels."""
        assert self.system is not None and self.engine is not None

        # Node features
        n = self.num_services
        in_degrees = np.sum(self.system.adjacency, axis=0) / max(1.0, n)
        out_degrees = np.sum(self.system.adjacency, axis=1) / max(1.0, n)

        features = []
        for i in range(n):
            svc = self.system.services[i]
            # Runtime telemetry from dynamics baseline
            lat_ratio = float(self.engine.dynamics.base_latency[i] / 20.0)
            err_rate = float(self.engine.dynamics.active_error_fault[i])
            cpu_util = float(self.engine.dynamics.active_cpu_fault[i] * 100.0)
            healthy_rep_frac = float(self.engine.dynamics.healthy_replicas[i] / max(1.0, svc.num_replicas))

            # Structure features
            layer_norm = float(svc.layer / 2.0)
            reps_norm = float(svc.num_replicas / 4.0)
            coloc_count = float(len(svc.assigned_nodes) / max(1.0, self.system.num_nodes))

            # History features: tested count per fault type (summed)
            tested_tot = float(np.sum(self.history_tested_counts[i, :]))

            node_row = [
                lat_ratio,
                err_rate,
                cpu_util,
                healthy_rep_frac,
                in_degrees[i],
                out_degrees[i],
                layer_norm,
                reps_norm,
                coloc_count,
                tested_tot,
                self.history_tested_counts[i, 0],
                self.history_tested_counts[i, 1],
                self.history_tested_counts[i, 2],
                self.history_tested_counts[i, 3],
                self.history_tested_counts[i, 4],
                self.history_tested_counts[i, 5],
            ]

            if self.obs_mode == ObservationMode.GRAY_BOX:
                # Expose static flags strictly in gray-box ablation mode
                node_row.extend([
                    1.0 if svc.has_timeout else 0.0,
                    1.0 if svc.has_circuit_breaker else 0.0,
                ])

            features.append(node_row)

        node_features_arr = np.array(features, dtype=np.float32)

        # Global features
        budget_left_frac = float((self.experiment_budget - self.current_step) / self.experiment_budget)
        damage_norm = float(self.cumulative_damage / 100.0)
        found_count_norm = float(self.weaknesses_found_count / 10.0)
        step_norm = float(self.current_step / self.experiment_budget)
        n_norm = float(self.num_services / 500.0)

        global_features = np.array([
            budget_left_frac,
            damage_norm,
            found_count_norm,
            step_norm,
            n_norm,
        ], dtype=np.float32)

        return {
            "node_features": node_features_arr,
            "adjacency": self.system.adjacency.astype(np.float32),
            "global_features": global_features,
            "action_mask": self.get_action_mask(),
        }
