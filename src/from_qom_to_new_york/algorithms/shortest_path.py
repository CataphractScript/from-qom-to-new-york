"""Shortest path algorithms (Dijkstra, Bellman-Ford, DAG Shortest Path, Floyd-Warshall).

Theoretical Complexities:
- Dijkstra (with Min-Heap): O((V + E) log V) time, O(V) space.
- Bellman-Ford (with Negative Cycle Detection): O(V * E) time, O(V) space.
- DAG Shortest Path (via Topological Sort): O(V + E) time, O(V) space.
- Floyd-Warshall (All-Pairs): O(V^3) time, O(V^2) space.
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple

from from_qom_to_new_york.core.edge import Edge, MetricType
from from_qom_to_new_york.core.graph import Graph


@dataclass
class ShortestPathResult:
    """Encapsulates the result of a shortest path computation.

    Attributes:
        source: Starting station name.
        target: Optional destination station name.
        path: List of station names from source to target, or empty if unreachable.
        total_cost: Minimal path weight (distance, time, or custom metric).
        distances: Full map of shortest distances from source to all reachable vertices.
        predecessors: Map of vertex to predecessor vertex for path reconstruction.
        nodes_visited: Count of vertices popped/relaxed during execution.
        metric: Optimization criterion ('distance', 'time', etc.).
        has_negative_cycle: True if a negative weight cycle was detected (Bellman-Ford / Floyd-Warshall).
        negative_cycle: List of station names forming the negative cycle, if detected.
    """

    source: str
    target: Optional[str]
    path: List[str]
    total_cost: float
    distances: Dict[str, float]
    predecessors: Dict[str, Optional[str]]
    nodes_visited: int
    metric: str
    has_negative_cycle: bool = False
    negative_cycle: Optional[List[str]] = None


def dijkstra(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
    metric: MetricType = "distance",
    weight_fn: Optional[Callable[[Edge], float]] = None,
) -> ShortestPathResult:
    """Compute single-source shortest paths using Dijkstra's algorithm with a binary min-heap.

    Why Dijkstra?
    When edge weights are non-negative (distances, travel times), Dijkstra provides optimal
    performance O((V + E) log V) by greedily exploring vertices in order of increasing distance.

    Args:
        graph: Transit network graph.
        source: Departure station name.
        target: Optional destination station name. If provided, stops immediately upon reaching target.
        metric: Cost criterion ('distance', 'time', 'cost', 'congestion').
        weight_fn: Optional custom callable to extract cost from an Edge.

    Returns:
        ShortestPathResult with path, cost, and distances.

    Raises:
        ValueError: If source/target are invalid or edge weights are negative.
    """
    if not graph.has_station(source):
        raise ValueError(f"Source station '{source}' not found in graph.")
    if target is not None and not graph.has_station(target):
        raise ValueError(f"Target station '{target}' not found in graph.")

    def get_w(edge: Edge) -> float:
        w = weight_fn(edge) if weight_fn is not None else edge.get_weight(metric)
        if w < 0:
            raise ValueError(
                f"Negative edge weight {w} detected on edge {edge.source}->{edge.target}. "
                f"Dijkstra requires non-negative weights; use Bellman-Ford instead."
            )
        return w

    # Priority queue stores tuples: (distance, vertex_name)
    pq: List[Tuple[float, str]] = [(0.0, source)]
    distances: Dict[str, float] = {st: float("inf") for st in graph.get_station_names()}
    distances[source] = 0.0
    predecessors: Dict[str, Optional[str]] = {st: None for st in graph.get_station_names()}
    visited: Set[str] = set()
    nodes_visited_count = 0

    while pq:
        dist_u, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)
        nodes_visited_count += 1

        if target is not None and u == target:
            break

        for edge in graph.get_outgoing_edges(u):
            v = edge.target
            if v in visited:
                continue

            edge_weight = get_w(edge)
            new_dist = dist_u + edge_weight

            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))

    # Path reconstruction
    path: List[str] = []
    total_cost = float("inf")

    if target is not None:
        if distances[target] < float("inf"):
            curr: Optional[str] = target
            while curr is not None:
                path.append(curr)
                curr = predecessors[curr]
            path.reverse()
            total_cost = distances[target]
    else:
        path = []
        total_cost = 0.0

    return ShortestPathResult(
        source=source,
        target=target,
        path=path,
        total_cost=total_cost,
        distances=distances,
        predecessors=predecessors,
        nodes_visited=nodes_visited_count,
        metric=metric,
    )


def bellman_ford(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
    metric: MetricType = "cost",
    weight_fn: Optional[Callable[[Edge], float]] = None,
) -> ShortestPathResult:
    """Compute shortest paths and detect negative cycles using the Bellman-Ford algorithm.

    Why Bellman-Ford?
    Unlike Dijkstra, Bellman-Ford correctly handles edges with negative weights (such as
    incentive bonuses, fare discounts, or energy regeneration) and detects whether a negative cycle exists.

    Complexity:
        Time: O(V * E) - relaxes all E edges (V - 1) times.
        Space: O(V) for distance and predecessor tables.

    Returns:
        ShortestPathResult. If a negative cycle is reachable from source, has_negative_cycle is True
        and negative_cycle contains the cycle sequence.
    """
    if not graph.has_station(source):
        raise ValueError(f"Source station '{source}' not found in graph.")
    if target is not None and not graph.has_station(target):
        raise ValueError(f"Target station '{target}' not found in graph.")

    def get_w(edge: Edge) -> float:
        return weight_fn(edge) if weight_fn is not None else edge.get_weight(metric)

    all_stations = graph.get_station_names()
    num_v = len(all_stations)
    distances: Dict[str, float] = {st: float("inf") for st in all_stations}
    distances[source] = 0.0
    predecessors: Dict[str, Optional[str]] = {st: None for st in all_stations}

    all_edges: List[Edge] = []
    for st in all_stations:
        all_edges.extend(graph.get_outgoing_edges(st))

    # Relax all edges |V| - 1 times
    last_relaxed_node: Optional[str] = None
    for _ in range(num_v - 1):
        relaxed_any = False
        for edge in all_edges:
            u, v = edge.source, edge.target
            w = get_w(edge)
            if distances[u] != float("inf") and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessors[v] = u
                relaxed_any = True
        if not relaxed_any:
            break

    # |V|-th iteration: Check for negative cycles
    negative_cycle: Optional[List[str]] = None
    has_neg_cycle = False

    for edge in all_edges:
        u, v = edge.source, edge.target
        w = get_w(edge)
        if distances[u] != float("inf") and distances[u] + w < distances[v]:
            has_neg_cycle = True
            last_relaxed_node = v
            break

    if has_neg_cycle and last_relaxed_node is not None:
        # Trace back |V| steps to guarantee entry into the cycle
        curr = last_relaxed_node
        for _ in range(num_v):
            curr = predecessors[curr] or curr

        # Extract cycle
        cycle_nodes: List[str] = [curr]
        p = predecessors[curr]
        while p is not None and p != curr:
            cycle_nodes.append(p)
            p = predecessors[p]
        cycle_nodes.append(curr)
        cycle_nodes.reverse()
        negative_cycle = cycle_nodes

        return ShortestPathResult(
            source=source,
            target=target,
            path=[],
            total_cost=float("-inf"),
            distances=distances,
            predecessors=predecessors,
            nodes_visited=num_v,
            metric=metric,
            has_negative_cycle=True,
            negative_cycle=negative_cycle,
        )

    # Path reconstruction if no negative cycle
    path: List[str] = []
    total_cost = float("inf")
    if target is not None:
        if distances[target] < float("inf"):
            curr_target: Optional[str] = target
            while curr_target is not None:
                path.append(curr_target)
                curr_target = predecessors[curr_target]
            path.reverse()
            total_cost = distances[target]

    return ShortestPathResult(
        source=source,
        target=target,
        path=path,
        total_cost=total_cost,
        distances=distances,
        predecessors=predecessors,
        nodes_visited=num_v,
        metric=metric,
        has_negative_cycle=False,
    )


def dag_shortest_path(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
    metric: MetricType = "distance",
    weight_fn: Optional[Callable[[Edge], float]] = None,
) -> ShortestPathResult:
    """Compute shortest path on a Directed Acyclic Graph (DAG) in linear O(V + E) time.

    Why Topological Sorting for DAGs?
    In a DAG, no negative cycles can exist. Processing vertices in topological order guarantees
    that when vertex u is relaxed, all shortest paths to u have already been finalized.
    This eliminates the need for priority queues, achieving linear time O(V + E).

    Complexity:
        Time: O(V + E) for topological sort + O(V + E) edge relaxations.
        Space: O(V).

    Raises:
        ValueError: If graph contains a cycle (not a DAG).
    """
    if not graph.has_station(source):
        raise ValueError(f"Source station '{source}' not found in graph.")
    if target is not None and not graph.has_station(target):
        raise ValueError(f"Target station '{target}' not found in graph.")

    def get_w(edge: Edge) -> float:
        return weight_fn(edge) if weight_fn is not None else edge.get_weight(metric)

    all_stations = graph.get_station_names()

    # 1. Calculate in-degrees for Kahn's Algorithm
    in_degrees: Dict[str, int] = {st: 0 for st in all_stations}
    for st in all_stations:
        for edge in graph.get_outgoing_edges(st):
            in_degrees[edge.target] += 1

    # 2. Queue all vertices with in-degree 0
    zero_in_queue: deque[str] = deque([st for st, deg in in_degrees.items() if deg == 0])
    topo_order: List[str] = []

    while zero_in_queue:
        u = zero_in_queue.popleft()
        topo_order.append(u)
        for edge in graph.get_outgoing_edges(u):
            v = edge.target
            in_degrees[v] -= 1
            if in_degrees[v] == 0:
                zero_in_queue.append(v)

    if len(topo_order) < len(all_stations):
        raise ValueError("Graph contains a cycle; DAG shortest path algorithm requires an acyclic graph.")

    # 3. Relax edges in topological order
    distances: Dict[str, float] = {st: float("inf") for st in all_stations}
    distances[source] = 0.0
    predecessors: Dict[str, Optional[str]] = {st: None for st in all_stations}

    for u in topo_order:
        if distances[u] == float("inf"):
            continue
        for edge in graph.get_outgoing_edges(u):
            v = edge.target
            w = get_w(edge)
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessors[v] = u

    # 4. Reconstruct path
    path: List[str] = []
    total_cost = float("inf")
    if target is not None:
        if distances[target] < float("inf"):
            curr: Optional[str] = target
            while curr is not None:
                path.append(curr)
                curr = predecessors[curr]
            path.reverse()
            total_cost = distances[target]

    return ShortestPathResult(
        source=source,
        target=target,
        path=path,
        total_cost=total_cost,
        distances=distances,
        predecessors=predecessors,
        nodes_visited=len(topo_order),
        metric=metric,
    )


@dataclass
class FloydWarshallResult:
    """Pre-computed All-Pairs Shortest Path matrix and query interface.

    Attributes:
        stations: Indexed list of station names.
        dist_matrix: 2D dictionary mapping dist[u][v] = minimal cost.
        next_matrix: 2D dictionary mapping next_node[u][v] = intermediate station to reach v from u.
        metric: Optimization metric.
        has_negative_cycle: True if graph has negative cycles.
    """

    stations: List[str]
    dist_matrix: Dict[str, Dict[str, float]]
    next_matrix: Dict[str, Dict[str, Optional[str]]]
    metric: str
    has_negative_cycle: bool = False

    def get_distance(self, source: str, target: str) -> float:
        """Query shortest distance between any pair in O(1) time."""
        return self.dist_matrix[source][target]

    def get_path(self, source: str, target: str) -> List[str]:
        """Reconstruct shortest path in O(length) time."""
        if self.dist_matrix[source][target] == float("inf"):
            return []
        if source == target:
            return [source]

        path = [source]
        curr = source
        while curr != target:
            nxt = self.next_matrix[curr][target]
            if nxt is None:
                return []
            curr = nxt
            path.append(curr)
        return path


def floyd_warshall(
    graph: Graph,
    metric: MetricType = "distance",
    weight_fn: Optional[Callable[[Edge], float]] = None,
) -> FloydWarshallResult:
    """Compute All-Pairs Shortest Paths using the dynamic programming Floyd-Warshall algorithm.

    Why Floyd-Warshall?
    Computes shortest paths between every pair of vertices in O(V^3) time.
    Ideal for dense graphs or for pre-computing an instant O(1) all-pairs lookup table for passenger apps.

    DP Formulation:
        D^(k)[i][j] = min( D^(k-1)[i][j], D^(k-1)[i][k] + D^(k-1)[k][j] )

    Complexity:
        Time: O(V^3)
        Space: O(V^2) for distance and next-step routing matrices.
    """
    stations = graph.get_station_names()

    def get_w(edge: Edge) -> float:
        return weight_fn(edge) if weight_fn is not None else edge.get_weight(metric)

    # Initialize matrices
    dist: Dict[str, Dict[str, float]] = {u: {v: float("inf") for v in stations} for u in stations}
    nxt: Dict[str, Dict[str, Optional[str]]] = {u: {v: None for v in stations} for u in stations}

    for u in stations:
        dist[u][u] = 0.0
        nxt[u][u] = u

    for u in stations:
        for edge in graph.get_outgoing_edges(u):
            v = edge.target
            w = get_w(edge)
            if w < dist[u][v]:
                dist[u][v] = w
                nxt[u][v] = v

    # Dynamic programming relaxation over all intermediate vertices k
    for k in stations:
        for i in stations:
            for j in stations:
                if dist[i][k] != float("inf") and dist[k][j] != float("inf"):
                    alt = dist[i][k] + dist[k][j]
                    if alt < dist[i][j]:
                        dist[i][j] = alt
                        nxt[i][j] = nxt[i][k]

    # Negative cycle check: if dist[i][i] < 0
    has_neg_cycle = any(dist[i][i] < 0 for i in stations)

    return FloydWarshallResult(
        stations=stations,
        dist_matrix=dist,
        next_matrix=nxt,
        metric=metric,
        has_negative_cycle=has_neg_cycle,
    )
