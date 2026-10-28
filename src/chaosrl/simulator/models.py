"""Data structures and types for the ChaosRL microservice simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


class TopologyFamily(str, Enum):
    LAYERED = "L"
    MESH = "M"


class FaultType(str, Enum):
    CONTAINER_KILL = "container_kill"
    NODE_FAILURE = "node_failure"
    LATENCY_INJECTION = "latency_injection"
    PACKET_LOSS = "packet_loss"
    CPU_STRESS = "cpu_stress"
    DEPENDENCY_ERROR = "dependency_error"


class FaultIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class FaultSpec:
    fault_type: FaultType
    target_id: int  # service_id or node_id
    intensity: FaultIntensity = FaultIntensity.MEDIUM
    duration_ticks: int = 10
    start_tick: int = 0
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceConfig:
    service_id: int
    name: str
    layer: int  # 0: gateway, 1: business, 2: data/backend
    base_latency_ms: float
    base_capacity_rps: float
    num_replicas: int
    assigned_nodes: List[int]
    timeout_ms: float
    has_timeout: bool
    max_retries: int
    retry_backoff_ms: float
    has_circuit_breaker: bool
    circuit_breaker_threshold: float = 0.25
    has_fallback: bool = False
    has_autoscaling: bool = False
    is_decoy: bool = False


@dataclass
class PlantedWeakness:
    weakness_id: str
    weakness_type: str  # e.g., 'single_replica_critical', 'missing_timeout', 'retry_storm'
    is_compound: bool
    target_service_ids: List[int]
    required_fault_types: List[FaultType]
    required_nodes: List[int] = field(default_factory=list)
    description: str = ""
    discovered: bool = False


@dataclass
class ExperimentResult:
    experiment_id: int
    faults: List[FaultSpec]
    slo_violated: bool
    gateway_p99_latency_ms: float
    gateway_error_rate: float
    cumulative_damage: float
    discovered_weakness_ids: List[str]
    emergent_violation: bool
    duration_ticks: int
    metrics_history: Dict[str, np.ndarray] = field(default_factory=dict)
