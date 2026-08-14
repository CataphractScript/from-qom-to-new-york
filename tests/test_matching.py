"""Unit tests for Hopcroft-Karp Bipartite Matching (T3.5 Staff Shift Allocation)."""

import pytest

from from_qom_to_new_york.algorithms.matching import (
    HopcroftKarp,
    ShiftSlot,
    StaffMember,
    match_staff_to_shifts,
)


def test_hopcroft_karp_basic_matching():
    # Simple bipartite graph:
    # L = {u1, u2, u3}, R = {v1, v2, v3}
    # u1 -> v1, v2
    # u2 -> v1
    # u3 -> v2
    left = ["u1", "u2", "u3"]
    right = ["v1", "v2", "v3"]
    adj = {
        "u1": ["v1", "v2"],
        "u2": ["v1"],
        "u3": ["v2"],
    }

    hk = HopcroftKarp(left, right, adj)
    matching = hk.compute_maximum_matching()

    # Max matching size is 2 (since v1 and v2 are shared between 3 left nodes)
    assert len(matching) == 2


def test_metro_staff_shift_allocation():
    staff = [
        StaffMember("S1", "Ali", "Station Master", ["Haram Motahhar Hazrat Masoumeh", "Meydan Motahari"]),
        StaffMember("S2", "Reza", "Train Driver", ["Meydan Motahari", "Pardisan"]),
        StaffMember("S3", "Mehdi", "Security Chief", ["Haram Motahhar Hazrat Masoumeh"]),
    ]

    shifts = [
        ShiftSlot("SH1", "Haram Motahhar Hazrat Masoumeh", "Station Master", "Morning"),
        ShiftSlot("SH2", "Pardisan", "Train Driver", "Morning"),
        ShiftSlot("SH3", "Haram Motahhar Hazrat Masoumeh", "Security Chief", "Evening"),
    ]

    res = match_staff_to_shifts(staff, shifts)

    assert res.total_matched == 3
    assert len(res.unmatched_staff) == 0
    assert len(res.unfilled_shifts) == 0
    assert res.coverage_ratio == 100.0
