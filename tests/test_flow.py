"""Unit tests for Maximum Flow and Minimum Cut (Edmonds-Karp)."""

import pytest

from from_qom_to_new_york.algorithms.flow import edmonds_karp_max_flow
from from_qom_to_new_york.core.data import build_qom_metro_graph
from from_qom_to_new_york.core.graph import Graph


def test_qom_metro_max_flow():
    g = build_qom_metro_graph()
    src = "Terminal Mosaferbari Qom"
    sink = "Masjed Moghaddas Jamkaran"

    res = edmonds_karp_max_flow(g, source=src, sink=sink)
    assert res.max_flow > 0
    assert res.source == src
    assert res.sink == sink
    assert len(res.bottleneck_edges) >= 1
    assert src in res.min_cut_source_set
    assert sink in res.min_cut_sink_set


def test_custom_flow_network():
    g = Graph(is_directed=True)
    g.add_connection("S", "A", 1.0, 1.0, capacity=10, is_directed=True)
    g.add_connection("S", "B", 1.0, 1.0, capacity=10, is_directed=True)
    g.add_connection("A", "T", 1.0, 1.0, capacity=10, is_directed=True)
    g.add_connection("B", "T", 1.0, 1.0, capacity=10, is_directed=True)
    g.add_connection("A", "B", 1.0, 1.0, capacity=2, is_directed=True)

    res = edmonds_karp_max_flow(g, source="S", sink="T")
    assert res.max_flow == 20.0
