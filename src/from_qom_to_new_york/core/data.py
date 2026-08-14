"""Official transit network dataset for the Qom Metro project.

Extracted directly from technical specification document:
'From Qom to New York: Technical Case Study Track (UrbanPulse Dynamics)'
Page 6 (Vertices) and Page 7 (Edges).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from from_qom_to_new_york.core.graph import Graph
from from_qom_to_new_york.core.station import Coordinates, Station

# Canonical Station Metadata (ID, English Name, Coordinates, Flags, Facilities)
# Coordinates represent real-world locations in Qom to provide an admissible
# straight-line Euclidean/Haversine heuristic for A* pathfinding.
OFFICIAL_STATIONS: List[Station] = [
    Station(
        id=1,
        name="Qaleh Kamkar",
        coordinates=Coordinates(latitude=34.6850, longitude=50.8680),
        is_terminal=False,
        is_transfer=True,
        facilities=["Elevator", "Bus Interchange", "Ticket Office"],
    ),
    Station(
        id=2,
        name="Meydan Keshavarz",
        coordinates=Coordinates(latitude=34.6750, longitude=50.8600),
        is_terminal=False,
        is_transfer=False,
        facilities=["Elevator", "Escalator", "Ticket Machine"],
    ),
    Station(
        id=3,
        name="Meydan Motahari",
        coordinates=Coordinates(latitude=34.6465, longitude=50.8785),
        is_terminal=False,
        is_transfer=True,
        facilities=["Elevator", "Escalator", "Bus Terminal", "Commercial Arcade"],
    ),
    Station(
        id=4,
        name="Bimarestan Nekouei",
        coordinates=Coordinates(latitude=34.6340, longitude=50.8830),
        is_terminal=False,
        is_transfer=False,
        facilities=["Hospital Access", "Wheelchair Ramp", "Elevator"],
    ),
    Station(
        id=5,
        name="Meydan Baghiatollah",
        coordinates=Coordinates(latitude=34.6180, longitude=50.9010),
        is_terminal=False,
        is_transfer=True,
        facilities=["Elevator", "Taxi Stand", "Ticket Machine"],
    ),
    Station(
        id=6,
        name="Masjed Moghaddas Jamkaran",
        coordinates=Coordinates(latitude=34.5830, longitude=50.9250),
        is_terminal=True,
        is_transfer=False,
        facilities=["Large Terminal Hall", "Bus Interchange", "Prayer Hall", "Parking"],
    ),
    Station(
        id=7,
        name="Haram Motahhar Hazrat Masoumeh",
        coordinates=Coordinates(latitude=34.6416, longitude=50.8794),
        is_terminal=False,
        is_transfer=True,
        facilities=["Pilgrim Center", "Underground Concourse", "Information Desk", "Luggage Storage"],
    ),
    Station(
        id=8,
        name="Arg Salariyeh",
        coordinates=Coordinates(latitude=34.6220, longitude=50.8650),
        is_terminal=False,
        is_transfer=False,
        facilities=["Shopping Center Link", "Elevator", "Bicycle Racks"],
    ),
    Station(
        id=9,
        name="Darvazeh Rey",
        coordinates=Coordinates(latitude=34.6360, longitude=50.8920),
        is_terminal=False,
        is_transfer=False,
        facilities=["Elevator", "Ticket Office"],
    ),
    Station(
        id=10,
        name="Bajek",
        coordinates=Coordinates(latitude=34.6420, longitude=50.9020),
        is_terminal=False,
        is_transfer=False,
        facilities=["Escalator", "Bicycle Parking"],
    ),
    Station(
        id=11,
        name="Niroogah",
        coordinates=Coordinates(latitude=34.6600, longitude=50.8500),
        is_terminal=False,
        is_transfer=True,
        facilities=["Elevator", "Bus Stand", "Ticket Machine"],
    ),
    Station(
        id=12,
        name="Sadeqiyeh",
        coordinates=Coordinates(latitude=34.6700, longitude=50.8400),
        is_terminal=False,
        is_transfer=False,
        facilities=["Elevator", "Ticket Office"],
    ),
    Station(
        id=13,
        name="Chehel Derakht",
        coordinates=Coordinates(latitude=34.6800, longitude=50.8300),
        is_terminal=False,
        is_transfer=False,
        facilities=["Elevator", "Ticket Machine"],
    ),
    Station(
        id=14,
        name="Amin Abad",
        coordinates=Coordinates(latitude=34.6750, longitude=50.8450),
        is_terminal=False,
        is_transfer=False,
        facilities=["Elevator", "Taxi Stand"],
    ),
    Station(
        id=15,
        name="Pardisan",
        coordinates=Coordinates(latitude=34.5680, longitude=50.8150),
        is_terminal=False,
        is_transfer=True,
        facilities=["Major Bus Hub", "Park & Ride", "Elevator", "Escalator"],
    ),
    Station(
        id=16,
        name="University of Qom",
        coordinates=Coordinates(latitude=34.5950, longitude=50.8400),
        is_terminal=False,
        is_transfer=False,
        facilities=["Campus Gateway", "Bicycle Station", "Student Help Desk"],
    ),
    Station(
        id=17,
        name="Boostan Jangali Ghadir",
        coordinates=Coordinates(latitude=34.5750, longitude=50.9100),
        is_terminal=False,
        is_transfer=False,
        facilities=["Recreation Park Access", "Parking", "Bicycle Rental"],
    ),
    Station(
        id=18,
        name="Boostan Fadak",
        coordinates=Coordinates(latitude=34.6650, longitude=50.8950),
        is_terminal=False,
        is_transfer=False,
        facilities=["Park Access", "Family Pavilion", "Elevator"],
    ),
    Station(
        id=19,
        name="Railway Station Qom",
        coordinates=Coordinates(latitude=34.6550, longitude=50.8820),
        is_terminal=True,
        is_transfer=True,
        facilities=["National Rail Interchange", "Waiting Lounges", "Ticket Counters", "ATM"],
    ),
    Station(
        id=20,
        name="Terminal Mosaferbari Qom",
        coordinates=Coordinates(latitude=34.6920, longitude=50.8750),
        is_terminal=True,
        is_transfer=True,
        facilities=["Intercity Bus Terminal", "Food Court", "Luggage Services", "Taxi Stand"],
    ),
]

# Official Raw Edges from PDF Page 7
# Tuple structure: (Source, Target, Distance_KM, Time_Minutes, Hourly_Capacity)
OFFICIAL_EDGES: List[Tuple[str, str, float, float, int]] = [
    ("Terminal Mosaferbari Qom", "Qaleh Kamkar", 1.2, 3.0, 6000),
    ("Qaleh Kamkar", "Meydan Keshavarz", 2.5, 5.0, 5000),
    ("Meydan Keshavarz", "Meydan Motahari", 6.0, 10.0, 7000),
    ("Meydan Motahari", "Bimarestan Nekouei", 3.0, 5.0, 5500),
    ("Bimarestan Nekouei", "Meydan Baghiatollah", 2.0, 4.0, 5500),
    ("Meydan Baghiatollah", "Masjed Moghaddas Jamkaran", 3.8, 6.0, 8000),
    ("Meydan Motahari", "Haram Motahhar Hazrat Masoumeh", 1.5, 4.0, 9000),
    ("Haram Motahhar Hazrat Masoumeh", "Arg Salariyeh", 1.0, 3.0, 5000),
    ("Haram Motahhar Hazrat Masoumeh", "Darvazeh Rey", 1.8, 4.0, 5000),
    ("Darvazeh Rey", "Bajek", 1.3, 3.0, 4500),
    ("Meydan Motahari", "Niroogah", 2.8, 5.0, 6000),
    ("Niroogah", "Sadeqiyeh", 1.5, 3.0, 4500),
    ("Sadeqiyeh", "Chehel Derakht", 1.7, 3.0, 4000),
    ("Chehel Derakht", "Amin Abad", 1.4, 3.0, 4000),
    ("Niroogah", "Amin Abad", 2.0, 4.0, 4500),
    ("Meydan Baghiatollah", "Pardisan", 5.0, 8.0, 7500),
    ("Pardisan", "University of Qom", 2.2, 4.0, 6000),
    ("Pardisan", "Boostan Jangali Ghadir", 3.5, 6.0, 4000),
    ("Haram Motahhar Hazrat Masoumeh", "Boostan Fadak", 2.4, 4.0, 4500),
    ("Qaleh Kamkar", "Railway Station Qom", 3.0, 5.0, 6500),
    ("University of Qom", "Masjed Moghaddas Jamkaran", 4.5, 7.0, 5000),
]


def build_qom_metro_graph() -> Graph:
    """Instantiate and populate the complete Qom Metro network graph.

    Returns:
        Graph: Fully configured undirected graph containing all 20 stations and 21 connections.
    """
    graph = Graph(is_directed=False)

    for station in OFFICIAL_STATIONS:
        graph.add_station(station)

    for src, dst, dist, time_min, cap in OFFICIAL_EDGES:
        graph.add_connection(
            source=src,
            target=dst,
            distance_km=dist,
            time_minutes=time_min,
            capacity=cap,
            weight=dist,
            is_directed=False,
        )

    return graph
