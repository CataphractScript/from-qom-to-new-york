"""Unit tests for Emergency Team Placement (Dominating Set Approximation)."""

import pytest

from from_qom_to_new_york.algorithms.approximation import (
    exact_minimum_dominating_set,
    greedy_dominating_set,
)
from from_qom_to_new_york.core.data import build_qom_metro_graph


def test_dominating_set_coverage_validity():
    g = build_qom_metro_graph()

    # Test greedy approximation
    greedy_res = greedy_dominating_set(g)
    assert greedy_res.is_valid_dominating_set is True
    assert greedy_res.team_count > 0
    assert len(greedy_res.coverage_map) == 20  # All 20 stations covered

    # Test exact solver
    exact_res = exact_minimum_dominating_set(g)
    assert exact_res.is_valid_dominating_set is True
    assert exact_res.is_exact_optimal is True
    assert exact_res.team_count <= greedy_res.team_count

    # Greedy approximation cannot exceed theoretical bound
    assert greedy_res.team_count <= greedy_res.theoretical_approx_ratio * exact_res.team_count
