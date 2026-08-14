"""Unit tests for Round 5 Innovations (A*, Bidirectional Dijkstra, Dynamic Congestion, ALT)."""

import pytest

from from_qom_to_new_york.algorithms.advanced import (
    ALTAlgorithm,
    astar_search,
    bidirectional_dijkstra,
    compare_dijkstra_vs_astar,
    dynamic_congestion_aware_dijkstra,
)
from from_qom_to_new_york.algorithms.shortest_path import dijkstra
from from_qom_to_new_york.core.data import build_qom_metro_graph


def test_astar_finds_optimal_path_with_fewer_expansions():
    g = build_qom_metro_graph()
    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"

    dijkstra_res = dijkstra(g, source=src, target=dst, metric="distance")
    astar_res = astar_search(g, source=src, target=dst, metric="distance")

    # Path cost must be strictly optimal (matching Dijkstra)
    assert abs(astar_res.total_cost - dijkstra_res.total_cost) < 1e-6
    assert astar_res.path == dijkstra_res.path

    # A* directed heuristic explores fewer or equal nodes
    assert astar_res.nodes_visited <= dijkstra_res.nodes_visited


def test_bidirectional_dijkstra():
    g = build_qom_metro_graph()
    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"

    dijkstra_res = dijkstra(g, source=src, target=dst, metric="distance")
    bi_res = bidirectional_dijkstra(g, source=src, target=dst, metric="distance")

    assert abs(bi_res.total_cost - dijkstra_res.total_cost) < 1e-6
    assert bi_res.path[0] == src
    assert bi_res.path[-1] == dst


def test_dynamic_congestion_routing():
    g = build_qom_metro_graph()
    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"

    # Simulate heavy saturation on primary corridor
    heavy_flows = {
        ("Meydan Motahari", "Bimarestan Nekouei"): 6000.0,
        ("Bimarestan Nekouei", "Meydan Baghiatollah"): 6000.0,
    }

    res = dynamic_congestion_aware_dijkstra(g, src, dst, passenger_flows=heavy_flows)
    assert res.static_shortest_path[0] == src
    assert res.dynamic_optimal_path[0] == src
    assert res.dynamic_cost_minutes >= res.static_cost_minutes


def test_alt_algorithm():
    g = build_qom_metro_graph()
    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"

    dijkstra_res = dijkstra(g, source=src, target=dst, metric="distance")
    alt_engine = ALTAlgorithm(g, metric="distance")
    alt_res = alt_engine.search(src, dst)

    assert abs(alt_res.total_cost - dijkstra_res.total_cost) < 1e-6
    assert alt_res.path == dijkstra_res.path
