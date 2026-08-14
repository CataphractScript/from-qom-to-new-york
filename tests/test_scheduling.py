"""Unit tests for Platform Interval Scheduling (Greedy EFT & Weighted DP)."""

import pytest

from from_qom_to_new_york.algorithms.scheduling import (
    TrainSlot,
    interval_scheduling_greedy,
    weighted_interval_scheduling_dp,
)


def test_greedy_interval_scheduling_non_overlapping():
    trains = [
        TrainSlot("T1", 1.0, 3.0),
        TrainSlot("T2", 2.0, 5.0),
        TrainSlot("T3", 4.0, 7.0),
        TrainSlot("T4", 6.0, 9.0),
        TrainSlot("T5", 8.0, 10.0),
    ]

    res = interval_scheduling_greedy(trains)
    # Optimal subset: T1 [1-3], T3 [4-7], T5 [8-10] => 3 trains
    assert res.total_trains == 3
    selected_ids = [t.train_id for t in res.selected_trains]
    assert selected_ids == ["T1", "T3", "T5"]

    # Verify no selected trains overlap
    for i in range(len(res.selected_trains) - 1):
        assert res.selected_trains[i].end_time <= res.selected_trains[i + 1].start_time


def test_weighted_interval_scheduling():
    trains = [
        TrainSlot("T1", 1.0, 4.0, weight=10.0),
        TrainSlot("T2", 2.0, 6.0, weight=100.0),  # Higher weight
        TrainSlot("T3", 5.0, 8.0, weight=10.0),
    ]

    res = weighted_interval_scheduling_dp(trains)
    # T2 alone gives weight 100 > T1+T3 (weight 20)
    assert res.total_weight == 100.0
    assert len(res.selected_trains) == 1
    assert res.selected_trains[0].train_id == "T2"
