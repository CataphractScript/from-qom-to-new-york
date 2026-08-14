"""Unit tests for Levenshtein Distance and Fuzzy Search."""

import pytest

from from_qom_to_new_york.algorithms.string import fuzzy_search_stations, levenshtein_distance


def test_levenshtein_distance_cases():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("metro", "metro") == 0
    assert levenshtein_distance("", "hello") == 5
    assert levenshtein_distance("abc", "") == 3
    assert levenshtein_distance("motahary", "motahari") == 1


def test_fuzzy_search_ranking():
    stations = [
        "Meydan Motahari",
        "Meydan Keshavarz",
        "Masjed Moghaddas Jamkaran",
        "Pardisan",
        "Haram Motahhar Hazrat Masoumeh",
    ]

    # Searching with typos
    matches = fuzzy_search_stations("motahary", stations, top_k=3)
    assert len(matches) > 0
    assert matches[0].station_name == "Meydan Motahari"
    assert matches[0].similarity_score > 0.8

    matches_jamk = fuzzy_search_stations("jamkaran", stations, top_k=3)
    assert matches_jamk[0].station_name == "Masjed Moghaddas Jamkaran"
