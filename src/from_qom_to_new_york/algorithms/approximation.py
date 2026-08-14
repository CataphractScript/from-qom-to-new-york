"""Emergency Response Team Placement (Dominating Set / Set Cover Approximation).

Formal Formulation & NP-Hardness Proof:
----------------------------------------
Problem Statement (Minimum Dominating Set):
Given an undirected transit graph G = (V, E), select a minimum cardinality subset S subseteq V
such that every vertex v in V is either in S or adjacent to at least one vertex u in S.
That is, the closed neighborhood N[S] = Union_{u in S} ({u} union Adj(u)) = V.

NP-Hardness Reduction:
1. Dominating Set is in NP because checking whether a given subset S of size <= k covers all V
   takes polynomial time O(V + E).
2. We reduce the known NP-complete VERTEX COVER problem to DOMINATING SET:
   Given graph G = (V, E), construct G' by:
   - Keeping all vertices V.
   - For every edge e = (u, v) in E, add a new vertex w_e and edges (u, w_e) and (v, w_e).
   - Add isolated pendants if needed.
   A vertex cover of size k in G exists if and only if G' has a dominating set of size k.
   Because Vertex Cover is NP-complete (Karp, 1972), Dominating Set is NP-complete,
   and its optimization version is NP-hard.

Approximation Ratio Analysis:
By formulating Dominating Set as Set Cover (universe = V, subsets = {N[u] for u in V}),
the standard greedy algorithm achieves an approximation guarantee of:
    alpha = H(Delta + 1) = sum_{i=1}^{Delta + 1} 1/i <= ln(Delta + 1) + 1
where Delta is the maximum degree of the graph.
For the Qom Metro network, Delta = 5, giving H(6) = 1 + 1/2 + 1/3 + 1/4 + 1/5 + 1/6 ~= 2.45.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from from_qom_to_new_york.core.graph import Graph


@dataclass
class DominatingSetResult:
    """Result of emergency response team placement.

    Attributes:
        chosen_stations: Selected stations where emergency teams are stationed (S).
        team_count: Number of emergency teams deployed (|S|).
        coverage_map: Dictionary mapping each station in network to the deployed team covering it.
        is_valid_dominating_set: True if every station in the network is covered.
        is_exact_optimal: True if found via exact branch & bound, False if greedy approximation.
        theoretical_approx_ratio: Upper bound on approximation ratio H(Delta + 1).
        max_degree: Maximum degree Delta in the graph.
    """

    chosen_stations: List[str]
    team_count: int
    coverage_map: Dict[str, str]
    is_valid_dominating_set: bool
    is_exact_optimal: bool
    theoretical_approx_ratio: float
    max_degree: int


def greedy_dominating_set(graph: Graph) -> DominatingSetResult:
    """Compute an approximate Minimum Dominating Set using the Greedy Set Cover heuristic.

    Greedy Strategy:
    In each step, select the station u whose closed neighborhood N[u] covers the largest number
    of currently uncovered stations.

    Approximation Ratio:
        H(Delta + 1) <= ln(Delta + 1) + 1 where Delta is max vertex degree.

    Complexity:
        Time: O(V * (V + E)).
        Space: O(V).
    """
    stations = graph.get_station_names()
    uncovered: Set[str] = set(stations)
    chosen: List[str] = []
    coverage_map: Dict[str, str] = {}

    # Precompute closed neighborhood N[u] = {u} union Adj(u) for each station
    neighborhoods: Dict[str, Set[str]] = {}
    max_deg = 0
    for st in stations:
        nbrs = set(graph.get_neighbors(st))
        nbrs.add(st)
        neighborhoods[st] = nbrs
        max_deg = max(max_deg, len(nbrs) - 1)

    while uncovered:
        # Pick candidate station with maximum uncovered overlap
        best_candidate: Optional[str] = None
        best_gain = -1
        best_covered_set: Set[str] = set()

        for candidate in stations:
            newly_covered = neighborhoods[candidate].intersection(uncovered)
            if len(newly_covered) > best_gain:
                best_gain = len(newly_covered)
                best_candidate = candidate
                best_covered_set = newly_covered

        if best_candidate is None or best_gain <= 0:
            break

        chosen.append(best_candidate)
        for st in best_covered_set:
            if st not in coverage_map:
                coverage_map[st] = best_candidate
        uncovered.difference_update(best_covered_set)

    harmonic_ratio = sum(1.0 / i for i in range(1, max_deg + 2))

    return DominatingSetResult(
        chosen_stations=chosen,
        team_count=len(chosen),
        coverage_map=coverage_map,
        is_valid_dominating_set=(len(coverage_map) == len(stations)),
        is_exact_optimal=False,
        theoretical_approx_ratio=round(harmonic_ratio, 3),
        max_degree=max_deg,
    )


def exact_minimum_dominating_set(graph: Graph) -> DominatingSetResult:
    """Compute the EXACT Minimum Dominating Set using recursive bitmask branch-and-bound.

    Used to evaluate the exact optimality gap of the polynomial-time greedy heuristic.

    Complexity:
        Worst-case Time: O(2^V) - extremely fast for V <= 25 (executes in milliseconds for V=20).
    """
    stations = graph.get_station_names()
    n = len(stations)
    st_to_idx = {st: i for i, st in enumerate(stations)}
    idx_to_st = {i: st for i, st in enumerate(stations)}

    # Bitmask closed neighborhoods
    masks: List[int] = [0] * n
    max_deg = 0
    for i, st in enumerate(stations):
        mask = 1 << i
        deg = 0
        for nbr in graph.get_neighbors(st):
            mask |= (1 << st_to_idx[nbr])
            deg += 1
        masks[i] = mask
        max_deg = max(max_deg, deg)

    target_mask = (1 << n) - 1
    best_size = n + 1
    best_subset: List[int] = list(range(n))

    def _search(curr_idx: int, current_mask: int, chosen_indices: List[int]) -> None:
        nonlocal best_size, best_subset

        if len(chosen_indices) >= best_size:
            return  # Prune branch

        if current_mask == target_mask:
            if len(chosen_indices) < best_size:
                best_size = len(chosen_indices)
                best_subset = list(chosen_indices)
            return

        if curr_idx >= n:
            return

        # Prune if remaining vertices cannot possibly cover uncovered elements
        remaining_cover = current_mask
        for j in range(curr_idx, n):
            remaining_cover |= masks[j]
        if (remaining_cover & target_mask) != target_mask:
            return

        # Branch 1: Include curr_idx
        chosen_indices.append(curr_idx)
        _search(curr_idx + 1, current_mask | masks[curr_idx], chosen_indices)
        chosen_indices.pop()

        # Branch 2: Exclude curr_idx
        _search(curr_idx + 1, current_mask, chosen_indices)

    _search(0, 0, [])

    chosen_stations = [idx_to_st[i] for i in best_subset]

    # Build coverage map
    coverage_map: Dict[str, str] = {}
    for team_st in chosen_stations:
        coverage_map[team_st] = team_st
        for nbr in graph.get_neighbors(team_st):
            if nbr not in coverage_map:
                coverage_map[nbr] = team_st

    harmonic_ratio = sum(1.0 / i for i in range(1, max_deg + 2))

    return DominatingSetResult(
        chosen_stations=chosen_stations,
        team_count=len(chosen_stations),
        coverage_map=coverage_map,
        is_valid_dominating_set=(len(coverage_map) == n),
        is_exact_optimal=True,
        theoretical_approx_ratio=round(harmonic_ratio, 3),
        max_degree=max_deg,
    )
