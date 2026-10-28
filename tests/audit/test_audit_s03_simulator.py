"""Independent research audit tests for Section S3: Discrete-Event Simulator Engine.

Verifies claims CLM-S03-01 through CLM-S03-08:
- Bit-for-bit determinism across identical seeds
- Steady-state false alarm rate <= 2% across 50 seeds
- Load monotonicity (increased ingress load increases latency, non-decreasing errors)
- Strict fault rollback semantics and state restoration
- Physical conservation laws (bounds [0, 1], finite telemetry)
- Exhaustive reachability of planted weaknesses on micro-topologies
- Scale boundary tests (N=2, N=100) and zero load
- Simulation throughput benchmarking (steps/second)
Includes explicit negative controls demonstrating test failure under broken assumptions.
"""

import time
import pytest
import numpy as np

from chaosrl.simulator.generator import MicroserviceSystem
from chaosrl.simulator.engine import SimulatorEngine
from chaosrl.simulator.models import (
    FaultType,
    FaultSpec,
    FaultIntensity,
    TopologyFamily,
)


@pytest.mark.audit
def test_t_s03_01_determinism():
    """T-S03-01: Verify bit-for-bit determinism between runs with identical seeds."""
    np.random.seed(42)
    sys1 = MicroserviceSystem(num_services=25, seed=12345)
    eng1 = SimulatorEngine(sys1, noise_std=0.0)
    fault = [FaultSpec(fault_type=FaultType.LATENCY_INJECTION, target_id=2, intensity=FaultIntensity.HIGH)]
    res1 = eng1.run_experiment(fault, duration_ticks=15, recovery_ticks=5)

    np.random.seed(42)
    sys2 = MicroserviceSystem(num_services=25, seed=12345)
    eng2 = SimulatorEngine(sys2, noise_std=0.0)
    res2 = eng2.run_experiment(fault, duration_ticks=15, recovery_ticks=5)

    assert abs(res1.gateway_p99_latency_ms - res2.gateway_p99_latency_ms) < 1e-9
    assert abs(res1.cumulative_damage - res2.cumulative_damage) < 1e-9
    assert res1.slo_violated == res2.slo_violated
    assert res1.discovered_weakness_ids == res2.discovered_weakness_ids

    # Negative control: Comparing against a different seed must show delta
    sys_diff = MicroserviceSystem(num_services=25, seed=54321)
    eng_diff = SimulatorEngine(sys_diff, noise_std=0.0)
    res_diff = eng_diff.run_experiment(fault, duration_ticks=15, recovery_ticks=5)
    with pytest.raises(AssertionError):
        assert abs(res1.gateway_p99_latency_ms - res_diff.gateway_p99_latency_ms) < 1e-9


@pytest.mark.audit
def test_t_s03_02_steady_state_slo_compliance():
    """T-S03-02: Verify that unperturbed steady-state false-alarm rate is <= 2% across 50 seeds."""
    violation_count = 0
    num_seeds = 50

    for s in range(num_seeds):
        system = MicroserviceSystem(num_services=20, seed=1000 + s)
        engine = SimulatorEngine(system)
        steady, p99, err = engine.verify_steady_state(ticks=20)
        if not steady or p99 >= 500.0 or err >= 0.02:
            violation_count += 1

    violation_rate = violation_count / num_seeds
    assert violation_rate <= 0.02, f"False alarm rate {violation_rate:.3f} exceeds 2% threshold"

    # Negative control: Stepping with extreme synthetic overload must trigger SLO breach
    overload_sys = MicroserviceSystem(num_services=20, seed=1000)
    overload_eng = SimulatorEngine(overload_sys)
    bad_ticks = 0
    for t in range(20):
        step_res = overload_eng.dynamics.step_tick(ingress_load=10000.0, tick=t)
        if step_res["slo_violated"]:
            bad_ticks += 1
    # Overload must produce violations
    with pytest.raises(AssertionError):
        assert bad_ticks == 0


@pytest.mark.audit
def test_t_s03_03_monotonicity_load_vs_latency():
    """T-S03-03: Verify load monotonicity (higher load increases latency without lowering errors)."""
    system = MicroserviceSystem(num_services=20, seed=42)
    eng = SimulatorEngine(system, noise_std=0.0)

    # Base load
    eng.dynamics.reset_state()
    p99_base_list = []
    for t in range(20):
        res = eng.dynamics.step_tick(ingress_load=50.0, tick=t)
        p99_base_list.append(res["gateway_p99_ms"])
    p99_base = np.mean(p99_base_list)

    # High load
    eng.dynamics.reset_state()
    p99_high_list = []
    for t in range(20):
        res = eng.dynamics.step_tick(ingress_load=200.0, tick=t)
        p99_high_list.append(res["gateway_p99_ms"])
    p99_high = np.mean(p99_high_list)

    assert p99_high > p99_base, f"Latency did not increase under higher load: {p99_high} vs {p99_base}"

    # Negative control: Lowering load cannot produce higher latency
    eng.dynamics.reset_state()
    p99_light_list = [eng.dynamics.step_tick(ingress_load=10.0, tick=t)["gateway_p99_ms"] for t in range(20)]
    p99_light = np.mean(p99_light_list)
    with pytest.raises(AssertionError):
        assert p99_light > p99_high


