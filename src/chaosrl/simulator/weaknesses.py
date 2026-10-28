"""Weakness matching, trigger evaluation, and emergent violation tracking."""

from __future__ import annotations

from typing import List, Tuple
from chaosrl.simulator.models import FaultSpec, FaultType, PlantedWeakness


class WeaknessMatcher:
    """Evaluates whether an experiment's fault injections reveal planted weaknesses."""

    def __init__(self, weaknesses: List[PlantedWeakness]) -> None:
        self.weaknesses = weaknesses
        self.discovered_ids: set[str] = set()

    def evaluate_experiment(
        self,
        faults: List[FaultSpec],
        slo_violated: bool,
    ) -> Tuple[List[str], bool]:
        """Match injected faults against planted weakness trigger conditions.

        Returns:
            Tuple of (list_of_newly_discovered_weakness_ids, is_emergent_violation)
        """
        if not slo_violated or not faults:
            return [], False

        newly_found = []
        matched_any_planted = False

        # Extract fault signatures: set of (target_id, fault_type)
        injected_services = [(f.target_id, f.fault_type) for f in faults]
        injected_types = [f.fault_type for f in faults]
        injected_targets = [f.target_id for f in faults]

        for w in self.weaknesses:
            # Check trigger condition
            matches_trigger = False

            if not w.is_compound:
                # Simple weakness requires single corresponding fault
                req_type = w.required_fault_types[0]
                if w.weakness_type == "colocated_critical_node":
                    # Matches if injected fault is NODE_FAILURE targeting the required node
                    if FaultType.NODE_FAILURE in injected_types:
                        for f in faults:
                            if f.fault_type == FaultType.NODE_FAILURE and f.target_id in w.required_nodes:
                                matches_trigger = True
                                break
                else:
                    target_svc = w.target_service_ids[0]
                    for f in faults:
                        if f.target_id == target_svc and f.fault_type == req_type:
                            matches_trigger = True
                            break

            else:
                # Compound weakness: requires combination of faults
                if w.weakness_type == "compound_retry_storm":
                    # Requires latency or packet loss on callee, or targeting both
                    has_lat = any(f.fault_type in [FaultType.LATENCY_INJECTION, FaultType.PACKET_LOSS] and f.target_id in w.target_service_ids for f in faults)
                    if has_lat and len(faults) >= 2:
                        matches_trigger = True

                elif w.weakness_type == "compound_kill_and_stress":
                    target_svc = w.target_service_ids[0]
                    has_kill = any(f.target_id == target_svc and f.fault_type == FaultType.CONTAINER_KILL for f in faults)
                    has_stress = any(f.target_id == target_svc and f.fault_type == FaultType.CPU_STRESS for f in faults)
                    if has_kill and has_stress:
                        matches_trigger = True

            if matches_trigger:
                matched_any_planted = True
                if w.weakness_id not in self.discovered_ids:
                    w.discovered = True
                    self.discovered_ids.add(w.weakness_id)
                    newly_found.append(w.weakness_id)

        is_emergent = slo_violated and not matched_any_planted
        return newly_found, is_emergent

    @property
    def total_discovered(self) -> int:
        return len(self.discovered_ids)

    @property
    def total_planted(self) -> int:
        return len(self.weaknesses)

    @property
    def discovery_rate(self) -> float:
        return float(len(self.discovered_ids) / len(self.weaknesses)) if self.weaknesses else 0.0
