"""Unit tests for Articulation Points and Bridges (Tarjan's DFS)."""

import pytest

from from_qom_to_new_york.algorithms.connectivity import find_articulation_points_and_bridges
from from_qom_to_new_york.core.data import build_qom_metro_graph
from from_qom_to_new_york.core.graph import Graph


def test_qom_metro_articulation_points_and_bridges():
    g = build_qom_metro_graph()
    res = find_articulation_points_and_bridges(g)

    # In Qom linear/tree branch structure, key hubs are articulation points
    assert len(res.articulation_points) > 0
    assert "Meydan Motahari" in res.articulation_points
    assert "Qaleh Kamkar" in res.articulation_points
    assert "Haram Motahhar Hazrat Masoumeh" in res.articulation_points

    # Terminal Mosaferbari <-> Qaleh Kamkar is a bridge (pendant edge)
    pair = tuple(sorted(("Terminal Mosaferbari Qom", "Qaleh Kamkar")))
    assert pair in res.bridges


def test_simple_cycle_has_no_bridges():
    # Triangle cycle A-B-C-A has 0 bridges and 0 articulation points
    g = Graph(is_directed=False)
    g.add_connection("A", "B", 1.0, 1.0)
    g.add_connection("B", "C", 1.0, 1.0)
    g.add_connection("C", "A", 1.0, 1.0)

    res = find_articulation_points_and_bridges(g)
    assert len(res.articulation_points) == 0
    assert len(res.bridges) == 0
