"""Network Analysis, Capacity Evaluation, Resilience, and Optimization Service."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from from_qom_to_new_york.algorithms.approximation import (
    DominatingSetResult,
    exact_minimum_dominating_set,
    greedy_dominating_set,
)
from from_qom_to_new_york.algorithms.connectivity import (
    TarjanConnectivityResult,
    find_articulation_points_and_bridges,
)
from from_qom_to_new_york.algorithms.flow import FlowResult, edmonds_karp_max_flow
from from_qom_to_new_york.algorithms.shortest_path import (
    FloydWarshallResult,
    floyd_warshall,
)
from from_qom_to_new_york.algorithms.string import (
    FuzzyMatchResult,
    fuzzy_search_stations,
)
from from_qom_to_new_york.core.edge import MetricType
from from_qom_to_new_york.core.graph import Graph


class AnalysisService:
    """Provides advanced transit network diagnostics, capacity analysis, resilience, and search."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._floyd_result_dist: Optional[FloydWarshallResult] = None
        self._floyd_result_time: Optional[FloydWarshallResult] = None

    # --- T4.1: Floyd-Warshall Precomputation ---
    def compute_all_pairs_matrix(self, metric: MetricType = "distance") -> FloydWarshallResult:
        """Compute or return cached All-Pairs Shortest Path matrix."""
        if metric == "distance":
            if self._floyd_result_dist is None:
                self._floyd_result_dist = floyd_warshall(self._graph, metric="distance")
            return self._floyd_result_dist
        else:
            if self._floyd_result_time is None:
                self._floyd_result_time = floyd_warshall(self._graph, metric="time")
            return self._floyd_result_time

    # --- T4.2: Maximum Flow & Capacity Bottlenecks ---
    def compute_peak_capacity(
        self,
        source: str,
        sink: str,
    ) -> FlowResult:
        """Compute maximum passenger throughput from source to sink and identify bottleneck tracks."""
        return edmonds_karp_max_flow(self._graph, source=source, sink=sink)

    # --- T4.3: Resilience, Articulation Points, and Bridges ---
    def identify_critical_infrastructure(self) -> TarjanConnectivityResult:
        """Find cut-vertices (critical stations) and bridges (critical tracks) using Tarjan's DFS."""
        return find_articulation_points_and_bridges(self._graph)

    # --- T4.4: Emergency Team Placement (Dominating Set) ---
    def plan_emergency_response_deployment(
        self,
        exact: bool = False,
    ) -> DominatingSetResult:
        """Deploy emergency response teams such that every station is at distance <= 1 hop."""
        if exact:
            return exact_minimum_dominating_set(self._graph)
        return greedy_dominating_set(self._graph)

    # --- T4.5 / T4.6: Fuzzy Station Search ---
    def search_station_fuzzy(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[FuzzyMatchResult]:
        """Fuzzy match station names tolerant to spelling errors using Levenshtein distance."""
        station_names = self._graph.get_station_names()
        return fuzzy_search_stations(query, station_names, top_k=top_k)
