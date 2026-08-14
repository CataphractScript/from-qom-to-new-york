"""Unit tests for Graph data structures and Disjoint Set Union (DSU)."""

import pytest

from from_qom_to_new_york.core.data import OFFICIAL_STATIONS, build_qom_metro_graph
from from_qom_to_new_york.core.dsu import DisjointSetUnion
from from_qom_to_new_york.core.edge import Edge
from from_qom_to_new_york.core.graph import Graph
from from_qom_to_new_york.core.station import Coordinates, Station


def test_dsu_basic_operations():
    dsu: DisjointSetUnion[str] = DisjointSetUnion(["A", "B", "C", "D", "E"])
    assert len(dsu) == 5
    assert dsu.num_components == 5

    assert dsu.union("A", "B") is True
    assert dsu.num_components == 4
    assert dsu.connected("A", "B") is True
    assert dsu.connected("A", "C") is False

    # Redundant union
    assert dsu.union("A", "B") is False
    assert dsu.num_components == 4

    assert dsu.union("C", "D") is True
    assert dsu.union("B", "D") is True
    assert dsu.num_components == 2
    assert dsu.connected("A", "C") is True
    assert dsu.connected("A", "E") is False


def test_coordinates_distance():
    # Qom coordinates
    c1 = Coordinates(latitude=34.6416, longitude=50.8794)  # Haram
    c2 = Coordinates(latitude=34.6465, longitude=50.8785)  # Motahari

    euclidean_d = c1.euclidean_distance_to(c2)
    haversine_d = c1.haversine_distance_to(c2)

    assert euclidean_d > 0
    assert haversine_d > 0
    # Distance between Haram and Motahari in straight line is approx 0.5 - 0.7 km
    assert 0.3 <= haversine_d <= 1.0


def test_graph_initialization_and_order():
    g = build_qom_metro_graph()
    assert g.order == 20
    assert g.size == 21
    assert len(g.get_all_stations()) == 20
    assert len(g.get_all_edges(deduplicate_undirected=True)) == 21

    # Verify key stations exist
    assert g.has_station("Haram Motahhar Hazrat Masoumeh")
    assert g.has_station("Masjed Moghaddas Jamkaran")
    assert g.has_station("Terminal Mosaferbari Qom")


def test_graph_edge_properties():
    g = build_qom_metro_graph()
    edge = g.get_edge("Terminal Mosaferbari Qom", "Qaleh Kamkar")
    assert edge is not None
    assert edge.distance_km == 1.2
    assert edge.time_minutes == 3.0
    assert edge.get_weight("distance") == 1.2
    assert edge.get_weight("time") == 3.0


def test_graph_clone():
    g = build_qom_metro_graph()
    cloned = g.clone()
    assert cloned.order == g.order
    assert cloned.size == g.size
    assert cloned.get_station_names() == g.get_station_names()
