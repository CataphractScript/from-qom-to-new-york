"""Unit tests for Search algorithms (BFS, DFS, Connectivity, Components)."""

import pytest

from from_qom_to_new_york.algorithms.search import (
    bfs_connectivity,
    dfs_connectivity,
    get_connected_components,
    is_connected,
)
from from_qom_to_new_york.core.data import build_qom_metro_graph
from from_qom_to_new_york.core.graph import Graph


def test_qom_graph_is_fully_connected():
    g = build_qom_metro_graph()
    assert is_connected(g) is True
    comps = get_connected_components(g)
    assert len(comps) == 1
    assert len(comps[0]) == 20


def test_bfs_connectivity():
    g = build_qom_metro_graph()
    res = bfs_connectivity(g, "Terminal Mosaferbari Qom", "Masjed Moghaddas Jamkaran")
    assert res.reachable is True
    assert res.path is not None
    assert res.path[0] == "Terminal Mosaferbari Qom"
    assert res.path[-1] == "Masjed Moghaddas Jamkaran"
    assert res.distance_hops > 0


def test_dfs_connectivity():
    g = build_qom_metro_graph()
    res = dfs_connectivity(g, "Pardisan", "Darvazeh Rey")
    assert res.reachable is True
    assert res.path is not None
    assert res.path[0] == "Pardisan"
    assert res.path[-1] == "Darvazeh Rey"


def test_unreachable_search():
    g = Graph(is_directed=True)
    g.add_station_by_name("A")
    g.add_station_by_name("B")
    # No edge connecting A and B
    res_bfs = bfs_connectivity(g, "A", "B")
    assert res_bfs.reachable is False
    assert res_bfs.path is None

    res_dfs = dfs_connectivity(g, "A", "B")
    assert res_dfs.reachable is False
    assert res_dfs.path is None
