"""Routing and Navigation Service."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple

from from_qom_to_new_york.algorithms.advanced import (
    AStarResult,
    CongestionRoutingResult,
    SearchComparisonResult,
    astar_search,
    bidirectional_dijkstra,
    compare_dijkstra_vs_astar,
    dynamic_congestion_aware_dijkstra,
)
from from_qom_to_new_york.algorithms.search import (
    SearchResult,
    bfs_connectivity,
    dfs_connectivity,
)
from from_qom_to_new_york.algorithms.shortest_path import (
    FloydWarshallResult,
    ShortestPathResult,
    dijkstra,
    floyd_warshall,
)
from from_qom_to_new_york.core.edge import MetricType
from from_qom_to_new_york.core.graph import Graph


class RoutingService:
    """Provides high-level routing, shortest path calculation, and navigation queries."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._cached_floyd_dist: Optional[FloydWarshallResult] = None
        self._cached_floyd_time: Optional[FloydWarshallResult] = None

    def check_connectivity(
        self,
        source: str,
        target: str,
        method: Literal["bfs", "dfs"] = "bfs",
    ) -> SearchResult:
        """Check if source station can reach target station and return a valid path."""
        if method == "bfs":
            return bfs_connectivity(self._graph, source, target)
        elif method == "dfs":
            return dfs_connectivity(self._graph, source, target)
        raise ValueError(f"Unknown traversal method: {method}")

    def find_shortest_path(
        self,
        source: str,
        target: str,
        metric: MetricType = "distance",
        algorithm: Literal["dijkstra", "astar", "bidirectional", "floyd"] = "dijkstra",
    ) -> ShortestPathResult:
        """Find the shortest route between two stations using the specified algorithm and metric."""
        if algorithm == "dijkstra":
            return dijkstra(self._graph, source, target, metric=metric)
        elif algorithm == "astar":
            return astar_search(self._graph, source, target, metric=metric)
        elif algorithm == "bidirectional":
            return bidirectional_dijkstra(self._graph, source, target, metric=metric)
        elif algorithm == "floyd":
            cached = self._get_or_build_floyd(metric)
            cost = cached.get_distance(source, target)
            path = cached.get_path(source, target)
            return ShortestPathResult(
                source=source,
                target=target,
                path=path,
                total_cost=cost,
                distances=cached.dist_matrix[source],
                predecessors={},
                nodes_visited=len(cached.stations),
                metric=metric,
            )
        raise ValueError(f"Unsupported routing algorithm: '{algorithm}'.")

    def compare_dijkstra_astar(
        self,
        source: str,
        target: str,
        metric: MetricType = "distance",
    ) -> SearchComparisonResult:
        """Benchmark Dijkstra vs A* node expansions and search efficiency."""
        return compare_dijkstra_vs_astar(self._graph, source, target, metric=metric)

    def dynamic_congestion_route(
        self,
        source: str,
        target: str,
        passenger_flows: Dict[Tuple[str, str], float],
    ) -> CongestionRoutingResult:
        """Find dynamic shortest route under real-time passenger congestion loads."""
        return dynamic_congestion_aware_dijkstra(
            graph=self._graph,
            source=source,
            target=target,
            passenger_flows=passenger_flows,
        )

    def _get_or_build_floyd(self, metric: MetricType) -> FloydWarshallResult:
        if metric == "distance":
            if self._cached_floyd_dist is None:
                self._cached_floyd_dist = floyd_warshall(self._graph, metric="distance")
            return self._cached_floyd_dist
        else:
            if self._cached_floyd_time is None:
                self._cached_floyd_time = floyd_warshall(self._graph, metric="time")
            return self._cached_floyd_time
