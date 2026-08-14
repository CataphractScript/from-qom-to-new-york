"""Maximum Flow and Minimum Cut algorithms (Edmonds-Karp / Ford-Fulkerson).

Theoretical Complexity:
- Edmonds-Karp: O(V * E^2) time, O(V + E) space.
Uses BFS to always select the shortest augmenting path in the residual network,
guaranteeing termination in at most O(V * E) augmenting steps.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from from_qom_to_new_york.core.edge import Edge
from from_qom_to_new_york.core.graph import Graph


@dataclass
class FlowResult:
    """Encapsulates the output of a network flow analysis.

    Attributes:
        source: Source station name.
        sink: Sink (destination) station name.
        max_flow: Maximum throughput (passengers/hour) from source to sink.
        flow_on_edges: Dictionary mapping (u, v) directed track pairs to assigned passenger flow.
        min_cut_source_set: Subset of vertices reachable from source in residual graph (S).
        min_cut_sink_set: Subset of vertices partitioned with the sink (T = V - S).
        bottleneck_edges: List of saturated edges spanning across the S-T cut boundary.
    """

    source: str
    sink: str
    max_flow: float
    flow_on_edges: Dict[Tuple[str, str], float]
    min_cut_source_set: Set[str]
    min_cut_sink_set: Set[str]
    bottleneck_edges: List[Edge]


def edmonds_karp_max_flow(
    graph: Graph,
    source: str,
    sink: str,
    capacity_attr: str = "capacity",
) -> FlowResult:
    """Compute the maximum passenger flow from source to sink using the Edmonds-Karp algorithm.

    Also identifies the Minimum Cut (the critical transit bottlenecks in accordance with the
    Max-Flow Min-Cut Theorem).

    Args:
        graph: Transit network graph.
        source: Inflow terminal station.
        sink: Outflow destination station.
        capacity_attr: Attribute name for capacity on Edge objects.

    Returns:
        FlowResult with max flow volume, edge flows, and min-cut bottlenecks.
    """
    if not graph.has_station(source):
        raise ValueError(f"Source station '{source}' not found in graph.")
    if not graph.has_station(sink):
        raise ValueError(f"Sink station '{sink}' not found in graph.")
    if source == sink:
        raise ValueError("Source and sink stations cannot be the same.")

    stations = graph.get_station_names()

    # Build capacity matrix
    capacities: Dict[Tuple[str, str], float] = {}
    for u in stations:
        for v in stations:
            capacities[(u, v)] = 0.0

    original_edges: Dict[Tuple[str, str], Edge] = {}

    for u in stations:
        for edge in graph.get_outgoing_edges(u):
            v = edge.target
            cap = float(getattr(edge, capacity_attr, edge.capacity))
            capacities[(u, v)] += cap
            original_edges[(u, v)] = edge

    # Residual network flows
    flow: Dict[Tuple[str, str], float] = {k: 0.0 for k in capacities}

    def _bfs_find_path() -> Tuple[bool, Dict[str, str], float]:
        """Find the shortest augmenting path from source to sink in residual network."""
        parent: Dict[str, str] = {}
        visited: Set[str] = {source}
        queue: deque[Tuple[str, float]] = deque([(source, float("inf"))])

        while queue:
            curr, bottleneck = queue.popleft()

            if curr == sink:
                return True, parent, bottleneck

            for v in stations:
                # Residual capacity = capacity - current_flow
                res_cap = capacities.get((curr, v), 0.0) - flow.get((curr, v), 0.0)
                if v not in visited and res_cap > 1e-9:
                    visited.add(v)
                    parent[v] = curr
                    new_bottleneck = min(bottleneck, res_cap)
                    queue.append((v, new_bottleneck))

        return False, {}, 0.0

    total_max_flow = 0.0

    while True:
        path_found, parent, push_amount = _bfs_find_path()
        if not path_found or push_amount <= 0:
            break

        # Augment flow along the path
        curr = sink
        while curr != source:
            prev = parent[curr]
            flow[(prev, curr)] += push_amount
            flow[(curr, prev)] -= push_amount
            curr = prev

        total_max_flow += push_amount

    # Compute Minimum Cut via reachable vertices in residual network from source
    cut_visited: Set[str] = {source}
    cut_queue: deque[str] = deque([source])

    while cut_queue:
        curr = cut_queue.popleft()
        for v in stations:
            res_cap = capacities.get((curr, v), 0.0) - flow.get((curr, v), 0.0)
            if v not in cut_visited and res_cap > 1e-9:
                cut_visited.add(v)
                cut_queue.append(v)

    min_cut_source = cut_visited
    min_cut_sink = set(stations) - cut_visited

    # Identify bottleneck edges spanning from S to T
    bottlenecks: List[Edge] = []
    active_flows: Dict[Tuple[str, str], float] = {}

    for (u, v), f_val in flow.items():
        if f_val > 1e-9:
            active_flows[(u, v)] = round(f_val, 2)
            if u in min_cut_source and v in min_cut_sink:
                if (u, v) in original_edges:
                    bottlenecks.append(original_edges[(u, v)])

    return FlowResult(
        source=source,
        sink=sink,
        max_flow=round(total_max_flow, 2),
        flow_on_edges=active_flows,
        min_cut_source_set=min_cut_source,
        min_cut_sink_set=min_cut_sink,
        bottleneck_edges=bottlenecks,
    )
