"""Adjacency List Graph representation for the transit network.

Design Justification (Adjacency List vs. Adjacency Matrix):
1. Space Efficiency: The Qom metro network is a sparse planar graph with |V| = 20 vertices and |E| = 21 edges.
   - Adjacency Matrix requires O(V^2) = 400 cells, the vast majority being 0/infinity (90%+ sparsity).
   - Adjacency List requires O(V + E) = 41 references, conserving memory.
2. Traversal Efficiency:
   - Iterating over incident neighbors of vertex v in an adjacency list takes O(deg(v)) time (average degree ~ 2.1).
   - In an adjacency matrix, finding neighbors requires an O(V) full row scan regardless of degree.
   - Core traversal algorithms (BFS, DFS, Dijkstra with min-heap) achieve optimal O((V + E) log V) or O(V + E) bounds.
"""

from __future__ import annotations

from typing import Callable, Dict, Iterator, List, Optional, Set, Tuple

from from_qom_to_new_york.core.edge import Edge, MetricType
from from_qom_to_new_york.core.station import Coordinates, Station


class Graph:
    """Represents a transit graph using an adjacency list.

    Supports both directed and undirected multi-modal networks with weighted edges.
    """

    def __init__(self, is_directed: bool = False) -> None:
        """Initialize an empty graph.

        Args:
            is_directed: If True, edges added without explicit direction are treated as directed.
        """
        self.is_directed: bool = is_directed
        self._stations: Dict[str, Station] = {}
        self._adj: Dict[str, List[Edge]] = {}

    def add_station(self, station: Station) -> None:
        """Register a new station vertex in the graph.

        Args:
            station: The Station instance to add.
        """
        if station.name not in self._stations:
            self._stations[station.name] = station
            self._adj[station.name] = []

    def add_station_by_name(
        self,
        name: str,
        station_id: Optional[int] = None,
        coordinates: Optional[Coordinates] = None,
        is_terminal: bool = False,
        is_transfer: bool = False,
    ) -> Station:
        """Helper to create and register a station vertex by name.

        Args:
            name: Station name.
            station_id: Optional unique integer ID (defaults to current vertex count + 1).
            coordinates: Optional geographic coordinates.
            is_terminal: Flag for major terminal.
            is_transfer: Flag for transfer hub.

        Returns:
            The created Station object.
        """
        if name in self._stations:
            return self._stations[name]

        sid = station_id if station_id is not None else len(self._stations) + 1
        st = Station(
            id=sid,
            name=name,
            coordinates=coordinates,
            is_terminal=is_terminal,
            is_transfer=is_transfer,
        )
        self.add_station(st)
        return st

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph.

        If the graph is undirected and edge is not explicitly directed,
        both forward (u -> v) and reverse (v -> u) entries are inserted.

        Args:
            edge: Edge object connecting source and target.
        """
        # Ensure endpoint vertices exist
        if edge.source not in self._stations:
            self.add_station_by_name(edge.source)
        if edge.target not in self._stations:
            self.add_station_by_name(edge.target)

        self._adj[edge.source].append(edge)

        if not self.is_directed and not edge.is_directed:
            rev_edge = edge.reverse()
            self._adj[edge.target].append(rev_edge)

    def add_connection(
        self,
        source: str,
        target: str,
        distance_km: float,
        time_minutes: float,
        capacity: int = 5000,
        weight: float = 0.0,
        is_directed: Optional[bool] = None,
    ) -> Edge:
        """Convenience method to create and insert an edge by vertex names.

        Args:
            source: Name of source station.
            target: Name of target station.
            distance_km: Distance in km.
            time_minutes: Travel time in minutes.
            capacity: Passenger capacity per hour.
            weight: Custom cost weight (defaults to distance_km if 0.0).
            is_directed: Optional direction override (defaults to graph's is_directed).

        Returns:
            The created Edge instance.
        """
        directed_flag = self.is_directed if is_directed is None else is_directed
        edge = Edge(
            source=source,
            target=target,
            distance_km=distance_km,
            time_minutes=time_minutes,
            capacity=capacity,
            weight=weight if weight != 0.0 else distance_km,
            is_directed=directed_flag,
        )
        self.add_edge(edge)
        return edge

    def get_station(self, name: str) -> Optional[Station]:
        """Retrieve Station metadata by name."""
        return self._stations.get(name)

    def has_station(self, name: str) -> bool:
        """Check if station exists in graph."""
        return name in self._stations

    def get_outgoing_edges(self, station_name: str) -> List[Edge]:
        """Get all outgoing edges starting from station_name."""
        return self._adj.get(station_name, [])

    def get_neighbors(self, station_name: str) -> List[str]:
        """Get list of adjacent station names reachable from station_name."""
        return [edge.target for edge in self.get_outgoing_edges(station_name)]

    def get_edge(self, source: str, target: str) -> Optional[Edge]:
        """Retrieve edge connecting source to target if one exists."""
        for edge in self.get_outgoing_edges(source):
            if edge.target == target:
                return edge
        return None

    def get_all_stations(self) -> List[Station]:
        """Return list of all registered stations."""
        return list(self._stations.values())

    def get_station_names(self) -> List[str]:
        """Return list of all registered station names."""
        return list(self._stations.keys())

    def get_all_edges(self, deduplicate_undirected: bool = True) -> List[Edge]:
        """Retrieve all edges in the graph.

        Args:
            deduplicate_undirected: If True on undirected graphs, returns only one representative
                                   edge per bidirectional pair (u, v) where u < v.

        Returns:
            List of Edge objects.
        """
        edges: List[Edge] = []
        seen: Set[Tuple[str, str]] = set()

        for u, edge_list in self._adj.items():
            for edge in edge_list:
                if deduplicate_undirected and not self.is_directed and not edge.is_directed:
                    pair = tuple(sorted([edge.source, edge.target]))
                    if pair in seen:
                        continue
                    seen.add(pair)
                edges.append(edge)
        return edges

    def degree(self, station_name: str) -> int:
        """Degree (number of incident connections) of a station."""
        return len(self.get_outgoing_edges(station_name))

    @property
    def order(self) -> int:
        """Number of vertices |V| in the graph."""
        return len(self._stations)

    @property
    def size(self) -> int:
        """Number of distinct edges |E| in the graph."""
        return len(self.get_all_edges(deduplicate_undirected=True))

    def clone(self) -> Graph:
        """Create a deep copy of the graph topology and metadata."""
        new_g = Graph(is_directed=self.is_directed)
        for st in self._stations.values():
            new_g.add_station(
                Station(
                    id=st.id,
                    name=st.name,
                    coordinates=st.coordinates,
                    is_terminal=st.is_terminal,
                    is_transfer=st.is_transfer,
                    daily_capacity=st.daily_capacity,
                    facilities=list(st.facilities),
                )
            )
        for edge in self.get_all_edges(deduplicate_undirected=False):
            if not self.is_directed and not edge.is_directed:
                # Add only once for undirected clone
                if edge.source < edge.target:
                    new_g.add_connection(
                        source=edge.source,
                        target=edge.target,
                        distance_km=edge.distance_km,
                        time_minutes=edge.time_minutes,
                        capacity=edge.capacity,
                        weight=edge.weight,
                        is_directed=edge.is_directed,
                    )
            else:
                new_g.add_connection(
                    source=edge.source,
                    target=edge.target,
                    distance_km=edge.distance_km,
                    time_minutes=edge.time_minutes,
                    capacity=edge.capacity,
                    weight=edge.weight,
                    is_directed=edge.is_directed,
                )
        return new_g

    def __len__(self) -> int:
        return self.order

    def __iter__(self) -> Iterator[Station]:
        return iter(self._stations.values())

    def __repr__(self) -> str:
        gtype = "Directed" if self.is_directed else "Undirected"
        return f"Graph({gtype}, |V|={self.order}, |E|={self.size})"
