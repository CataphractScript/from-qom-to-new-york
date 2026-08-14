"""Unified System Facade orchestrating all metro sub-services."""

from __future__ import annotations

from typing import Optional

from from_qom_to_new_york.core.data import build_qom_metro_graph
from from_qom_to_new_york.core.graph import Graph
from from_qom_to_new_york.services.analysis_service import AnalysisService
from from_qom_to_new_york.services.infrastructure_service import InfrastructureService
from from_qom_to_new_york.services.operations_service import OperationsService
from from_qom_to_new_york.services.routing_service import RoutingService


class MetroSystem:
    """Unified Facade for the Qom Metro Transit Optimization Platform.

    Provides single-point access to:
    - Core Graph Topology
    - Routing and Navigation Engine (Dijkstra, A*, Bi-Dijkstra, Floyd-Warshall)
    - Infrastructure Optimization (Kruskal, Prim, Express DAG, Bellman-Ford)
    - Daily Transit Operations (Platform Scheduling, Dispatch Min-Heap, Traffic Analytics, Simulation)
    - Network Diagnostics (Max-Flow/Min-Cut, Articulation Points, Bridges, Dominating Set, Fuzzy Search)
    """

    def __init__(self, graph: Optional[Graph] = None) -> None:
        self.graph: Graph = graph if graph is not None else build_qom_metro_graph()
        self.routing: RoutingService = RoutingService(self.graph)
        self.infrastructure: InfrastructureService = InfrastructureService(self.graph)
        self.operations: OperationsService = OperationsService(self.graph)
        self.analysis: AnalysisService = AnalysisService(self.graph)

    @classmethod
    def create_default(cls) -> MetroSystem:
        """Create and initialize the standard Qom Metro system instance."""
        return cls(build_qom_metro_graph())
