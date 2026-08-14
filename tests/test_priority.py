"""Unit tests for Train Dispatch Priority Queue (Min-Heap)."""

import pytest

from from_qom_to_new_york.algorithms.priority import Train, TrainPriorityQueue


def test_priority_queue_ordering():
    pq = TrainPriorityQueue()
    assert pq.is_empty() is True

    # Normal train with 5 min delay
    t1 = Train("T1", delay_minutes=5.0, emergency_level=0, passenger_count=100)
    # Train with critical emergency
    t2 = Train("T2", delay_minutes=1.0, emergency_level=3, passenger_count=50)
    # Train with huge delay
    t3 = Train("T3", delay_minutes=45.0, emergency_level=0, passenger_count=500)

    pq.push(t1)
    pq.push(t2)
    pq.push(t3)

    assert len(pq) == 3

    # Emergency train T2 should be dispatched first
    first = pq.pop_highest_priority()
    assert first.train_id == "T2"

    # Next should be high delay train T3
    second = pq.pop_highest_priority()
    assert second.train_id == "T3"

    # Finally t1
    third = pq.pop_highest_priority()
    assert third.train_id == "T1"

    assert pq.is_empty() is True


def test_priority_update():
    pq = TrainPriorityQueue()
    t1 = Train("T1", delay_minutes=2.0, emergency_level=0)
    t2 = Train("T2", delay_minutes=5.0, emergency_level=0)

    pq.push(t1)
    pq.push(t2)

    # Initially T2 is higher priority than T1
    assert pq.peek().train_id == "T2"

    # Elevate T1 to medical emergency
    pq.update_priority("T1", emergency_level=3)
    assert pq.peek().train_id == "T1"
