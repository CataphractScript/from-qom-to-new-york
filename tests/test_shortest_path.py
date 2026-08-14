"""Unit tests for Shortest Path algorithms (Dijkstra, Bellman-Ford, DAG, Floyd-Warshall)."""

import pytest

from from_qom_to_new_york.algorithms.shortest_path import (
    bellman_ford,
    dag_shortest_path,
    dijkstra,
    floyd_warshall,
)
from from_qom_to_new_york.core.data import build_qom_metro_graph
from from_qom_to_new_york.core.graph import Graph


def test_dijkstra_distance_and_time():
    g = build_qom_metro_graph()
    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"

    res_dist = dijkstra(g, source=src, target=dst, metric="distance")
    assert res_dist.total_cost == 18.5
    assert res_dist.path[0] == src
    assert res_dist.path[-1] == dst
    assert len(res_dist.path) == 7

    res_time = dijkstra(g, source=src, target=dst, metric="time")
    assert res_time.total_cost > 0
    assert res_time.path[0] == src
    assert res_time.path[-1] == dst


def test_floyd_warshall_all_pairs():
    g = build_qom_metro_graph()
    fw_res = floyd_warshall(g, metric="distance")

    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"

    # Floyd-Warshall distance should match Dijkstra distance exactly
    dijkstra_res = dijkstra(g, source=src, target=dst, metric="distance")
    assert abs(fw_res.get_distance(src, dst) - dijkstra_res.total_cost) < 1e-6

    fw_path = fw_res.get_path(src, dst)
    assert fw_path == dijkstra_res.path


def test_dag_shortest_path():
    dag = Graph(is_directed=True)
    dag.add_connection("A", "B", distance_km=5.0, time_minutes=5.0, is_directed=True)
    dag.add_connection("B", "C", distance_km=3.0, time_minutes=3.0, is_directed=True)
    dag.add_connection("A", "C", distance_km=10.0, time_minutes=10.0, is_directed=True)

    res = dag_shortest_path(dag, source="A", target="C", metric="distance")
    assert res.total_cost == 8.0
    assert res.path == ["A", "B", "C"]


def test_bellman_ford_no_negative_cycle():
    g = build_qom_metro_graph()
    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"

    res = bellman_ford(g, source=src, target=dst, metric="distance")
    assert res.has_negative_cycle is False
    assert abs(res.total_cost - 18.5) < 1e-6


def test_bellman_ford_detects_negative_cycle():
    g = Graph(is_directed=True)
    g.add_connection("A", "B", 1.0, 1.0, weight=1.0, is_directed=True)
    g.add_connection("B", "C", 1.0, 1.0, weight=-5.0, is_directed=True)
    g.add_connection("C", "A", 1.0, 1.0, weight=2.0, is_directed=True)  # Cycle A->B->C->A has weight -2.0

    res = bellman_ford(g, source="A", metric="cost")
    assert res.has_negative_cycle is True
    assert res.negative_cycle is not None
