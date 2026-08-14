"""Metro Operations, Train Dispatch, Platform Scheduling, Staff Allocation, and Simulation Service."""

from __future__ import annotations

from typing import Dict, List, Optional

from from_qom_to_new_york.algorithms.analytics import (
    AnalyticsSummary,
    compute_operational_analytics,
)
from from_qom_to_new_york.algorithms.matching import (
    MatchingResult,
    ShiftSlot,
    StaffMember,
    match_staff_to_shifts,
)
from from_qom_to_new_york.algorithms.priority import Train, TrainPriorityQueue
from from_qom_to_new_york.algorithms.scheduling import (
    SchedulingResult,
    TrainSlot,
    interval_scheduling_greedy,
    weighted_interval_scheduling_dp,
)
from from_qom_to_new_york.algorithms.simulation import (
    PassengerArrivalSimulator,
    StationSimulationMetrics,
    SystemSimulationReport,
)
from from_qom_to_new_york.core.graph import Graph


class OperationsService:
    """Manages daily transit operations, dispatch queues, scheduling, staff shifts, and traffic simulations."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._dispatch_queue = TrainPriorityQueue()
        self._simulator = PassengerArrivalSimulator()

    # --- T3.1: Platform Interval Scheduling ---
    def schedule_platform_trains(
        self,
        train_requests: List[TrainSlot],
        weighted: bool = False,
    ) -> SchedulingResult:
        """Allocate maximum number of non-overlapping trains to a shared platform."""
        if weighted:
            return weighted_interval_scheduling_dp(train_requests)
        return interval_scheduling_greedy(train_requests)

    def generate_sample_platform_requests(self) -> List[TrainSlot]:
        """Generate realistic train occupancy requests for platform scheduling demonstration."""
        return [
            TrainSlot("TR-101", 6.0, 6.3, platform_id="Platform-1", line="Line-1 North", weight=120.0),
            TrainSlot("TR-102", 6.2, 6.5, platform_id="Platform-1", line="Line-1 Express", weight=200.0),
            TrainSlot("TR-103", 6.4, 6.7, platform_id="Platform-1", line="Line-1 Local", weight=90.0),
            TrainSlot("TR-104", 6.6, 7.0, platform_id="Platform-1", line="Line-1 South", weight=150.0),
            TrainSlot("TR-105", 6.8, 7.2, platform_id="Platform-1", line="Line-1 Special", weight=110.0),
            TrainSlot("TR-106", 7.1, 7.4, platform_id="Platform-1", line="Line-1 Local", weight=95.0),
            TrainSlot("TR-107", 7.3, 7.6, platform_id="Platform-1", line="Line-1 Express", weight=210.0),
            TrainSlot("TR-108", 7.5, 7.8, platform_id="Platform-1", line="Line-1 North", weight=130.0),
            TrainSlot("TR-109", 7.7, 8.1, platform_id="Platform-1", line="Line-1 South", weight=160.0),
            TrainSlot("TR-110", 8.0, 8.3, platform_id="Platform-1", line="Line-1 Local", weight=100.0),
        ]

    # --- T3.2: Train Dispatch Priority Queue ---
    def enqueue_train(self, train: Train) -> None:
        """Enqueue a train in the dispatch queue."""
        self._dispatch_queue.push(train)

    def dispatch_next_train(self) -> Train:
        """Dispatch the highest priority train."""
        return self._dispatch_queue.pop_highest_priority()

    def peek_next_train(self) -> Optional[Train]:
        """View the next train in queue."""
        return self._dispatch_queue.peek()

    def update_train_urgency(
        self,
        train_id: str,
        delay_minutes: Optional[float] = None,
        emergency_level: Optional[int] = None,
        passenger_count: Optional[int] = None,
    ) -> bool:
        """Update train status."""
        return self._dispatch_queue.update_priority(
            train_id=train_id,
            delay_minutes=delay_minutes,
            emergency_level=emergency_level,
            passenger_count=passenger_count,
        )

    def get_dispatch_queue_status(self) -> List[Train]:
        """Get all queued trains in priority order."""
        return self._dispatch_queue.get_all_ordered()

    def initialize_sample_dispatch_queue(self) -> None:
        """Populate dispatch queue with realistic metro trains."""
        sample_trains = [
            Train("TR-101", "Central Line", "Terminal Mosaferbari Qom", "Masjed Moghaddas Jamkaran", delay_minutes=2.0, emergency_level=0, passenger_count=450),
            Train("TR-204", "Express Line", "Qaleh Kamkar", "Pardisan", delay_minutes=15.0, emergency_level=0, passenger_count=820),
            Train("TR-911", "Emergency Service", "Meydan Motahari", "Bimarestan Nekouei", delay_minutes=0.0, emergency_level=3, passenger_count=10),
            Train("TR-305", "South Line", "Pardisan", "University of Qom", delay_minutes=8.5, emergency_level=1, passenger_count=600),
            Train("TR-108", "Central Line", "Haram Motahhar Hazrat Masoumeh", "Railway Station Qom", delay_minutes=1.0, emergency_level=0, passenger_count=350),
        ]
        for t in sample_trains:
            self.enqueue_train(t)

    # --- T3.3: Operational Analytics ---
    def get_operational_traffic_data(self) -> Dict[str, int]:
        """Generate realistic baseline daily passenger volume data for Qom stations."""
        return {
            "Haram Motahhar Hazrat Masoumeh": 85000,
            "Meydan Motahari": 78000,
            "Masjed Moghaddas Jamkaran": 65000,
            "Terminal Mosaferbari Qom": 54000,
            "Railway Station Qom": 48000,
            "Pardisan": 45000,
            "University of Qom": 38000,
            "Meydan Keshavarz": 32000,
            "Meydan Baghiatollah": 31000,
            "Niroogah": 29000,
            "Bimarestan Nekouei": 26000,
            "Qaleh Kamkar": 24000,
            "Darvazeh Rey": 22000,
            "Arg Salariyeh": 21000,
            "Bajek": 19000,
            "Boostan Fadak": 17000,
            "Boostan Jangali Ghadir": 16000,
            "Sadeqiyeh": 15000,
            "Chehel Derakht": 13000,
            "Amin Abad": 12000,
        }

    def analyze_operational_traffic(self, k_busiest: int = 1) -> AnalyticsSummary:
        """Calculate average daily trips and k-th most frequent station using Quickselect."""
        traffic = self.get_operational_traffic_data()
        return compute_operational_analytics(traffic, k_busiest=k_busiest)

    # --- T3.4: Passenger Simulation ---
    def run_passenger_simulation(
        self,
        duration_minutes: float = 60.0,
        peak_multiplier: float = 1.0,
    ) -> SystemSimulationReport:
        """Simulate random passenger arrivals and gate queues across all stations."""
        base_rates = {
            "Haram Motahhar Hazrat Masoumeh": 35.0 * peak_multiplier,
            "Meydan Motahari": 30.0 * peak_multiplier,
            "Masjed Moghaddas Jamkaran": 25.0 * peak_multiplier,
            "Terminal Mosaferbari Qom": 20.0 * peak_multiplier,
            "Railway Station Qom": 18.0 * peak_multiplier,
            "Pardisan": 16.0 * peak_multiplier,
            "University of Qom": 14.0 * peak_multiplier,
            "Meydan Keshavarz": 12.0 * peak_multiplier,
            "Niroogah": 10.0 * peak_multiplier,
            "Bimarestan Nekouei": 9.0 * peak_multiplier,
        }
        return self._simulator.simulate_network(base_rates, duration_minutes=duration_minutes)

    # --- T3.5 / Round 5: Staff Shift Bipartite Matching (Hopcroft-Karp) ---
    def allocate_staff_shifts(
        self,
        custom_staff: Optional[List[StaffMember]] = None,
        custom_shifts: Optional[List[ShiftSlot]] = None,
    ) -> MatchingResult:
        """Assign metro personnel to station shifts using the Hopcroft-Karp algorithm in O(E * sqrt(V))."""
        staff = custom_staff or self.generate_sample_staff()
        shifts = custom_shifts or self.generate_sample_shifts()
        return match_staff_to_shifts(staff, shifts)

    def generate_sample_staff(self) -> List[StaffMember]:
        """Generate realistic sample workforce for Qom Metro shift assignment."""
        return [
            StaffMember("EMP-01", "Ali Rezaei", "Station Master", ["Haram Motahhar Hazrat Masoumeh", "Meydan Motahari"]),
            StaffMember("EMP-02", "Hossein Moradi", "Station Master", ["Terminal Mosaferbari Qom", "Qaleh Kamkar"]),
            StaffMember("EMP-03", "Mehdi Kazemi", "Train Driver", ["Meydan Motahari", "Masjed Moghaddas Jamkaran"]),
            StaffMember("EMP-04", "Sadegh Ahmadi", "Train Driver", ["Terminal Mosaferbari Qom", "Pardisan"]),
            StaffMember("EMP-05", "Reza Hosseini", "Security Chief", ["Haram Motahhar Hazrat Masoumeh", "Railway Station Qom"]),
            StaffMember("EMP-06", "Mohammad Jafari", "Security Chief", ["Masjed Moghaddas Jamkaran", "Pardisan"]),
            StaffMember("EMP-07", "Hassan Taghavi", "Maintenance Lead", ["Niroogah", "Meydan Motahari"]),
            StaffMember("EMP-08", "Vahid Ebrahimi", "Maintenance Lead", ["Qaleh Kamkar", "Bimarestan Nekouei"]),
        ]

    def generate_sample_shifts(self) -> List[ShiftSlot]:
        """Generate station shift requirements for Qom Metro daily operation."""
        return [
            ShiftSlot("SH-101", "Haram Motahhar Hazrat Masoumeh", "Station Master", "Morning (06:00-14:00)"),
            ShiftSlot("SH-102", "Terminal Mosaferbari Qom", "Station Master", "Morning (06:00-14:00)"),
            ShiftSlot("SH-103", "Meydan Motahari", "Train Driver", "Peak Morning (07:00-15:00)"),
            ShiftSlot("SH-104", "Pardisan", "Train Driver", "Peak Morning (07:00-15:00)"),
            ShiftSlot("SH-105", "Haram Motahhar Hazrat Masoumeh", "Security Chief", "All-Day (08:00-16:00)"),
            ShiftSlot("SH-106", "Masjed Moghaddas Jamkaran", "Security Chief", "Evening (14:00-22:00)"),
            ShiftSlot("SH-107", "Niroogah", "Maintenance Lead", "Morning Inspection (06:00-14:00)"),
            ShiftSlot("SH-108", "Qaleh Kamkar", "Maintenance Lead", "Night Maintenance (22:00-06:00)"),
        ]
