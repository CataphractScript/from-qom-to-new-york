"""Graph search and traversal algorithms (BFS, DFS, Reachability, Components).

Theoretical Complexity:
- BFS (Breadth-First Search): O(V + E) time, O(V) space.
- DFS (Depth-First Search): O(V + E) time, O(V) space.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from from_qom_to_new_york.core.graph import Graph


@dataclass
class SearchResult:
    """Result container for graph search traversals.

    Attributes:
        reachable: Whether target vertex was reachable from source.
        path: Ordered list of station names forming the discovered path, or None if unreachable.
        visited_count: Number of vertices explored during traversal.
        visited_order: Full sequence of vertices in order of exploration.
        distance_hops: Number of edge transitions (unweighted hop count).
    """

    reachable: bool
    path: Optional[List[str]]
    visited_count: int
    visited_order: List[str]
    distance_hops: Optional[int] = None


def bfs_connectivity(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
) -> SearchResult:
    """Perform Breadth-First Search (BFS) to explore reachable vertices or find shortest unweighted path.

    Why BFS?
    BFS explores the graph in concentric rings (level-order), guaranteeing the minimum number of
    hops (unweighted shortest path) between source and any reachable vertex.

    Args:
        graph: The transit graph.
        source: Departure station name.
        target: Optional destination station name. If None, explores the entire component.

    Returns:
        SearchResult containing reachability, path, and exploration metadata.

    Complexity:
        Time: O(V + E) where V is vertex count and E is edge count.
        Space: O(V) for visited set and FIFO queue.
    """
    if not graph.has_station(source):
        raise ValueError(f"Source station '{source}' not found in graph.")
    if target is not None and not graph.has_station(target):
        raise ValueError(f"Target station '{target}' not found in graph.")

    visited_set: Set[str] = {source}
    visited_order: List[str] = []
    parent: Dict[str, Optional[str]] = {source: None}
    queue: deque[str] = deque([source])

    found = False

    while queue:
        curr = queue.popleft()
        visited_order.append(curr)

        if target is not None and curr == target:
            found = True
            break

        for neighbor in graph.get_neighbors(curr):
            if neighbor not in visited_set:
                visited_set.add(neighbor)
                parent[neighbor] = curr
                queue.append(neighbor)

    if target is None:
        return SearchResult(
            reachable=True,
            path=None,
            visited_count=len(visited_order),
            visited_order=visited_order,
            distance_hops=None,
        )

    if not found and target not in visited_set:
        return SearchResult(
            reachable=False,
            path=None,
            visited_count=len(visited_order),
            visited_order=visited_order,
            distance_hops=None,
        )

    # Reconstruct path from target back to source
    path: List[str] = []
    curr_node: Optional[str] = target
    while curr_node is not None:
        path.append(curr_node)
        curr_node = parent.get(curr_node)
    path.reverse()

    return SearchResult(
        reachable=True,
        path=path,
        visited_count=len(visited_order),
        visited_order=visited_order,
        distance_hops=len(path) - 1,
    )


def dfs_connectivity(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
) -> SearchResult:
    """Perform Depth-First Search (DFS) to explore reachability or find a path.

    Why DFS?
    DFS dives deep along paths before backtracking, useful for topological sorting, cycle detection,
    and exploring deep structural components.

    Args:
        graph: The transit graph.
        source: Departure station name.
        target: Optional destination station name.

    Returns:
        SearchResult containing reachability, path, and exploration metadata.

    Complexity:
        Time: O(V + E).
        Space: O(V) for the recursion/call stack and visited tracker.
    """
    if not graph.has_station(source):
        raise ValueError(f"Source station '{source}' not found in graph.")
    if target is not None and not graph.has_station(target):
        raise ValueError(f"Target station '{target}' not found in graph.")

    visited_set: Set[str] = set()
    visited_order: List[str] = []
    parent: Dict[str, Optional[str]] = {}
    found = False

    def _dfs(u: str) -> bool:
        nonlocal found
        visited_set.add(u)
        visited_order.append(u)

        if target is not None and u == target:
            found = True
            return True

        for v in graph.get_neighbors(u):
            if v not in visited_set:
                parent[v] = u
                if _dfs(v):
                    return True
        return False

    parent[source] = None
    _dfs(source)

    if target is None:
        return SearchResult(
            reachable=True,
            path=None,
            visited_count=len(visited_order),
            visited_order=visited_order,
            distance_hops=None,
        )

    if not found:
        return SearchResult(
            reachable=False,
            path=None,
            visited_count=len(visited_order),
            visited_order=visited_order,
            distance_hops=None,
        )

    # Reconstruct path
    path: List[str] = []
    curr_node: Optional[str] = target
    while curr_node is not None:
        path.append(curr_node)
        curr_node = parent.get(curr_node)
    path.reverse()

    return SearchResult(
        reachable=True,
        path=path,
        visited_count=len(visited_order),
        visited_order=visited_order,
        distance_hops=len(path) - 1,
    )


def is_connected(graph: Graph) -> bool:
    """Check whether the entire graph forms a single connected component.

    Complexity: O(V + E) using BFS from an arbitrary starting vertex.
    """
    stations = graph.get_station_names()
    if not stations:
        return True
    res = bfs_connectivity(graph, source=stations[0])
    return res.visited_count == graph.order


def get_connected_components(graph: Graph) -> List[List[str]]:
    """Partition all stations into maximal connected components.

    Returns:
        List of components, where each component is a list of station names.

    Complexity: O(V + E) overall time.
    """
    visited: Set[str] = set()
    components: List[List[str]] = []

    for name in graph.get_station_names():
        if name not in visited:
            res = bfs_connectivity(graph, source=name)
            comp = res.visited_order
            visited.update(comp)
            components.append(comp)

    return components
