"""Edge data model representing transit connections between stations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MetricType = Literal["distance", "time", "cost", "congestion"]


@dataclass
class Edge:
    """Represents a rail connection between two stations.

    Attributes:
        source: Name of the departure station.
        target: Name of the arrival station.
        distance_km: Track length in kilometers.
        time_minutes: Average travel time in minutes.
        capacity: Maximum passenger throughput (passengers/hour).
        weight: Generic weight override (used for custom heuristics, negative weights, etc.).
        is_directed: True if track is one-way, False if bidirectional.
    """

    source: str
    target: str
    distance_km: float
    time_minutes: float
    capacity: int = 5000
    weight: float = 0.0
    is_directed: bool = False

    def __post_init__(self) -> None:
        """Default generic weight to distance_km if not explicitly supplied."""
        if self.weight == 0.0:
            self.weight = self.distance_km

    def get_weight(self, metric: MetricType = "distance") -> float:
        """Retrieve edge cost based on the requested evaluation metric.

        Args:
            metric: Optimization criterion ('distance', 'time', 'cost', or 'congestion').

        Returns:
            The numerical weight for pathfinding / spanning tree algorithms.
        """
        if metric == "distance":
            return self.distance_km
        elif metric == "time":
            return self.time_minutes
        elif metric == "cost":
            return self.weight
        elif metric == "congestion":
            return self.weight
        raise ValueError(f"Unsupported metric: '{metric}'. Choose from: distance, time, cost, congestion.")

    def reverse(self) -> Edge:
        """Create a reversed directed edge (target -> source) with identical properties."""
        return Edge(
            source=self.target,
            target=self.source,
            distance_km=self.distance_km,
            time_minutes=self.time_minutes,
            capacity=self.capacity,
            weight=self.weight,
            is_directed=self.is_directed,
        )

    def __repr__(self) -> str:
        arrow = "->" if self.is_directed else "<->"
        return (
            f"Edge({self.source} {arrow} {self.target}, "
            f"dist={self.distance_km}km, time={self.time_minutes}min, cap={self.capacity})"
        )
