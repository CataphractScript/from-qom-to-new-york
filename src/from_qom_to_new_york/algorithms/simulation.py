"""Stochastic passenger arrival and gate queueing simulation.

Simulates passenger entry processes, queueing at fare turnstiles/ticket gates,
and boarding dynamics under variable rush-hour and off-peak conditions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Passenger:
    """Individual simulated passenger."""

    id: int
    station_name: str
    arrival_time_min: float
    gate_entry_time: float = 0.0
    service_completion_time: float = 0.0

    @property
    def wait_time_min(self) -> float:
        """Time spent waiting in gate queue before reaching turnstile."""
        return max(0.0, self.gate_entry_time - self.arrival_time_min)

    @property
    def total_system_time_min(self) -> float:
        """Total time from station arrival to passing turnstiles."""
        return max(0.0, self.service_completion_time - self.arrival_time_min)


@dataclass
class StationSimulationMetrics:
    """Performance metrics for an individual station's entrance gates."""

    station_name: str
    total_passengers_arrived: int
    total_passengers_served: int
    avg_wait_time_minutes: float
    max_wait_time_minutes: float
    avg_queue_length: float
    max_queue_length: int
    gate_utilization_ratio: float
    is_bottleneck: bool


@dataclass
class SystemSimulationReport:
    """Consolidated report across all simulated stations."""

    simulation_duration_minutes: float
    total_system_passengers: int
    average_system_wait_time_minutes: float
    max_system_wait_time_minutes: float
    busiest_station: str
    station_metrics: Dict[str, StationSimulationMetrics]
    recommendations: List[str]


class PassengerArrivalSimulator:
    """Simulates passenger arrivals and turnstile queues at metro stations."""

    def __init__(
        self,
        random_seed: Optional[int] = 42,
    ) -> None:
        if random_seed is not None:
            random.seed(random_seed)

    def simulate_station_gates(
        self,
        station_name: str,
        duration_minutes: float = 60.0,
        arrival_rate_per_min: float = 15.0,
        num_turnstiles: int = 4,
        avg_service_time_sec: float = 4.0,
    ) -> StationSimulationMetrics:
        """Simulate entrance turnstiles at a specific station over a time horizon.

        Models arrivals as a Poisson process (exponential inter-arrival times) and
        service times as exponentially distributed (M/M/c queueing model).

        Args:
            station_name: Station being evaluated.
            duration_minutes: Total simulation duration in minutes.
            arrival_rate_per_min: Average passenger arrival rate lambda.
            num_turnstiles: Number of parallel automated fare gates c.
            avg_service_time_sec: Average time in seconds to tap card and pass gate.

        Returns:
            StationSimulationMetrics.
        """
        avg_service_time_min = avg_service_time_sec / 60.0

        # Generate passenger arrivals via Poisson process
        passengers: List[Passenger] = []
        current_time = 0.0
        pid = 1

        while current_time < duration_minutes:
            inter_arrival = random.expovariate(arrival_rate_per_min)
            current_time += inter_arrival
            if current_time < duration_minutes:
                passengers.append(
                    Passenger(
                        id=pid,
                        station_name=station_name,
                        arrival_time_min=current_time,
                    )
                )
                pid += 1

        # Multi-server queue simulation
        turnstile_available_time = [0.0] * num_turnstiles
        total_service_busy_time = 0.0
        queue_lengths: List[int] = []

        for p in passengers:
            # Find earliest available turnstile
            earliest_gate_idx = min(range(num_turnstiles), key=lambda i: turnstile_available_time[i])
            gate_ready_time = turnstile_available_time[earliest_gate_idx]

            # Passenger starts service at max(arrival_time, gate_ready_time)
            p.gate_entry_time = max(p.arrival_time_min, gate_ready_time)

            # Sample service time
            service_duration = random.expovariate(1.0 / avg_service_time_min)
            p.service_completion_time = p.gate_entry_time + service_duration

            turnstile_available_time[earliest_gate_idx] = p.service_completion_time
            total_service_busy_time += service_duration

            # Approximate queue length at arrival
            current_in_queue = sum(1 for prev_p in passengers if prev_p.arrival_time_min < p.arrival_time_min and prev_p.gate_entry_time > p.arrival_time_min)
            queue_lengths.append(current_in_queue)

        served = [p for p in passengers if p.service_completion_time <= duration_minutes + 10.0]
        wait_times = [p.wait_time_min for p in served]

        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0
        max_wait = max(wait_times) if wait_times else 0.0
        max_q = max(queue_lengths) if queue_lengths else 0
        avg_q = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0.0

        total_capacity_time = duration_minutes * num_turnstiles
        utilization = min(1.0, total_service_busy_time / total_capacity_time) if total_capacity_time > 0 else 0.0

        is_bottleneck = avg_wait > 2.0 or utilization > 0.85 or max_q > 25

        return StationSimulationMetrics(
            station_name=station_name,
            total_passengers_arrived=len(passengers),
            total_passengers_served=len(served),
            avg_wait_time_minutes=round(avg_wait, 3),
            max_wait_time_minutes=round(max_wait, 3),
            avg_queue_length=round(avg_q, 2),
            max_queue_length=max_q,
            gate_utilization_ratio=round(utilization, 4),
            is_bottleneck=is_bottleneck,
        )

    def simulate_network(
        self,
        station_rates: Dict[str, float],
        duration_minutes: float = 60.0,
        default_turnstiles: int = 4,
    ) -> SystemSimulationReport:
        """Run full network simulation across multiple stations.

        Args:
            station_rates: Map of station_name -> arrival_rate_per_minute.
            duration_minutes: Duration of simulation in minutes.
            default_turnstiles: Number of turnstiles per station.

        Returns:
            SystemSimulationReport.
        """
        metrics_map: Dict[str, StationSimulationMetrics] = {}
        total_p = 0
        all_waits: List[float] = []

        for station_name, rate in station_rates.items():
            st_metric = self.simulate_station_gates(
                station_name=station_name,
                duration_minutes=duration_minutes,
                arrival_rate_per_min=rate,
                num_turnstiles=default_turnstiles,
            )
            metrics_map[station_name] = st_metric
            total_p += st_metric.total_passengers_arrived
            all_waits.append(st_metric.avg_wait_time_minutes)

        avg_sys_wait = sum(all_waits) / len(all_waits) if all_waits else 0.0
        max_sys_wait = max((m.max_wait_time_minutes for m in metrics_map.values()), default=0.0)
        busiest = max(metrics_map.keys(), key=lambda k: metrics_map[k].total_passengers_arrived)

        recommendations: List[str] = []
        for name, m in metrics_map.items():
            if m.is_bottleneck:
                recommendations.append(
                    f"Deploy +2 automated gates at '{name}' (utilization: {m.gate_utilization_ratio*100:.1f}%, max queue: {m.max_queue_length})."
                )

        if not recommendations:
            recommendations.append("All station gate configurations are operating within optimal QoS thresholds.")

        return SystemSimulationReport(
            simulation_duration_minutes=duration_minutes,
            total_system_passengers=total_p,
            average_system_wait_time_minutes=round(avg_sys_wait, 3),
            max_system_wait_time_minutes=round(max_sys_wait, 3),
            busiest_station=busiest,
            station_metrics=metrics_map,
            recommendations=recommendations,
        )
