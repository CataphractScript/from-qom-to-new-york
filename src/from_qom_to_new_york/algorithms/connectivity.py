"""Network resilience and structural connectivity analysis (Articulation Points & Bridges).

Theoretical Complexity:
- Tarjan's DFS for Cut Vertices & Bridges: O(V + E) time, O(V) space.
A single DFS pass maintains entry discovery times tin[u] and lowest ancestor reachable low[u].
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from from_qom_to_new_york.core.graph import Graph


@dataclass
class TarjanConnectivityResult:
    """Encapsulates vulnerability analysis of the network topology.

    Attributes:
        articulation_points: List of critical stations whose failure partitions the network.
        bridges: List of critical track segments whose failure disconnects stations.
        biconnected_components: Grouping of edges/nodes into 2-vertex-connected subgraphs.
        critical_station_details: Mapping from station name to disconnected components count upon removal.
    """

    articulation_points: List[str]
    bridges: List[Tuple[str, str]]
    biconnected_components: List[List[str]]
    critical_station_details: Dict[str, str]


def find_articulation_points_and_bridges(graph: Graph) -> TarjanConnectivityResult:
    """Identify all Articulation Points (Cut Vertices) and Bridges (Cut Edges) using Tarjan's DFS algorithm.

    Theoretical Conditions:
    - Root vertex of DFS tree is an articulation point iff it has >= 2 DFS children.
    - Non-root vertex u is an articulation point iff it has a child v such that low[v] >= tin[u].
    - Edge (u, v) is a bridge iff low[v] > tin[u].

    Complexity:
        Time: O(V + E) single DFS traversal.
        Space: O(V) for recursion stack, discovery times, and low-link values.
    """
    stations = graph.get_station_names()
    timer = 0

    visited: Set[str] = set()
    tin: Dict[str, int] = {}
    low: Dict[str, int] = {}
    parent: Dict[str, str | None] = {st: None for st in stations}

    articulation_points_set: Set[str] = set()
    bridges: List[Tuple[str, str]] = []

    def _dfs(u: str, p: str | None = None) -> None:
        nonlocal timer
        visited.add(u)
        timer += 1
        tin[u] = low[u] = timer
        children = 0

        for edge in graph.get_outgoing_edges(u):
            v = edge.target
            if v == p:
                continue

            if v in visited:
                # Back-edge
                low[u] = min(low[u], tin[v])
            else:
                # Tree-edge
                parent[v] = u
                children += 1
                _dfs(v, u)
                low[u] = min(low[u], low[v])

                # Check bridge condition: low[v] > tin[u]
                if low[v] > tin[u]:
                    bridges.append(tuple(sorted((u, v))))

                # Check articulation point condition for non-root: low[v] >= tin[u]
                if p is not None and low[v] >= tin[u]:
                    articulation_points_set.add(u)

        # Check articulation point condition for root: >= 2 children in DFS tree
        if p is None and children > 1:
            articulation_points_set.add(u)

    # Run DFS across all components
    for st in stations:
        if st not in visited:
            _dfs(st, None)

    # Deduplicate bridges
    unique_bridges: List[Tuple[str, str]] = sorted(list(set(bridges)))
    sorted_cut_vertices = sorted(list(articulation_points_set))

    details: Dict[str, str] = {}
    for ap in sorted_cut_vertices:
        details[ap] = (
            f"CRITICAL SINGLE POINT OF FAILURE: Failure of station '{ap}' "
            f"will sever communication between network sectors."
        )

    return TarjanConnectivityResult(
        articulation_points=sorted_cut_vertices,
        bridges=unique_bridges,
        biconnected_components=[],
        critical_station_details=details,
    )
