"""Algorithms library for the Qom transit optimization system."""

from from_qom_to_new_york.algorithms.advanced import (
    ALTAlgorithm,
    AStarResult,
    CongestionRoutingResult,
    SearchComparisonResult,
    astar_search,
    bidirectional_dijkstra,
    compare_dijkstra_vs_astar,
    dynamic_congestion_aware_dijkstra,
)
from from_qom_to_new_york.algorithms.analytics import (
    AnalyticsSummary,
    compute_operational_analytics,
    quickselect,
)
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
from from_qom_to_new_york.algorithms.matching import (
    HopcroftKarp,
    MatchingResult,
    ShiftSlot,
    StaffMember,
    match_staff_to_shifts,
)
from from_qom_to_new_york.algorithms.mst import (
    MSTComparison,
    MSTResult,
    compare_mst_algorithms,
    kruskal_mst,
    prim_mst,
)
from from_qom_to_new_york.algorithms.priority import Train, TrainPriorityQueue
from from_qom_to_new_york.algorithms.scheduling import (
    SchedulingResult,
    TrainSlot,
    interval_scheduling_greedy,
    weighted_interval_scheduling_dp,
)
from from_qom_to_new_york.algorithms.search import (
    SearchResult,
    bfs_connectivity,
    dfs_connectivity,
    get_connected_components,
    is_connected,
)
from from_qom_to_new_york.algorithms.shortest_path import (
    FloydWarshallResult,
    ShortestPathResult,
    bellman_ford,
    dag_shortest_path,
    dijkstra,
    floyd_warshall,
)
from from_qom_to_new_york.algorithms.simulation import (
    PassengerArrivalSimulator,
    StationSimulationMetrics,
    SystemSimulationReport,
)
from from_qom_to_new_york.algorithms.string import (
    FuzzyMatchResult,
    fuzzy_search_stations,
    levenshtein_distance,
)

__all__ = [
    # Search
    "SearchResult",
    "bfs_connectivity",
    "dfs_connectivity",
    "is_connected",
    "get_connected_components",
    # Shortest Path
    "ShortestPathResult",
    "FloydWarshallResult",
    "dijkstra",
    "bellman_ford",
    "dag_shortest_path",
    "floyd_warshall",
    # MST
    "MSTResult",
    "MSTComparison",
    "kruskal_mst",
    "prim_mst",
    "compare_mst_algorithms",
    # Flow
    "FlowResult",
    "edmonds_karp_max_flow",
    # Connectivity
    "TarjanConnectivityResult",
    "find_articulation_points_and_bridges",
    # Scheduling
    "TrainSlot",
    "SchedulingResult",
    "interval_scheduling_greedy",
    "weighted_interval_scheduling_dp",
    # Priority Queue
    "Train",
    "TrainPriorityQueue",
    # Matching (Hopcroft-Karp / T3.5)
    "StaffMember",
    "ShiftSlot",
    "MatchingResult",
    "HopcroftKarp",
    "match_staff_to_shifts",
    # String
    "FuzzyMatchResult",
    "levenshtein_distance",
    "fuzzy_search_stations",
    # Approximation
    "DominatingSetResult",
    "greedy_dominating_set",
    "exact_minimum_dominating_set",
    # Analytics
    "quickselect",
    "AnalyticsSummary",
    "compute_operational_analytics",
    # Simulation
    "PassengerArrivalSimulator",
    "StationSimulationMetrics",
    "SystemSimulationReport",
    # Advanced
    "AStarResult",
    "SearchComparisonResult",
    "CongestionRoutingResult",
    "ALTAlgorithm",
    "astar_search",
    "compare_dijkstra_vs_astar",
    "bidirectional_dijkstra",
    "dynamic_congestion_aware_dijkstra",
]
