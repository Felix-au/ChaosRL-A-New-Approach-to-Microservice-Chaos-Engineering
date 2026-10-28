"""Vectorized discrete-time microservice dynamics and SLO evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

from chaosrl.simulator.generator import MicroserviceSystem
from chaosrl.simulator.models import FaultSpec, FaultType, FaultIntensity

CALIB_PARAMS_FILE = Path("results/calibration/fitted_parameters.json")


def load_calibrated_parameters() -> Dict[str, dict]:
    """Load empirical parameters fitted in Stage 2 or fallback to literature bounds."""
    if CALIB_PARAMS_FILE.exists():
        try:
            with open(CALIB_PARAMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Literature fallback bounds
    return {
        "cpu": {"mean": 35.0, "std": 10.0},
        "delay": {"scale": 30.0, "shape": 0.8},
        "loss": {"scale": 4.5, "shape": 0.5},
        "mem": {"scale": 12.0, "shape": 0.6},
        "disk": {"scale": 3.8, "shape": 0.4},
    }


class SystemDynamics:
    """Simulates multi-tick system dynamics, propagation, and SLO evaluation."""

    def __init__(self, system: MicroserviceSystem, noise_std: float = 0.03) -> None:
        self.system = system
        self.n = system.num_services
        self.noise_std = noise_std
        self.calib_params = load_calibrated_parameters()

        # Static vectors
        self.base_latency = np.array([system.services[i].base_latency_ms for i in range(self.n)], dtype=np.float64)
        self.base_capacity = np.array([system.services[i].base_capacity_rps for i in range(self.n)], dtype=np.float64)
        self.total_replicas = np.array([system.services[i].num_replicas for i in range(self.n)], dtype=np.float64)
        self.timeouts = np.array([system.services[i].timeout_ms for i in range(self.n)], dtype=np.float64)
        self.has_cb = np.array([1.0 if system.services[i].has_circuit_breaker else 0.0 for i in range(self.n)], dtype=np.float64)
        self.max_retries = np.array([system.services[i].max_retries for i in range(self.n)], dtype=np.float64)

        # Adjacency matrix: A[u, v] = 1 if u calls v
        self.adj = system.adjacency.copy()
        # Precomputed callee arrays for ultra-fast vectorised backward propagation
        self.callees = [np.where(self.adj[u, :] > 0)[0] for u in range(self.n)]

        # Dynamic state vectors
        self.healthy_replicas = self.total_replicas.copy()
        self.cb_open = np.zeros(self.n, dtype=np.float64)
        self.active_latency_fault = np.zeros(self.n, dtype=np.float64)
        self.active_loss_fault = np.zeros(self.n, dtype=np.float64)
        self.active_cpu_fault = np.zeros(self.n, dtype=np.float64)
        self.active_error_fault = np.zeros(self.n, dtype=np.float64)

        self.reset_state()

    def reset_state(self) -> None:
        """Reset all dynamic faults, circuit breakers, and replicas to healthy baseline."""
        self.healthy_replicas = self.total_replicas.copy()
        self.cb_open.fill(0.0)
        self.active_latency_fault.fill(0.0)
        self.active_loss_fault.fill(0.0)
        self.active_cpu_fault.fill(0.0)
        self.active_error_fault.fill(0.0)

    def apply_fault(self, fault: FaultSpec) -> None:
        """Apply a single fault specification to dynamic state."""
        target = fault.target_id
        intensity = fault.intensity

        # Intensity scale multiplier
        scale = 0.5 if intensity == FaultIntensity.LOW else (1.0 if intensity == FaultIntensity.MEDIUM else 2.0)

        if fault.fault_type == FaultType.CONTAINER_KILL:
            if 0 <= target < self.n:
                kill_count = max(1, int(np.ceil(1.0 * scale)))
                self.healthy_replicas[target] = max(0.0, self.healthy_replicas[target] - kill_count)

        elif fault.fault_type == FaultType.NODE_FAILURE:
            # Kill all replicas residing on this physical node
            node_id = target
            for svc_id, svc in self.system.services.items():
                killed_on_node = sum(1 for nd in svc.assigned_nodes if nd == node_id)
                self.healthy_replicas[svc_id] = max(0.0, self.healthy_replicas[svc_id] - killed_on_node)

        elif fault.fault_type == FaultType.LATENCY_INJECTION:
            if 0 <= target < self.n:
                calib_scale = self.calib_params.get("delay", {}).get("scale", 30.0)
                self.active_latency_fault[target] += (calib_scale * 10.0 * scale)

        elif fault.fault_type == FaultType.PACKET_LOSS:
            if 0 <= target < self.n:
                self.active_loss_fault[target] += min(0.95, 0.25 * scale)

        elif fault.fault_type == FaultType.CPU_STRESS:
            if 0 <= target < self.n:
                calib_cpu = self.calib_params.get("cpu", {}).get("mean", 35.0)
                self.active_cpu_fault[target] += (calib_cpu * 0.02 * scale)

        elif fault.fault_type == FaultType.DEPENDENCY_ERROR:
            if 0 <= target < self.n:
                self.active_error_fault[target] += min(0.95, 0.35 * scale)

    def step_tick(self, ingress_load: float = 100.0, tick: int = 0) -> Dict[str, np.ndarray]:
        """Execute one discrete-time tick of queueing, load propagation, and SLO evaluation."""
        # 1. Ingress traffic at gateway (service 0)
        load = np.zeros(self.n, dtype=np.float64)
        load[0] = ingress_load * (1.0 + self.noise_std * np.random.randn())

        # 2. Downstream traffic propagation with retry amplification
        for u in range(self.n):
            if load[u] > 0:
                downstream = np.where(self.adj[u, :] > 0)[0]
                if len(downstream) > 0:
                    share = load[u] / len(downstream)
                    for v in downstream:
                        # Circuit breaker check: if CB is OPEN, shed traffic
                        if self.cb_open[v] == 1.0:
                            continue
                        # Base call
                        load[v] += share
                        # Retry amplification if v has error or latency
                        err_prob = self.active_error_fault[v] + self.active_loss_fault[v]
                        if err_prob > 0.05 and self.max_retries[u] > 0:
                            retry_mult = 1.0 + 0.5 * self.max_retries[u] * min(1.0, err_prob * 2.0)
                            load[v] += share * (retry_mult - 1.0)

        # 3. Utilization & Queueing Latency
        effective_capacity = self.healthy_replicas * self.base_capacity
        # Effective capacity reduced by CPU stress
        effective_capacity *= np.maximum(0.05, 1.0 - self.active_cpu_fault)

        utilization = np.zeros(self.n, dtype=np.float64)
        pos_cap = effective_capacity > 0
        utilization[pos_cap] = load[pos_cap] / effective_capacity[pos_cap]
        utilization[~pos_cap] = 10.0  # Infinite utilization when no replicas alive

        # Non-linear saturating queueing curve
        rho = np.clip(utilization, 0.0, 0.999)
        queue_multiplier = 1.0 + (rho / (1.0 - rho + 1e-4)) ** 2.0
        # If no replicas alive, latency jumps to timeout
        queue_multiplier[~pos_cap] = 50.0

        p50_latency = self.base_latency * queue_multiplier + self.active_latency_fault
        p99_latency = p50_latency * 1.8 + (p50_latency ** 1.1) * 0.1

        # 4. Error Rates & Timeout Violations
        timeout_mask = p99_latency > self.timeouts
        error_rate = np.clip(
            self.active_error_fault + self.active_loss_fault + (0.8 * timeout_mask) + (1.0 * (~pos_cap)),
            0.0, 1.0
        )

        # 5. Backward Propagation to Callers (Cascading Call Chain Impact)
        # In microservices (Tail at Scale), p99 tail latency is driven by the slowest critical path branch
        # and downstream callee errors propagate upstream to callers
        for u in range(self.n - 1, -1, -1):
            callees = self.callees[u]
            if len(callees) > 0:
                active_callees = callees[self.cb_open[callees] == 0.0]
                if len(active_callees) > 0:
                    max_callee_lat = float(np.max(p99_latency[active_callees]))
                    avg_callee_lat = float(np.mean(p50_latency[active_callees]))
                    callee_err = float(np.mean(error_rate[active_callees]))
                    p99_latency[u] += max_callee_lat * 0.85
                    p50_latency[u] += avg_callee_lat * 0.60
                    error_rate[u] = np.clip(error_rate[u] + callee_err * 0.80, 0.0, 1.0)

        # Circuit breaker trips if error rate > 0.25 and has_cb is True
        trip_mask = (error_rate > 0.25) & (self.has_cb == 1.0)
        self.cb_open[trip_mask] = 1.0
        # Auto-reset circuit breaker after recovery if error drops
        reset_mask = (error_rate < 0.10) & (self.cb_open == 1.0)
        self.cb_open[reset_mask] = 0.0

        # Measurement noise added to observed outputs
        obs_p50 = np.maximum(1.0, p50_latency * (1.0 + self.noise_std * np.random.randn(self.n)))
        obs_p99 = np.maximum(1.0, p99_latency * (1.0 + self.noise_std * np.random.randn(self.n)))
        obs_err = np.clip(error_rate * (1.0 + self.noise_std * np.random.randn(self.n)) + np.abs(0.001 * np.random.randn(self.n)), 0.0, 1.0)
        obs_cpu = np.clip(utilization * 100.0, 0.0, 100.0)

        # Evaluate Gateway SLO
        gw_p99 = float(obs_p99[0])
        gw_err = float(obs_err[0])
        slo_violated = (gw_p99 > 500.0) or (gw_err > 0.02)

        # Damage calculation: severity-weighted duration
        damage_severity = 0.0
        if gw_p99 > 500.0:
            damage_severity += (gw_p99 - 500.0) / 500.0
        if gw_err > 0.02:
            damage_severity += (gw_err - 0.02) / 0.02

        return {
            "p50_latency": obs_p50,
            "p99_latency": obs_p99,
            "error_rate": obs_err,
            "cpu_utilization": obs_cpu,
            "request_rate": load,
            "healthy_replicas": self.healthy_replicas.copy(),
            "gateway_p99_ms": gw_p99,
            "gateway_error_rate": gw_err,
            "slo_violated": slo_violated,
            "damage": float(damage_severity) if slo_violated else 0.0,
        }
