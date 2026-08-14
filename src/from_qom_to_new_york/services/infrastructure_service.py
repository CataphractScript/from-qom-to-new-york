"""Infrastructure Design and Network Optimization Service."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from from_qom_to_new_york.algorithms.mst import (
    MSTComparison,
    MSTResult,
    compare_mst_algorithms,
    kruskal_mst,
    prim_mst,
)
from from_qom_to_new_york.algorithms.shortest_path import (
    ShortestPathResult,
    bellman_ford,
    dag_shortest_path,
)
from from_qom_to_new_york.core.edge import MetricType
from from_qom_to_new_york.core.graph import Graph


class InfrastructureService:
    """Provides network design tools (MST, Express Line DAG, Negative Cycle Detection)."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._express_dag: Optional[Graph] = None

    def design_minimum_cost_network(
        self,
        algorithm: str = "kruskal",
        metric: MetricType = "distance",
    ) -> MSTResult:
        """Compute the Minimum Spanning Tree for the Qom transit network."""
        if algorithm.lower() == "kruskal":
            return kruskal_mst(self._graph, metric=metric)
        elif algorithm.lower() == "prim":
            return prim_mst(self._graph, metric=metric)
        raise ValueError(f"Unknown MST algorithm: '{algorithm}'. Choose 'kruskal' or 'prim'.")

    def compare_mst_algorithms(self, metric: MetricType = "distance") -> MSTComparison:
        """Run and compare Kruskal's and Prim's algorithms."""
        return compare_mst_algorithms(self._graph, metric=metric)

    def get_or_build_express_dag(self) -> Graph:
        """Build a dedicated one-way high-speed Express Line forming a Directed Acyclic Graph (DAG).

        Network Topology:
        North-to-South Express Trunk with High-Speed Skip-Stop Bypasses:
        - Terminal Mosaferbari Qom -> Qaleh Kamkar (1.2 km, 2.0 min)
        - Qaleh Kamkar -> Meydan Motahari (8.5 km, 8.0 min)
        - Meydan Motahari -> Bimarestan Nekouei (3.0 km, 3.5 min)
        - Bimarestan Nekouei -> Meydan Baghiatollah (2.0 km, 2.5 min)
        - Meydan Baghiatollah -> Pardisan (5.0 km, 5.0 min)
        - Pardisan -> University of Qom (2.2 km, 2.5 min)
        - University of Qom -> Masjed Moghaddas Jamkaran (4.5 km, 4.0 min)
        - Express Direct Bypass 1: Terminal Mosaferbari Qom -> Meydan Motahari (9.0 km, 7.0 min)
        - Express Direct Bypass 2: Meydan Motahari -> Pardisan (9.5 km, 8.0 min)
        - Express Direct Bypass 3: Pardisan -> Masjed Moghaddas Jamkaran (6.0 km, 5.0 min)

        This subnetwork is strictly acyclic (topologically ordered), allowing linear O(V + E) routing.
        """
        if self._express_dag is not None:
            return self._express_dag

        dag = Graph(is_directed=True)

        express_edges = [
            ("Terminal Mosaferbari Qom", "Qaleh Kamkar", 1.2, 2.0),
            ("Qaleh Kamkar", "Meydan Motahari", 8.5, 8.0),
            ("Meydan Motahari", "Bimarestan Nekouei", 3.0, 3.5),
            ("Bimarestan Nekouei", "Meydan Baghiatollah", 2.0, 2.5),
            ("Meydan Baghiatollah", "Pardisan", 5.0, 5.0),
            ("Pardisan", "University of Qom", 2.2, 2.5),
            ("University of Qom", "Masjed Moghaddas Jamkaran", 4.5, 4.0),
            # Express skip-stop bypasses
            ("Terminal Mosaferbari Qom", "Meydan Motahari", 9.0, 7.0),
            ("Meydan Motahari", "Pardisan", 9.5, 8.0),
            ("Pardisan", "Masjed Moghaddas Jamkaran", 6.0, 5.0),
        ]

        for src, dst, dist, tm in express_edges:
            dag.add_connection(
                source=src,
                target=dst,
                distance_km=dist,
                time_minutes=tm,
                capacity=10000,
                weight=dist,
                is_directed=True,
            )

        self._express_dag = dag
        return dag

    def compute_express_dag_shortest_path(
        self,
        source: str,
        target: str,
        metric: MetricType = "time",
    ) -> ShortestPathResult:
        """Find the optimal express route along the one-way DAG express line in O(V + E) time."""
        dag = self.get_or_build_express_dag()
        return dag_shortest_path(dag, source=source, target=target, metric=metric)

    def evaluate_negative_weights(
        self,
        source: str,
        target: Optional[str] = None,
        inject_test_negative_cycle: bool = False,
    ) -> ShortestPathResult:
        """Run Bellman-Ford to find shortest paths under promotional incentives and test for negative cycles.

        Args:
            source: Departure station.
            target: Destination station.
            inject_test_negative_cycle: If True, injects an intentional negative cycle to demonstrate
                                       robust detection and extraction.
        """
        # Create a directed copy for Bellman-Ford
        bf_graph = Graph(is_directed=True)
        for st in self._graph.get_all_stations():
            bf_graph.add_station(st)

        for edge in self._graph.get_all_edges(deduplicate_undirected=False):
            # Apply promotional incentive discounts on select lines
            discount = 0.0
            if "Jamkaran" in edge.target or "Haram" in edge.target:
                discount = -1.0  # Pilgrimage promotional subsidy

            bf_graph.add_connection(
                source=edge.source,
                target=edge.target,
                distance_km=edge.distance_km,
                time_minutes=edge.time_minutes,
                capacity=edge.capacity,
                weight=edge.distance_km + discount,
                is_directed=True,
            )

        if inject_test_negative_cycle:
            # Inject a negative cycle: Motahari -> Haram (-10) -> Arg (-10) -> Motahari (-10)
            bf_graph.add_connection("Meydan Motahari", "Haram Motahhar Hazrat Masoumeh", 1.5, 4.0, weight=-10.0, is_directed=True)
            bf_graph.add_connection("Haram Motahhar Hazrat Masoumeh", "Arg Salariyeh", 1.0, 3.0, weight=-10.0, is_directed=True)
            bf_graph.add_connection("Arg Salariyeh", "Meydan Motahari", 2.0, 5.0, weight=-10.0, is_directed=True)

        return bellman_ford(bf_graph, source=source, target=target, metric="cost")
