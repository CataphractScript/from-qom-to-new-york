"""Platform Interval Scheduling algorithms (Greedy Unweighted & DP Weighted).

Theoretical Complexity:
- Greedy Earliest Finish Time (EFT): O(n log n) time, O(n) space.
  Proven mathematically optimal for unweighted interval scheduling via the "Greedy Stays Ahead" proof technique.
- Weighted Interval Scheduling (DP + Binary Search): O(n log n) time, O(n) space.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class TrainSlot:
    """Represents a scheduled train occupying a platform.

    Attributes:
        train_id: Unique train identifier (e.g. 'TR-101').
        start_time: Platform arrival / occupancy start time (minutes or float timestamp).
        end_time: Platform departure time (minutes or float timestamp).
        platform_id: Platform identifier (e.g. 'Platform-1').
        line: Line name or route.
        weight: Importance / passenger capacity / revenue value (for weighted scheduling).
    """

    train_id: str
    start_time: float
    end_time: float
    platform_id: str = "Platform-1"
    line: str = "Central Line"
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.start_time >= self.end_time:
            raise ValueError(
                f"Invalid time interval for {self.train_id}: start_time ({self.start_time}) "
                f"must be strictly less than end_time ({self.end_time})."
            )

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    def overlaps_with(self, other: TrainSlot) -> bool:
        """Check if two train slots overlap in time."""
        return max(self.start_time, other.start_time) < min(self.end_time, other.end_time)

    def __hash__(self) -> int:
        return hash((self.train_id, self.start_time, self.end_time))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrainSlot):
            return False
        return (
            self.train_id == other.train_id
            and abs(self.start_time - other.start_time) < 1e-9
            and abs(self.end_time - other.end_time) < 1e-9
        )

    def __repr__(self) -> str:
        return f"TrainSlot({self.train_id}, [{self.start_time:.1f} - {self.end_time:.1f}], weight={self.weight})"


@dataclass
class SchedulingResult:
    """Encapsulates the optimal platform train allocation result.

    Attributes:
        selected_trains: List of non-overlapping TrainSlots chosen.
        total_trains: Count of scheduled trains.
        total_weight: Sum of weights (or total trains in unweighted mode).
        platform_utilization_ratio: Fraction of the active horizon during which the platform is occupied.
        rejected_trains: List of TrainSlots that could not be accommodated due to conflict.
    """

    selected_trains: List[TrainSlot]
    total_trains: int
    total_weight: float
    platform_utilization_ratio: float
    rejected_trains: List[TrainSlot]


def interval_scheduling_greedy(trains: List[TrainSlot]) -> SchedulingResult:
    """Select the maximum number of mutually compatible (non-overlapping) trains for a shared platform.

    Algorithmic Strategy:
    Earliest Finish Time First (Greedy).
    1. Sort all train requests in ascending order of their end time: f_1 <= f_2 <= ... <= f_n.
    2. Greedily pick the first train.
    3. For subsequent trains, accept if and only if start_time >= finish_time of the last accepted train.

    Proof of Optimality (Greedy Stays Ahead):
    Let G = {g_1, ..., g_k} be the greedy schedule and O = {o_1, ..., o_m} be an optimal schedule.
    By mathematical induction: f(g_r) <= f(o_r) for all r <= k.
    Hence, when the greedy algorithm finishes with k trains, no other schedule can pack more trains
    without violating non-overlap, proving k = m.

    Complexity:
        Time: O(n log n) dominated by sorting.
        Space: O(n) to store schedule.
    """
    if not trains:
        return SchedulingResult([], 0, 0.0, 0.0, [])

    # Sort strictly by earliest finish time
    sorted_trains = sorted(trains, key=lambda t: t.end_time)

    selected: List[TrainSlot] = []
    rejected: List[TrainSlot] = []
    last_finish = float("-inf")

    min_start = min(t.start_time for t in trains)
    max_end = max(t.end_time for t in trains)
    total_horizon = max_end - min_start if max_end > min_start else 1.0

    for train in sorted_trains:
        if train.start_time >= last_finish:
            selected.append(train)
            last_finish = train.end_time
        else:
            rejected.append(train)

    occupied_duration = sum(t.duration for t in selected)
    utilization = min(1.0, occupied_duration / total_horizon) if total_horizon > 0 else 0.0

    return SchedulingResult(
        selected_trains=selected,
        total_trains=len(selected),
        total_weight=float(len(selected)),
        platform_utilization_ratio=round(utilization, 4),
        rejected_trains=rejected,
    )


def weighted_interval_scheduling_dp(trains: List[TrainSlot]) -> SchedulingResult:
    """Compute the maximum-weight compatible subset of trains using Dynamic Programming and Binary Search.

    Recurrence Relation:
    Let OPT(j) be the maximum weight achievable considering trains 1..j sorted by finish time.
    OPT(j) = max( OPT(j-1), weight(j) + OPT(p(j)) )
    where p(j) is the largest index i < j such that train i does not conflict with train j (f_i <= s_j).

    Complexity:
        Time: O(n log n) - sorting takes O(n log n), and binary search for each p(j) takes O(log n).
        Space: O(n) for DP memoization and predecessor tracking.
    """
    if not trains:
        return SchedulingResult([], 0, 0.0, 0.0, [])

    sorted_trains = sorted(trains, key=lambda t: t.end_time)
    n = len(sorted_trains)
    finish_times = [t.end_time for t in sorted_trains]

    # p(j) precomputation via binary search
    p: List[int] = []
    for j in range(n):
        # Find rightmost interval that finishes <= sorted_trains[j].start_time
        idx = bisect.bisect_right(finish_times, sorted_trains[j].start_time) - 1
        p.append(idx)

    # DP table: dp[j] is optimal value using subset of first j intervals (1-indexed)
    dp: List[float] = [0.0] * (n + 1)
    for j in range(1, n + 1):
        incl = sorted_trains[j - 1].weight + (dp[p[j - 1] + 1] if p[j - 1] != -1 else 0.0)
        excl = dp[j - 1]
        dp[j] = max(incl, excl)

    # Backtracking to reconstruct selected items
    selected: List[TrainSlot] = []
    curr = n
    while curr > 0:
        incl = sorted_trains[curr - 1].weight + (dp[p[curr - 1] + 1] if p[curr - 1] != -1 else 0.0)
        if incl >= dp[curr - 1]:
            selected.append(sorted_trains[curr - 1])
            curr = p[curr - 1] + 1
        else:
            curr -= 1

    selected.reverse()
    selected_set = set(selected)
    rejected = [t for t in sorted_trains if t not in selected_set]

    min_start = min(t.start_time for t in trains)
    max_end = max(t.end_time for t in trains)
    total_horizon = max_end - min_start if max_end > min_start else 1.0
    occupied_duration = sum(t.duration for t in selected)
    utilization = min(1.0, occupied_duration / total_horizon) if total_horizon > 0 else 0.0

    return SchedulingResult(
        selected_trains=selected,
        total_trains=len(selected),
        total_weight=round(dp[n], 2),
        platform_utilization_ratio=round(utilization, 4),
        rejected_trains=rejected,
    )
