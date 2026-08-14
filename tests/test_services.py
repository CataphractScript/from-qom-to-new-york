"""Integration tests for Service layers and MetroSystem Facade."""

import pytest

from from_qom_to_new_york.services.metro_system import MetroSystem


def test_metro_system_facade_integration():
    system = MetroSystem.create_default()

    # Test Routing Service
    r_res = system.routing.find_shortest_path("Terminal Mosaferbari Qom", "Masjed Moghaddas Jamkaran")
    assert r_res.total_cost == 18.5

    # Test Infrastructure Service
    mst_res = system.infrastructure.design_minimum_cost_network("kruskal")
    assert mst_res.total_weight == 47.1

    # Test Operations Service
    analytics = system.operations.analyze_operational_traffic(k_busiest=3)
    assert analytics.total_system_trips > 0
    assert analytics.kth_busiest_station != ""

    # Test Analysis Service
    crit_res = system.analysis.identify_critical_infrastructure()
    assert len(crit_res.articulation_points) > 0
    assert len(crit_res.bridges) > 0

    fuzzy_res = system.analysis.search_station_fuzzy("motahari")
    assert len(fuzzy_res) > 0
    assert fuzzy_res[0].station_name == "Meydan Motahari"
