"""String algorithms and typo-tolerant station name search using Levenshtein Distance.

Theoretical Complexity:
- Levenshtein Distance: O(M * N) time, O(min(M, N)) space using space-optimized dynamic programming.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


def levenshtein_distance(s1: str, s2: str, case_sensitive: bool = False) -> int:
    """Compute the Levenshtein (edit) distance between two strings using dynamic programming.

    The edit distance is the minimum number of single-character operations (insertions,
    deletions, or substitutions) required to transform s1 into s2.

    DP Formulation:
        D(i, j) = D(i-1, j-1) if s1[i-1] == s2[j-1]
        D(i, j) = 1 + min( D(i-1, j),   # deletion
                           D(i, j-1),   # insertion
                           D(i-1, j-1)  # substitution
                         )

    Space Optimization:
        Because row i only depends on row i-1, we use two rows, reducing space from O(M * N) to O(min(M, N)).

    Complexity:
        Time: O(M * N)
        Space: O(min(M, N))
    """
    if not case_sensitive:
        s1 = s1.lower()
        s2 = s2.lower()

    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    # Ensure s2 is the shorter string to minimize space
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    m, n = len(s1), len(s2)
    prev_row = list(range(n + 1))
    curr_row = [0] * (n + 1)

    for i in range(1, m + 1):
        curr_row[0] = i
        char1 = s1[i - 1]
        for j in range(1, n + 1):
            char2 = s2[j - 1]
            cost = 0 if char1 == char2 else 1
            curr_row[j] = min(
                prev_row[j] + 1,        # Deletion
                curr_row[j - 1] + 1,    # Insertion
                prev_row[j - 1] + cost  # Substitution
            )
        prev_row, curr_row = curr_row, prev_row

    return prev_row[n]


@dataclass
class FuzzyMatchResult:
    """Represents a fuzzy search candidate station match."""

    station_name: str
    edit_distance: int
    similarity_score: float  # Value between 0.0 (completely dissimilar) and 1.0 (exact match)

    def __repr__(self) -> str:
        return f"FuzzyMatch('{self.station_name}', dist={self.edit_distance}, sim={self.similarity_score*100:.1f}%)"


def fuzzy_search_stations(
    query: str,
    candidate_stations: List[str],
    top_k: int = 5,
    case_sensitive: bool = False,
) -> List[FuzzyMatchResult]:
    """Perform typo-tolerant fuzzy matching over station names.

    Calculates normalized similarity across full string as well as individual token words
    (e.g., 'motahary' matches 'Meydan Motahari' with high precision).

    Args:
        query: User input string (may contain typos).
        candidate_stations: List of valid station names.
        top_k: Maximum number of candidate matches to return.
        case_sensitive: Whether matching is case-sensitive.

    Returns:
        List of FuzzyMatchResult objects ordered from highest to lowest similarity.
    """
    if not query:
        return []

    q_clean = query if case_sensitive else query.lower().strip()
    results: List[FuzzyMatchResult] = []

    for name in candidate_stations:
        n_clean = name if case_sensitive else name.lower().strip()

        # 1. Full string distance
        full_dist = levenshtein_distance(q_clean, n_clean, case_sensitive=True)
        max_full_len = max(len(q_clean), len(n_clean))
        full_sim = 1.0 - (full_dist / max_full_len) if max_full_len > 0 else 1.0

        best_dist = full_dist
        best_sim = full_sim

        # 2. Token-level matching (check each word in multi-word station names)
        tokens = n_clean.split()
        for token in tokens:
            t_dist = levenshtein_distance(q_clean, token, case_sensitive=True)
            max_t_len = max(len(q_clean), len(token))
            t_sim = 1.0 - (t_dist / max_t_len) if max_t_len > 0 else 1.0
            if t_sim > best_sim:
                best_sim = t_sim
                best_dist = t_dist

        # 3. Substring boost
        if q_clean in n_clean:
            best_sim = max(best_sim, 0.90)
            best_dist = min(best_dist, len(n_clean) - len(q_clean))

        sim_score = max(0.0, min(1.0, best_sim))
        results.append(
            FuzzyMatchResult(
                station_name=name,
                edit_distance=best_dist,
                similarity_score=round(sim_score, 4),
            )
        )

    # Sort primarily by highest similarity, secondarily by smallest edit distance
    results.sort(key=lambda r: (-r.similarity_score, r.edit_distance, r.station_name))
    return results[:top_k]
