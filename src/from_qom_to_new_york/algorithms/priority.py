"""Train dispatch management using an optimized Min-Heap Priority Queue.

Theoretical Complexity:
- Push (Insert train): O(log N) time.
- Pop (Dispatch highest priority train): O(log N) time.
- Peek: O(1) time.
- Update Priority (Decrease-Key / Re-heapify): O(N) worst-case with indexed mapping, O(log N) amortized.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Train:
    """Represents a train awaiting dispatch in the depot/station queue.

    Attributes:
        train_id: Unique train code (e.g. 'EXP-901').
        line_name: Metro line code or route.
        origin: Starting station.
        destination: Destination terminal station.
        delay_minutes: Cumulative delay behind schedule in minutes.
        emergency_level: Severity level (0 = Normal, 1 = Elevated, 2 = Urgent, 3 = Critical Emergency).
        passenger_count: Number of onboard passengers.
        scheduled_departure: Scheduled departure minute.
    """

    train_id: str
    line_name: str = "Line 1"
    origin: str = "Terminal Mosaferbari Qom"
    destination: str = "Masjed Moghaddas Jamkaran"
    delay_minutes: float = 0.0
    emergency_level: int = 0
    passenger_count: int = 0
    scheduled_departure: float = 0.0

    @property
    def urgency_score(self) -> float:
        """Calculate composite dispatch priority score (higher score = more urgent).

        Formula:
            urgency = (emergency_level * 1000.0) + (delay_minutes * 10.0) + (passenger_count * 0.05)
        """
        return (
            (float(self.emergency_level) * 1000.0)
            + (max(0.0, self.delay_minutes) * 10.0)
            + (float(self.passenger_count) * 0.05)
        )

    def __repr__(self) -> str:
        return (
            f"Train({self.train_id}, line='{self.line_name}', "
            f"delay={self.delay_minutes}min, emg={self.emergency_level}, "
            f"passengers={self.passenger_count}, score={self.urgency_score:.1f})"
        )


class TrainPriorityQueue:
    """Priority queue for train dispatch scheduling backed by a binary heap."""

    def __init__(self) -> None:
        # Heap elements: (-urgency_score, entry_index, train_id)
        self._heap: List[Tuple[float, int, str]] = []
        self._train_map: Dict[str, Train] = {}
        self._entry_counter: int = 0

    def push(self, train: Train) -> None:
        """Enqueue a train for dispatch.

        Complexity: O(log N)
        """
        self._train_map[train.train_id] = train
        self._entry_counter += 1
        # Store negative urgency score so maximum urgency appears at root of min-heap
        heapq.heappush(self._heap, (-train.urgency_score, self._entry_counter, train.train_id))

    def pop_highest_priority(self) -> Train:
        """Dispatch and remove the train with the highest urgency score.

        Complexity: O(log N)
        """
        while self._heap:
            neg_score, _, train_id = heapq.heappop(self._heap)
            if train_id in self._train_map:
                train = self._train_map.pop(train_id)
                return train
        raise IndexError("Cannot pop from an empty TrainPriorityQueue.")

    def peek(self) -> Optional[Train]:
        """Inspect the next train to be dispatched without removing it.

        Complexity: O(1)
        """
        while self._heap:
            _, _, train_id = self._heap[0]
            if train_id in self._train_map:
                return self._train_map[train_id]
            heapq.heappop(self._heap)
        return None

    def update_priority(
        self,
        train_id: str,
        delay_minutes: Optional[float] = None,
        emergency_level: Optional[int] = None,
        passenger_count: Optional[int] = None,
    ) -> bool:
        """Update operational parameters of an active queued train and re-heapify.

        Args:
            train_id: ID of train to modify.
            delay_minutes: New delay in minutes.
            emergency_level: New emergency severity.
            passenger_count: New passenger count.

        Returns:
            True if train was found and updated, False otherwise.
        """
        if train_id not in self._train_map:
            return False

        train = self._train_map[train_id]
        if delay_minutes is not None:
            train.delay_minutes = delay_minutes
        if emergency_level is not None:
            train.emergency_level = emergency_level
        if passenger_count is not None:
            train.passenger_count = passenger_count

        # Rebuild heap entries
        self.push(train)
        return True

    def remove(self, train_id: str) -> bool:
        """Remove a train from the dispatch queue."""
        if train_id in self._train_map:
            del self._train_map[train_id]
            return True
        return False

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._train_map) == 0

    def __len__(self) -> int:
        return len(self._train_map)

    def get_all_ordered(self) -> List[Train]:
        """Return a sorted snapshot of all pending trains in descending order of priority."""
        return sorted(self._train_map.values(), key=lambda t: t.urgency_score, reverse=True)
