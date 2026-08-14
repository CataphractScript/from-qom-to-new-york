"""Unit tests for Minimum Spanning Tree algorithms (Kruskal, Prim, and comparison)."""

import pytest

from from_qom_to_new_york.algorithms.mst import compare_mst_algorithms, kruskal_mst, prim_mst
from from_qom_to_new_york.core.data import build_qom_metro_graph


def test_kruskal_and_prim_produce_identical_mst_weight():
    g = build_qom_metro_graph()

    k_res = kruskal_mst(g, metric="distance")
    p_res = prim_mst(g, metric="distance")

    assert k_res.is_connected is True
    assert p_res.is_connected is True
    assert len(k_res.mst_edges) == 19  # |V| - 1 = 20 - 1 = 19
    assert len(p_res.mst_edges) == 19

    # Both algorithms must yield identical minimum spanning cost
    assert abs(k_res.total_weight - p_res.total_weight) < 1e-6
    assert k_res.total_weight == 47.1


def test_compare_mst_helper():
    g = build_qom_metro_graph()
    comp = compare_mst_algorithms(g, metric="distance")
    assert comp.weights_match is True
    assert comp.edge_count == 19
    assert "Kruskal" in comp.analysis
    assert "Prim" in comp.analysis
