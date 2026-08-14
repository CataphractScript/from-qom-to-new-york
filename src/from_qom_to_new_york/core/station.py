"""Station data model representing vertices in the transit network."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Coordinates:
    """Geographical coordinates (latitude, longitude) for spatial distance heuristics."""

    latitude: float
    longitude: float

    def euclidean_distance_to(self, other: Coordinates) -> float:
        """Calculate flat Cartesian Euclidean distance (scaled to approx km).

        One degree of latitude in Qom (~34.6 deg N) is approx 110.9 km.
        One degree of longitude is approx 111.32 * cos(34.6 deg) ~= 91.6 km.
        """
        d_lat = (self.latitude - other.latitude) * 110.9
        d_lon = (self.longitude - other.longitude) * 91.6
        return math.sqrt(d_lat**2 + d_lon**2)

    def haversine_distance_to(self, other: Coordinates) -> float:
        """Calculate Great-Circle distance in kilometers using the Haversine formula.

        Used as an admissible and consistent lower-bound heuristic for A* pathfinding.
        """
        earth_radius_km = 6371.0
        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(other.latitude)
        d_lat = math.radians(other.latitude - self.latitude)
        d_lon = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(d_lat / 2.0) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return earth_radius_km * c


@dataclass
class Station:
    """Represents a transit station (graph vertex).

    Attributes:
        id: Unique integer identifier.
        name: Canonical English station name.
        coordinates: Optional geographic coordinates for spatial heuristics.
        is_terminal: Whether this station serves as an intercity/major terminal.
        is_transfer: Whether this station serves as a transfer intersection.
        daily_capacity: Design passenger capacity per day.
        facilities: List of amenities (e.g. 'Elevator', 'Parking', 'Bus Interchange').
    """

    id: int
    name: str
    coordinates: Optional[Coordinates] = None
    is_terminal: bool = False
    is_transfer: bool = False
    daily_capacity: int = 50000
    facilities: List[str] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Station):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __repr__(self) -> str:
        return f"Station(id={self.id}, name='{self.name}')"

    def __str__(self) -> str:
        return self.name
