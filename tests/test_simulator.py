"""Unit tests for the ChaosRL discrete-time microservice simulator."""

import os
import pytest
import numpy as np

from chaosrl.simulator.engine import SimulatorEngine
from chaosrl.simulator.generator import MicroserviceSystem
from chaosrl.simulator.models import (
    FaultIntensity,
    FaultSpec,
    FaultType,
    TopologyFamily,
)


def test_steady_state_fault_free():
    """Verify that a fault-free system operates stably within SLO thresholds."""
    system = MicroserviceSystem(num_services=50, seed=1234)
    engine = SimulatorEngine(system)
    steady, p99, err = engine.verify_steady_state(ticks=30)
    assert steady, f"System should be steady, got p99={p99}, err={err}"
    assert p99 < 500.0, f"Gateway p99 must be < 500 ms, got {p99}"
    assert err < 0.02, f"Gateway error rate must be < 0.02, got {err}"


def test_seed_determinism():
    """Verify that two simulators initialized with identical seeds produce identical logs."""
    sys1 = MicroserviceSystem(num_services=30, seed=999)
    sys2 = MicroserviceSystem(num_services=30, seed=999)

    eng1 = SimulatorEngine(sys1, noise_std=0.0)
    eng2 = SimulatorEngine(sys2, noise_std=0.0)

    fault = [FaultSpec(fault_type=FaultType.LATENCY_INJECTION, target_id=1, intensity=FaultIntensity.HIGH)]
    res1 = eng1.run_experiment(fault, duration_ticks=10, recovery_ticks=5)
    res2 = eng2.run_experiment(fault, duration_ticks=10, recovery_ticks=5)

    assert abs(res1.gateway_p99_latency_ms - res2.gateway_p99_latency_ms) < 1e-6
    assert abs(res1.cumulative_damage - res2.cumulative_damage) < 1e-6
    assert res1.slo_violated == res2.slo_violated
    assert res1.discovered_weakness_ids == res2.discovered_weakness_ids


def test_node_failure_colocation():
    """Verify that a node failure terminates all replicas assigned to that physical node."""
    system = MicroserviceSystem(num_services=20, seed=42)
    engine = SimulatorEngine(system)

    # Pick node 0
    node_id = 0
    expected_affected = [svc_id for svc_id, svc in system.services.items() if node_id in svc.assigned_nodes]
    assert len(expected_affected) > 0, "Node 0 should host at least one replica"

    engine.dynamics.apply_fault(FaultSpec(fault_type=FaultType.NODE_FAILURE, target_id=node_id))
    for svc_id in expected_affected:
        initial_reps = system.services[svc_id].num_replicas
        remaining_reps = engine.dynamics.healthy_replicas[svc_id]
        killed_count = sum(1 for nd in system.services[svc_id].assigned_nodes if nd == node_id)
        assert remaining_reps == max(0, initial_reps - killed_count)


def test_fault_rollback_restores_steady_state():
    """Verify that clearing faults restores the system to healthy baseline."""
    system = MicroserviceSystem(num_services=25, seed=555)
    engine = SimulatorEngine(system)

    # Inject severe fault
    fault = [FaultSpec(fault_type=FaultType.CONTAINER_KILL, target_id=1, intensity=FaultIntensity.HIGH)]
    res = engine.run_experiment(fault, duration_ticks=10, recovery_ticks=10)

    # After recovery, healthy replicas should match total replicas
    assert np.all(engine.dynamics.healthy_replicas == engine.dynamics.total_replicas)
    assert np.all(engine.dynamics.active_latency_fault == 0.0)
    assert np.all(engine.dynamics.cb_open == 0.0)


def test_weakness_matching_and_near_miss():
    """Verify that weakness matcher triggers only on matching conditions and rejects near-misses."""
    system = MicroserviceSystem(num_services=40, seed=777)
    engine = SimulatorEngine(system)
    weaknesses = system.ground_truth_weaknesses
    assert len(weaknesses) >= 3

    # Test exact match on first simple weakness
    simple_w = next(w for w in weaknesses if not w.is_compound and w.weakness_type != "colocated_critical_node")
    matching_fault = [FaultSpec(fault_type=simple_w.required_fault_types[0], target_id=simple_w.target_service_ids[0], intensity=FaultIntensity.HIGH)]

    found, emergent = engine.matcher.evaluate_experiment(matching_fault, slo_violated=True)
    assert simple_w.weakness_id in found
    assert not emergent

    # Test Near-Miss: Wrong fault type on target service
    wrong_type = FaultType.CPU_STRESS if simple_w.required_fault_types[0] != FaultType.CPU_STRESS else FaultType.PACKET_LOSS
    near_miss_fault = [FaultSpec(fault_type=wrong_type, target_id=simple_w.target_service_ids[0], intensity=FaultIntensity.LOW)]
    found_miss, emergent_miss = engine.matcher.evaluate_experiment(near_miss_fault, slo_violated=True)
    assert simple_w.weakness_id not in found_miss


def test_test_set_lock():
    """Assert that requesting a seed in test range (200,000..200,199) raises an error without env var."""
    test_seed = 200050
    # Ensure env var is not set
    old_env = os.environ.get("CHAOSRL_FINAL_TEST")
    if "CHAOSRL_FINAL_TEST" in os.environ:
        del os.environ["CHAOSRL_FINAL_TEST"]

    try:
        with pytest.raises(PermissionError) as exc_info:
            MicroserviceSystem(num_services=20, seed=test_seed)
        assert "Test set is locked" in str(exc_info.value)
    finally:
        if old_env is not None:
            os.environ["CHAOSRL_FINAL_TEST"] = old_env

