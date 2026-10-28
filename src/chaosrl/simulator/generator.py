"""System topology and weakness generator for ChaosRL simulator."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from chaosrl.simulator.models import (
    FaultType,
    PlantedWeakness,
    ServiceConfig,
    TopologyFamily,
)

TEST_ACCESS_LOG = Path("results/test_access_log.csv")


def check_test_set_lock(seed: int) -> None:
    """Enforce Section 5.6 test-set lock."""
    # Test range: 200,000 to 200,199
    if 200000 <= seed <= 200199:
        if os.environ.get("CHAOSRL_FINAL_TEST") != "1":
            raise PermissionError(
                f"Test set is locked! Attempted access with seed {seed}. "
                "Only final-eval with CHAOSRL_FINAL_TEST=1 may access test systems."
            )
        # Log access
        TEST_ACCESS_LOG.parent.mkdir(parents=True, exist_ok=True)
        file_exists = TEST_ACCESS_LOG.exists()
        with open(TEST_ACCESS_LOG, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "seed", "command", "pid"])
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                seed,
                os.environ.get("CHAOSRL_CMD", "final-eval"),
                os.getpid(),
            ])


class MicroserviceSystem:
    """Represents a generated microservice system with call graph, nodes, and hidden weaknesses."""

    def __init__(
        self,
        num_services: int,
        family: TopologyFamily = TopologyFamily.LAYERED,
        seed: int = 42,
    ) -> None:
        check_test_set_lock(seed)
        self.num_services = num_services
        self.family = family
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        self.num_nodes = max(3, int(np.round(num_services * 0.20)))
        self.services: Dict[int, ServiceConfig] = {}
        self.adjacency: np.ndarray = np.zeros((num_services, num_services), dtype=np.float32)
        self.node_allocations: Dict[int, List[int]] = {n: [] for n in range(self.num_nodes)}
        self._ground_truth_weaknesses: List[PlantedWeakness] = []

        self._build_topology()
        self._plant_weaknesses()

    def _build_topology(self) -> None:
        """Construct call graph and per-service configurations."""
        n = self.num_services

        if self.family == TopologyFamily.LAYERED:
            # Layered DAG: Gateway (idx 0), Business tier (1 to ~60% of N), Backend/Data tier
            layers = [0]
            num_layer1 = max(1, int(n * 0.55))
            for i in range(1, n):
                if i <= num_layer1:
                    layers.append(1)
                else:
                    layers.append(2)

            for i in range(1, n):
                if layers[i] == 1:
                    # Gateway calls layer 1 services
                    if self.rng.random() < 0.65 or i == 1:
                        self.adjacency[0, i] = 1.0
                elif layers[i] == 2:
                    # Layer 1 calls layer 2 services (preferential attachment)
                    callers = [u for u in range(1, num_layer1 + 1)]
                    k = max(1, int(self.rng.geometric(p=0.4)))
                    chosen_callers = self.rng.choice(callers, size=min(k, len(callers)), replace=False)
                    for c in chosen_callers:
                        self.adjacency[c, i] = 1.0

        else:
            # Family M (Mesh / Hub-and-Spoke): Star clusters with lateral calls
            layers = [0] + [1] * (n - 1)
            num_clusters = max(2, n // 8)
            cluster_hubs = [0] + list(self.rng.choice(range(1, n), size=num_clusters - 1, replace=False))

            for i in range(1, n):
                # Connect to nearest cluster hub
                hub = self.rng.choice(cluster_hubs)
                if hub != i:
                    self.adjacency[hub, i] = 1.0
                # Lateral call with probability 0.25
                if self.rng.random() < 0.25:
                    target = self.rng.integers(0, n)
                    if target != i:
                        self.adjacency[i, target] = 1.0

        # Gateway (service 0) must call at least one service
        if np.sum(self.adjacency[0, :]) == 0 and n > 1:
            self.adjacency[0, 1] = 1.0

        # Build ServiceConfigs
        for i in range(n):
            layer = layers[i]
            base_lat = float(self.rng.uniform(8.0, 25.0)) if i > 0 else 5.0
            base_cap = float(self.rng.uniform(120.0, 250.0))

            # Replicas: 1 to 4
            num_replicas = int(self.rng.integers(1, 4))
            if i == 0:
                num_replicas = 3  # Gateway is well replicated

            # Assign replicas to physical nodes
            assigned_nodes = list(self.rng.choice(range(self.num_nodes), size=num_replicas, replace=True))
            for nd in assigned_nodes:
                self.node_allocations[nd].append(i)

            has_to = (self.rng.random() < 0.80) or (i == 0)
            timeout = float(self.rng.uniform(350.0, 600.0)) if has_to else 9999.0

            has_cb = (self.rng.random() < 0.70) or (i == 0)
            max_retries = int(self.rng.integers(1, 4)) if self.rng.random() < 0.65 else 0

            # Decoy: Highly connected hub fortified with protection
            in_deg = int(np.sum(self.adjacency[:, i]))
            is_decoy = False
            if in_deg >= 3 and i > 0:
                is_decoy = True
                num_replicas = 4
                has_to = True
                has_cb = True
                timeout = 300.0

            self.services[i] = ServiceConfig(
                service_id=i,
                name=f"svc_{i:03d}" if i > 0 else "gateway",
                layer=layer,
                base_latency_ms=base_lat,
                base_capacity_rps=base_cap,
                num_replicas=num_replicas,
                assigned_nodes=assigned_nodes,
                timeout_ms=timeout,
                has_timeout=has_to,
                max_retries=max_retries,
                retry_backoff_ms=50.0,
                has_circuit_breaker=has_cb,
                is_decoy=is_decoy,
            )

    def _plant_weaknesses(self) -> None:
        """Plant simple and compound ground-truth weaknesses."""
        n = self.num_services
        simple_target = max(3, int(np.round(0.06 * n)))
        compound_target = max(1, int(np.round(0.02 * n)))

        planted: List[PlantedWeakness] = []
        wid = 1

        # 1. Simple: Single-replica critical service
        candidates_single = [
            i for i in range(1, n)
            if self.services[i].num_replicas == 1 and np.sum(self.adjacency[0, i]) > 0
        ]
        if candidates_single:
            t = self.rng.choice(candidates_single)
            planted.append(PlantedWeakness(
                weakness_id=f"W{wid:03d}",
                weakness_type="single_replica_critical",
                is_compound=False,
                target_service_ids=[int(t)],
                required_fault_types=[FaultType.CONTAINER_KILL],
                description=f"Single replica on critical service {t}",
            ))
            wid += 1

        # 2. Simple: Missing timeout on hot path
        candidates_to = [
            i for i in range(1, n)
            if not self.services[i].has_timeout and not self.services[i].is_decoy
        ]
        if candidates_to:
            t = self.rng.choice(candidates_to)
            planted.append(PlantedWeakness(
                weakness_id=f"W{wid:03d}",
                weakness_type="missing_timeout_hotpath",
                is_compound=False,
                target_service_ids=[int(t)],
                required_fault_types=[FaultType.LATENCY_INJECTION],
                description=f"Missing timeout on service {t} causes caller stall",
            ))
            wid += 1

        # 3. Simple: Co-located critical services on one node
        # Find a node hosting replicas of >= 2 critical services
        node_coloc = []
        for nd, svcs in self.node_allocations.items():
            unique_svcs = set(svcs) - {0}
            if len(unique_svcs) >= 2:
                node_coloc.append((nd, list(unique_svcs)[:2]))
        if node_coloc:
            nd, target_svcs = node_coloc[0]
            planted.append(PlantedWeakness(
                weakness_id=f"W{wid:03d}",
                weakness_type="colocated_critical_node",
                is_compound=False,
                target_service_ids=target_svcs,
                required_fault_types=[FaultType.NODE_FAILURE],
                required_nodes=[nd],
                description=f"Critical services {target_svcs} co-located on physical node {nd}",
            ))
            wid += 1

        # 4. Simple: Unshielded flaky dependency (no circuit breaker)
        candidates_cb = [
            i for i in range(1, n)
            if not self.services[i].has_circuit_breaker and not self.services[i].is_decoy
        ]
        while len(planted) < simple_target and candidates_cb:
            t = int(self.rng.choice(candidates_cb))
            candidates_cb.remove(t)
            planted.append(PlantedWeakness(
                weakness_id=f"W{wid:03d}",
                weakness_type="no_circuit_breaker",
                is_compound=False,
                target_service_ids=[t],
                required_fault_types=[FaultType.DEPENDENCY_ERROR],
                description=f"Missing circuit breaker on flaky dependency {t}",
            ))
            wid += 1

        # Fallback simple weaknesses if target count not reached
        while len(planted) < simple_target:
            t = int(self.rng.integers(1, n))
            planted.append(PlantedWeakness(
                weakness_id=f"W{wid:03d}",
                weakness_type="capacity_margin_low",
                is_compound=False,
                target_service_ids=[t],
                required_fault_types=[FaultType.CPU_STRESS],
                description=f"Low CPU margin on service {t}",
            ))
            wid += 1

        # 5. Compound Weakness: Latency on B + retries on A -> retry storm
        # Find edge A -> B where A has retries
        edges_with_retries = []
        for u in range(n):
            if self.services[u].max_retries >= 2:
                for v in range(n):
                    if self.adjacency[u, v] > 0 and not self.services[v].is_decoy:
                        edges_with_retries.append((u, v))

        if edges_with_retries:
            u, v = edges_with_retries[0]
            planted.append(PlantedWeakness(
                weakness_id=f"W{wid:03d}",
                weakness_type="compound_retry_storm",
                is_compound=True,
                target_service_ids=[u, v],
                required_fault_types=[FaultType.LATENCY_INJECTION, FaultType.PACKET_LOSS],
                description=f"Retry storm: Latency/Loss on {v} amplified by retries at {u}",
            ))
            wid += 1

        # 6. Compound Weakness: Pod kill + CPU stress on multi-replica service
        multi_rep = [i for i in range(1, n) if self.services[i].num_replicas >= 2 and not self.services[i].is_decoy]
        while len([p for p in planted if p.is_compound]) < compound_target:
            target_svc = int(self.rng.choice(multi_rep)) if multi_rep else 1
            planted.append(PlantedWeakness(
                weakness_id=f"W{wid:03d}",
                weakness_type="compound_kill_and_stress",
                is_compound=True,
                target_service_ids=[target_svc, target_svc],
                required_fault_types=[FaultType.CONTAINER_KILL, FaultType.CPU_STRESS],
                description=f"Container kill combined with CPU exhaustion on remaining replica of {target_svc}",
            ))
            wid += 1

        self._ground_truth_weaknesses = planted

    @property
    def ground_truth_weaknesses(self) -> List[PlantedWeakness]:
        """Internal simulator accessor for evaluation; NEVER exposed to agents."""
        return self._ground_truth_weaknesses
