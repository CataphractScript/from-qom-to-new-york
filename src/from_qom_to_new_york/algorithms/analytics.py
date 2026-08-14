"""Operational transit analytics and selection algorithms (Quickselect, Rank Statistics).

Theoretical Complexity:
- Quickselect: Expected O(N) time, O(1) auxiliary space.
  Worst-case O(N^2) avoided by randomized pivot selection or median-of-three.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, TypeVar

T = TypeVar("T")


def quickselect(arr: List[T], k: int, key: Optional[Callable[[T], float]] = None) -> T:
    """Find the k-th smallest element in an unordered list in expected linear O(N) time.

    Args:
        arr: Non-empty list of elements.
        k: 0-indexed rank (0 is smallest, len(arr)-1 is largest).
        key: Optional feature extractor.

    Returns:
        The element with rank k.

    Complexity:
        Expected Time: O(N).
        Worst-case Time: O(N^2).
        Space: O(N) for working partition copies (or O(1) in-place).
    """
    if not 0 <= k < len(arr):
        raise IndexError(f"Rank index k={k} out of bounds for array of size {len(arr)}.")

    val_fn = key if key is not None else (lambda x: float(x))  # type: ignore

    def _select(sub_arr: List[T], target_k: int) -> T:
        if len(sub_arr) == 1:
            return sub_arr[0]

        pivot = random.choice(sub_arr)
        pivot_val = val_fn(pivot)

        lows = [x for x in sub_arr if val_fn(x) < pivot_val]
        highs = [x for x in sub_arr if val_fn(x) > pivot_val]
        pivots = [x for x in sub_arr if val_fn(x) == pivot_val]

        if target_k < len(lows):
            return _select(lows, target_k)
        elif target_k < len(lows) + len(pivots):
            return pivots[0]
        else:
            return _select(highs, target_k - len(lows) - len(pivots))

    return _select(list(arr), k)


@dataclass
class StationTrafficRecord:
    """Daily passenger traffic metrics for a station."""

    station_name: str
    daily_boardings: int
    daily_alightings: int
    transit_transfers: int
    total_trips: int


@dataclass
class AnalyticsSummary:
    """Consolidated operational report for network traffic and ridership.

    Attributes:
        average_daily_trips: Network-wide average daily passenger trips per station.
        total_system_trips: Total trips served daily across all stations.
        busiest_station: Station with highest traffic volume.
        kth_busiest_station: The k-th busiest station queried.
        k_rank: The requested k rank.
        station_rankings: Full ranked list of stations from highest to lowest traffic.
        standard_deviation: Standard deviation of passenger volumes.
    """

    average_daily_trips: float
    total_system_trips: int
    busiest_station: str
    kth_busiest_station: str
    k_rank: int
    station_rankings: List[Tuple[str, int]]
    standard_deviation: float


def compute_operational_analytics(
    traffic_data: Dict[str, int],
    k_busiest: int = 1,
) -> AnalyticsSummary:
    """Compute ridership analytics, including average daily trips and k-th most frequent station.

    Uses Quickselect to identify the k-th busiest station in expected O(N) time.

    Args:
        traffic_data: Dictionary mapping station names to daily passenger trip counts.
        k_busiest: 1-indexed rank for busiest station (1 = 1st busiest, 2 = 2nd busiest, etc.).

    Returns:
        AnalyticsSummary with statistical indicators.
    """
    if not traffic_data:
        raise ValueError("Traffic data cannot be empty.")

    items = list(traffic_data.items())  # List of (station_name, trip_count)
    n = len(items)

    if not 1 <= k_busiest <= n:
        raise ValueError(f"k_busiest must be between 1 and {n}, got {k_busiest}.")

    # k-th busiest means (n - k_busiest)-th smallest
    target_index = n - k_busiest
    kth_item = quickselect(items, k=target_index, key=lambda item: float(item[1]))

    total_trips = sum(v for _, v in items)
    avg_trips = total_trips / float(n)

    # Standard deviation
    variance = sum((v - avg_trips) ** 2 for _, v in items) / float(n)
    std_dev = math.sqrt(variance)

    # Sorted rankings
    rankings = sorted(items, key=lambda x: x[1], reverse=True)
    busiest = rankings[0][0]

    return AnalyticsSummary(
        average_daily_trips=round(avg_trips, 2),
        total_system_trips=total_trips,
        busiest_station=busiest,
        kth_busiest_station=kth_item[0],
        k_rank=k_busiest,
        station_rankings=rankings,
        standard_deviation=round(std_dev, 2),
    )
