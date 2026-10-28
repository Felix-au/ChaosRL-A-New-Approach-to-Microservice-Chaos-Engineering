"""High-throughput discrete-time execution engine for ChaosRL experiments."""

from __future__ import annotations

import time
from typing import List, Optional, Tuple
import numpy as np

from chaosrl.simulator.dynamics import SystemDynamics
from chaosrl.simulator.generator import MicroserviceSystem
from chaosrl.simulator.models import ExperimentResult, FaultSpec
from chaosrl.simulator.weaknesses import WeaknessMatcher


class SimulatorEngine:
    """Manages system execution, experiment lifecycle, fault rollback, and benchmarking."""

    def __init__(self, system: MicroserviceSystem, noise_std: float = 0.03) -> None:
        self.system = system
        self.dynamics = SystemDynamics(system, noise_std=noise_std)
        self.matcher = WeaknessMatcher(system.ground_truth_weaknesses)
        self.experiment_counter = 0

    def verify_steady_state(self, ticks: int = 20) -> Tuple[bool, float, float]:
        """Verify that a fault-free system operates in steady state meeting the SLO."""
        self.dynamics.reset_state()
        p99_list = []
        err_list = []
        violation_count = 0

        for t in range(ticks):
            step_res = self.dynamics.step_tick(ingress_load=100.0, tick=t)
            p99_list.append(step_res["gateway_p99_ms"])
            err_list.append(step_res["gateway_error_rate"])
            if step_res["slo_violated"]:
                violation_count += 1

        mean_p99 = float(np.mean(p99_list))
        mean_err = float(np.mean(err_list))
        # Steady state holds if at least 95% of ticks meet the SLO
        is_steady = (violation_count / ticks) <= 0.05
        return is_steady, mean_p99, mean_err

    def run_experiment(
        self,
        faults: List[FaultSpec],
        duration_ticks: int = 20,
        recovery_ticks: int = 10,
    ) -> ExperimentResult:
        """Execute one complete chaos experiment:

        1. Inject fault set
        2. Simulate active duration ticks
        3. Record damage and SLO breach
        4. Rollback faults
        5. Simulate recovery ticks
        6. Evaluate weakness matching
        """
        self.experiment_counter += 1
        self.dynamics.reset_state()

        for f in faults:
            self.dynamics.apply_fault(f)

        slo_violated_any = False
        cumulative_damage = 0.0
        p99_records = []
        err_records = []

        # Active fault phase
        for t in range(duration_ticks):
            res = self.dynamics.step_tick(ingress_load=100.0, tick=t)
            p99_records.append(res["gateway_p99_ms"])
            err_records.append(res["gateway_error_rate"])
            if res["slo_violated"]:
                slo_violated_any = True
                cumulative_damage += res["damage"]

        # Rollback phase
        self.dynamics.reset_state()

        # Recovery phase
        for t in range(recovery_ticks):
            self.dynamics.step_tick(ingress_load=100.0, tick=duration_ticks + t)

        # Match weaknesses
        newly_found, is_emergent = self.matcher.evaluate_experiment(faults, slo_violated_any)

        return ExperimentResult(
            experiment_id=self.experiment_counter,
            faults=faults,
            slo_violated=slo_violated_any,
            gateway_p99_latency_ms=float(np.mean(p99_records)),
            gateway_error_rate=float(np.mean(err_records)),
            cumulative_damage=float(cumulative_damage),
            discovered_weakness_ids=newly_found,
            emergent_violation=is_emergent,
            duration_ticks=duration_ticks,
        )


def benchmark_engine_throughput(
    num_services: int,
    num_experiments: int = 100,
    seed: int = 42,
) -> float:
    """Benchmark simulator throughput in experiments per minute."""
    sys = MicroserviceSystem(num_services=num_services, seed=seed)
    engine = SimulatorEngine(sys)

    # Pre-generate simple fault for testing
    from chaosrl.simulator.models import FaultType, FaultIntensity
    fault = [FaultSpec(fault_type=FaultType.CONTAINER_KILL, target_id=1, intensity=FaultIntensity.MEDIUM)]

    start_time = time.perf_counter()
    for _ in range(num_experiments):
        engine.run_experiment(fault, duration_ticks=15, recovery_ticks=5)
    elapsed_sec = time.perf_counter() - start_time

    experiments_per_min = (num_experiments / elapsed_sec) * 60.0
    return float(experiments_per_min)