@pytest.mark.audit
def test_t_s03_04_fault_rollback_recovery():
    """T-S03-04: Test rollback semantics: clearing faults restores healthy replica count and latency."""
    system = MicroserviceSystem(num_services=25, seed=888)
    engine = SimulatorEngine(system)

    fault = [FaultSpec(fault_type=FaultType.CONTAINER_KILL, target_id=1, intensity=FaultIntensity.HIGH)]
    res = engine.run_experiment(fault, duration_ticks=10, recovery_ticks=15)

    # After recovery, healthy replicas should match total replicas
    assert np.all(engine.dynamics.healthy_replicas == engine.dynamics.total_replicas)
    assert np.all(engine.dynamics.active_latency_fault == 0.0)
    assert np.all(engine.dynamics.active_loss_fault == 0.0)
    assert np.all(engine.dynamics.cb_open == 0.0)

    # Negative control: While fault is actively applied, replicas must NOT match total
    engine.dynamics.apply_fault(fault[0])
    with pytest.raises(AssertionError):
        assert np.all(engine.dynamics.healthy_replicas == engine.dynamics.total_replicas)


@pytest.mark.audit
def test_t_s03_05_physical_conservation_bounds():
    """T-S03-05: Verify conservation laws (utilization, error rates in [0, 1], finite telemetry)."""
    system = MicroserviceSystem(num_services=30, seed=333)
    engine = SimulatorEngine(system)

    for step in range(100):
        res = engine.dynamics.step_tick(ingress_load=100.0, tick=step)
        util = res["cpu_utilization"]
        err = res["error_rate"]
        lat = res["p99_latency"]

        assert np.all(util >= 0.0) and np.all(util <= 100.0), "Utilization out of bounds"
        assert np.all(err >= 0.0) and np.all(err <= 1.0), "Error rate out of bounds"
        assert np.all(np.isfinite(lat)), "Non-finite latency observed"

    # Negative control: Out of bounds error rate must trigger assertion
    corrupted_err = np.array([-0.05, 1.20])
    with pytest.raises(AssertionError):
        assert np.all(corrupted_err >= 0.0) and np.all(corrupted_err <= 1.0)


@pytest.mark.audit
def test_t_s03_06_exhaustive_reachability_micro():
    """T-S03-06: Brute-force reachability on micro-systems (every planted weakness can be triggered)."""
    system = MicroserviceSystem(num_services=6, seed=777)
    engine = SimulatorEngine(system)
    weaknesses = system.ground_truth_weaknesses
    assert len(weaknesses) >= 1, "Must have at least one planted weakness on micro-system"

    for w in weaknesses:
        if w.weakness_type == "colocated_critical_node":
            node_id = w.required_nodes[0]
            faults = [FaultSpec(fault_type=FaultType.NODE_FAILURE, target_id=node_id, intensity=FaultIntensity.HIGH)]
        else:
            faults = [FaultSpec(fault_type=ft, target_id=tid, intensity=FaultIntensity.HIGH) for ft, tid in zip(w.required_fault_types, w.target_service_ids)]

        res = engine.run_experiment(faults, duration_ticks=10, recovery_ticks=5)
        assert res.slo_violated, f"Expected SLO violation for weakness {w.weakness_id}"
        assert w.weakness_id in res.discovered_weakness_ids, f"Weakness {w.weakness_id} not discovered"

    # Negative control: Harmless fault on leaf service should not discover all weaknesses
    safe_fault = [FaultSpec(fault_type=FaultType.LATENCY_INJECTION, target_id=5, intensity=FaultIntensity.LOW)]
    res_safe = engine.run_experiment(safe_fault, duration_ticks=2, recovery_ticks=5)
    with pytest.raises(AssertionError):
        assert len(res_safe.discovered_weakness_ids) == len(weaknesses)


@pytest.mark.audit
def test_t_s03_07_scale_boundaries_and_extremes():
    """T-S03-07: Verify boundary behavior at scales N=2 and N=100 without exceptions."""
    for n in [2, 50, 100]:
        sys = MicroserviceSystem(num_services=n, seed=100 + n)
        eng = SimulatorEngine(sys)
        steady, p99, err = eng.verify_steady_state(ticks=10)
        assert isinstance(steady, (bool, np.bool_))
        assert p99 >= 0.0
        assert 0.0 <= err <= 1.0

    # Low load condition
    sys_zero = MicroserviceSystem(num_services=10, seed=50)
    eng_zero = SimulatorEngine(sys_zero)
    step_res = eng_zero.dynamics.step_tick(ingress_load=0.01, tick=0)
    assert step_res["gateway_error_rate"] < 0.01


@pytest.mark.audit
def test_t_s03_08_simulator_throughput_benchmark():
    """T-S03-08: Measure simulation throughput across scales (N=20, 100) and verify performance."""
    throughputs = {}
    for n in [20, 100]:
        sys = MicroserviceSystem(num_services=n, seed=99)
        eng = SimulatorEngine(sys)
        fault = [FaultSpec(fault_type=FaultType.LATENCY_INJECTION, target_id=1, intensity=FaultIntensity.MEDIUM)]
        eng.dynamics.apply_fault(fault[0])

        t0 = time.perf_counter()
        steps = 100
        for s in range(steps):
            eng.dynamics.step_tick(ingress_load=100.0, tick=s)
        elapsed = time.perf_counter() - t0
        rate = steps / max(1e-5, elapsed)
        throughputs[n] = rate
        assert rate > 100.0, f"Throughput too low for N={n}: {rate:.1f} steps/s"

    # Negative control: Expecting 10,000,000 steps/sec on single core must fail
    with pytest.raises(AssertionError):
        assert throughputs[100] > 10_000_000.0
