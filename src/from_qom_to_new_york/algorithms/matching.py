"""Hopcroft-Karp algorithm for Maximum Cardinality Bipartite Matching.

Applied to Task T3.5 / Round 5: Optimal Metro Staff & Crew Shift Allocation.

Theoretical Complexity:
- Hopcroft-Karp: O(E * sqrt(V)) time, O(V + E) space.
Significantly outperforms the standard Ford-Fulkerson / augmenting path method O(V * E)
by finding a maximal set of shortest vertex-disjoint augmenting paths in each phase using BFS,
then augmenting along them using DFS.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class StaffMember:
    """Represents a metro employee requesting or qualified for specific station shifts."""

    staff_id: str
    name: str
    role: str  # e.g., 'Station Master', 'Train Driver', 'Security Chief', 'Maintenance Lead'
    qualified_stations: List[str]


@dataclass
class ShiftSlot:
    """Represents a required operational shift at a metro station."""

    shift_id: str
    station_name: str
    required_role: str
    time_window: str  # e.g., 'Morning (06:00-14:00)', 'Evening (14:00-22:00)'


@dataclass
class MatchingResult:
    """Encapsulates the output of Hopcroft-Karp bipartite matching.

    Attributes:
        matches: List of (StaffMember, ShiftSlot) matched pairs.
        total_matched: Number of successfully assigned shifts.
        unmatched_staff: List of staff members not assigned to a shift.
        unfilled_shifts: List of shifts that could not be staffed.
        coverage_ratio: Percentage of required shifts successfully filled.
    """

    matches: List[Tuple[StaffMember, ShiftSlot]]
    total_matched: int
    unmatched_staff: List[StaffMember]
    unfilled_shifts: List[ShiftSlot]
    coverage_ratio: float


class HopcroftKarp:
    """Hopcroft-Karp Maximum Bipartite Matching algorithm."""

    NIL = "NIL"
    INF = float("inf")

    def __init__(self, left_nodes: List[str], right_nodes: List[str], adj: Dict[str, List[str]]) -> None:
        self.left_nodes = left_nodes
        self.right_nodes = right_nodes
        self.adj = adj

        # pair_u stores the right node matched to left node u
        self.pair_u: Dict[str, str] = {u: self.NIL for u in self.left_nodes}
        # pair_v stores the left node matched to right node v
        self.pair_v: Dict[str, str] = {v: self.NIL for v in self.right_nodes}
        # dist stores distance of left nodes from free nodes in BFS
        self.dist: Dict[str, float] = {}

    def _bfs(self) -> bool:
        """Find the length of the shortest augmenting path using BFS."""
        queue: deque[str] = deque()

        for u in self.left_nodes:
            if self.pair_u[u] == self.NIL:
                self.dist[u] = 0.0
                queue.append(u)
            else:
                self.dist[u] = self.INF

        self.dist[self.NIL] = self.INF

        while queue:
            u = queue.popleft()

            if self.dist[u] < self.dist[self.NIL]:
                for v in self.adj.get(u, []):
                    matched_u = self.pair_v.get(v, self.NIL)
                    if self.dist.get(matched_u, self.INF) == self.INF:
                        self.dist[matched_u] = self.dist[u] + 1.0
                        queue.append(matched_u)

        return self.dist[self.NIL] != self.INF

    def _dfs(self, u: str) -> bool:
        """Augment paths along vertex-disjoint shortest paths using DFS."""
        if u != self.NIL:
            for v in self.adj.get(u, []):
                matched_u = self.pair_v.get(v, self.NIL)
                if self.dist.get(matched_u, self.INF) == self.dist[u] + 1.0:
                    if self._dfs(matched_u):
                        self.pair_v[v] = u
                        self.pair_u[u] = v
                        return True
            self.dist[u] = self.INF
            return False
        return True

    def compute_maximum_matching(self) -> Dict[str, str]:
        """Execute Hopcroft-Karp algorithm and return mapping {left_node: right_node}."""
        while self._bfs():
            for u in self.left_nodes:
                if self.pair_u[u] == self.NIL:
                    self._dfs(u)

        return {u: v for u, v in self.pair_u.items() if v != self.NIL}


def match_staff_to_shifts(
    staff_list: List[StaffMember],
    shift_list: List[ShiftSlot],
) -> MatchingResult:
    """Solve the Staff-to-Shift Assignment problem (Task T3.5 / Round 5) via Hopcroft-Karp.

    Constructs a bipartite graph G = (L union R, E) where:
    - Left partition L = Staff Members
    - Right partition R = Shift Slots
    - Edge (u, v) exists iff staff u matches shift v's required role and qualified station.

    Complexity:
        Time: O(E * sqrt(V)).
        Space: O(V + E).
    """
    staff_map = {s.staff_id: s for s in staff_list}
    shift_map = {sh.shift_id: sh for sh in shift_list}

    left_ids = [s.staff_id for s in staff_list]
    right_ids = [sh.shift_id for sh in shift_list]

    # Build bipartite adjacency
    adj: Dict[str, List[str]] = {s_id: [] for s_id in left_ids}

    for staff in staff_list:
        for shift in shift_list:
            if staff.role == shift.required_role and shift.station_name in staff.qualified_stations:
                adj[staff.staff_id].append(shift.shift_id)

    solver = HopcroftKarp(left_ids, right_ids, adj)
    matching_dict = solver.compute_maximum_matching()

    matched_pairs: List[Tuple[StaffMember, ShiftSlot]] = []
    matched_staff_ids = set()
    matched_shift_ids = set()

    for s_id, sh_id in matching_dict.items():
        matched_pairs.append((staff_map[s_id], shift_map[sh_id]))
        matched_staff_ids.add(s_id)
        matched_shift_ids.add(sh_id)

    unmatched_staff = [s for s in staff_list if s.staff_id not in matched_staff_ids]
    unfilled_shifts = [sh for sh in shift_list if sh.shift_id not in matched_shift_ids]

    total_shifts = len(shift_list)
    cov_ratio = (len(matched_pairs) / total_shifts * 100.0) if total_shifts > 0 else 100.0

    return MatchingResult(
        matches=matched_pairs,
        total_matched=len(matched_pairs),
        unmatched_staff=unmatched_staff,
        unfilled_shifts=unfilled_shifts,
        coverage_ratio=round(cov_ratio, 2),
    )
