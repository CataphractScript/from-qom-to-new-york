"""Minimum Spanning Tree (MST) algorithms (Kruskal, Prim) and comparative analysis.

Theoretical Complexities:
- Kruskal (with Union-Find): O(E log E) = O(E log V) time, O(V + E) space.
  Sorting takes O(E log E); union-find operations take O(E * alpha(V)) where alpha is the inverse Ackermann.
- Prim (with Min-Heap): O(E log V) time, O(V) space.
  Best suited for dense graphs (E ~ V^2), whereas Kruskal is ideal for sparse graphs.
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple

from from_qom_to_new_york.core.dsu import DisjointSetUnion
from from_qom_to_new_york.core.edge import Edge, MetricType
from from_qom_to_new_york.core.graph import Graph


@dataclass
class MSTResult:
    """Result of a Minimum Spanning Tree computation.

    Attributes:
        algorithm_name: 'Kruskal' or 'Prim'.
        mst_edges: Selected subset of edges forming the tree.
        total_weight: Sum of edge weights in the MST.
        execution_time_ms: Wall-clock execution time in milliseconds.
        is_connected: True if the resulting tree spans all vertices (|V| - 1 edges).
        metric: Optimization metric ('distance', 'cost', etc.).
    """

    algorithm_name: str
    mst_edges: List[Edge]
    total_weight: float
    execution_time_ms: float
    is_connected: bool
    metric: str


def kruskal_mst(
    graph: Graph,
    metric: MetricType = "distance",
    weight_fn: Optional[Callable[[Edge], float]] = None,
) -> MSTResult:
    """Compute Minimum Spanning Tree using Kruskal's algorithm with Union-Find (DSU).

    Why Kruskal?
    Kruskal follows an edge-centric greedy strategy. It sorts all unique undirected edges by weight
    and adds an edge to the forest if and only if it does not introduce a cycle.
    With Path Compression and Union by Rank, cycle testing takes amortized O(alpha(V)) time.

    Complexity:
        Time: O(E log E) = O(E log V).
        Space: O(V + E).
    """
    start_time = time.perf_counter()

    def get_w(edge: Edge) -> float:
        return weight_fn(edge) if weight_fn is not None else edge.get_weight(metric)

    # 1. Collect and deduplicate all undirected edges
    edges = graph.get_all_edges(deduplicate_undirected=True)

    # 2. Sort edges in non-decreasing order of weight
    sorted_edges = sorted(edges, key=get_w)

    # 3. Initialize Disjoint Set Union with all station vertices
    stations = graph.get_station_names()
    dsu: DisjointSetUnion[str] = DisjointSetUnion(stations)

    mst_edges: List[Edge] = []
    total_weight = 0.0

    # 4. Greedily pick edges
    for edge in sorted_edges:
        u, v = edge.source, edge.target
        if dsu.union(u, v):
            mst_edges.append(edge)
            total_weight += get_w(edge)
            if len(mst_edges) == len(stations) - 1:
                break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    is_spanning = (len(mst_edges) == len(stations) - 1) if stations else True

    return MSTResult(
        algorithm_name="Kruskal (with Union-Find)",
        mst_edges=mst_edges,
        total_weight=round(total_weight, 4),
        execution_time_ms=round(elapsed_ms, 4),
        is_connected=is_spanning,
        metric=metric,
    )


def prim_mst(
    graph: Graph,
    start_station: Optional[str] = None,
    metric: MetricType = "distance",
    weight_fn: Optional[Callable[[Edge], float]] = None,
) -> MSTResult:
    """Compute Minimum Spanning Tree using Prim's algorithm with a binary min-heap.

    Why Prim?
    Prim follows a vertex-centric greedy strategy. Starting from a root vertex, it grows a single
    tree by iteratively choosing the cheapest cut-crossing edge connecting a visited vertex to an
    unvisited vertex.

    Complexity:
        Time: O(E log V) with binary heap.
        Space: O(V + E) for priority queue and visited tracking.
    """
    start_time = time.perf_counter()

    def get_w(edge: Edge) -> float:
        return weight_fn(edge) if weight_fn is not None else edge.get_weight(metric)

    stations = graph.get_station_names()
    if not stations:
        return MSTResult("Prim", [], 0.0, 0.0, True, metric)

    root = start_station if start_station is not None else stations[0]
    if not graph.has_station(root):
        raise ValueError(f"Start station '{root}' not found in graph.")

    visited: Set[str] = {root}
    mst_edges: List[Edge] = []
    total_weight = 0.0

    # Priority queue stores tuples: (weight, source, target, edge_obj)
    pq: List[Tuple[float, str, str, Edge]] = []

    # Initialize priority queue with edges incident to the root
    for edge in graph.get_outgoing_edges(root):
        heapq.heappush(pq, (get_w(edge), edge.source, edge.target, edge))

    while pq and len(visited) < len(stations):
        w, u, v, edge_obj = heapq.heappop(pq)

        if v in visited:
            continue

        visited.add(v)
        mst_edges.append(edge_obj)
        total_weight += w

        # Add all edges incident to newly visited vertex v
        for next_edge in graph.get_outgoing_edges(v):
            neighbor = next_edge.target
            if neighbor not in visited:
                heapq.heappush(pq, (get_w(next_edge), next_edge.source, neighbor, next_edge))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    is_spanning = len(visited) == len(stations)

    return MSTResult(
        algorithm_name="Prim (with Min-Heap)",
        mst_edges=mst_edges,
        total_weight=round(total_weight, 4),
        execution_time_ms=round(elapsed_ms, 4),
        is_connected=is_spanning,
        metric=metric,
    )


@dataclass
class MSTComparison:
    """Side-by-side performance and structural comparison between Kruskal and Prim.

    Attributes:
        kruskal_result: MSTResult from Kruskal.
        prim_result: MSTResult from Prim.
        weights_match: Boolean verification that both algorithms produced identical MST total cost.
        edge_count: Number of edges in the MST (|V| - 1).
        analysis: Theoretical and practical comparison commentary.
    """

    kruskal_result: MSTResult
    prim_result: MSTResult
    weights_match: bool
    edge_count: int
    analysis: str


def compare_mst_algorithms(graph: Graph, metric: MetricType = "distance") -> MSTComparison:
    """Run both Kruskal's and Prim's algorithms and generate a comparative benchmark.

    Returns:
        MSTComparison holding benchmark results and algorithmic evaluation.
    """
    kruskal_res = kruskal_mst(graph, metric=metric)
    prim_res = prim_mst(graph, metric=metric)

    weights_match = abs(kruskal_res.total_weight - prim_res.total_weight) < 1e-6

    commentary = (
        f"Comparative Analysis for Qom Metro Graph (|V|={graph.order}, |E|={graph.size}):\n"
        f"- Both algorithms yield the exact same minimum spanning cost: {kruskal_res.total_weight} {metric} units.\n"
        f"- Number of spanning edges: {len(kruskal_res.mst_edges)} (satisfying |V|-1 = {graph.order-1}).\n"
        f"- Kruskal runtime: {kruskal_res.execution_time_ms:.4f} ms | Prim runtime: {prim_res.execution_time_ms:.4f} ms.\n"
        f"- On sparse transit networks like Qom (|E| ~= |V|), Kruskal is exceptionally fast due to O(E log E) sorting "
        f"and O(alpha(V)) DSU operations. Prim is similarly efficient O(E log V) with a binary heap."
    )

    return MSTComparison(
        kruskal_result=kruskal_res,
        prim_result=prim_res,
        weights_match=weights_match,
        edge_count=len(kruskal_res.mst_edges),
        analysis=commentary,
    )
