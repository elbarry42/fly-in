from __future__ import annotations
from enum import Enum


class HubType(Enum):
    """Define the possible types of hubs in the map."""

    START = "start_hub"
    HUB = "hub"
    END = "end_hub"


class ZoneType(Enum):
    """Define the possible types of zones in the map."""

    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


class Zone:
    """Represent a zone where drones can move or wait."""

    def __init__(
        self,
        name: str,
        hub_type: HubType,
        x: int,
        y: int,
        zone_type: ZoneType = ZoneType.NORMAL,
        color: str | None = None,
        max_drones: int = 1,
    ):
        """Initialize a zone with its map and capacity information."""
        self.name = name
        self.hub_type = hub_type

        self.x = x
        self.y = y

        self.zone_type = zone_type
        self.color = color

        self.max_drones = max_drones
        self.current_drones = 0

        self.neighbors: list[Zone] = []

    def __str__(self) -> str:
        """Return a readable representation of the zone."""
        return (
            f"Zone(name={self.name}, type={self.hub_type.value}, "
            f"x={self.x}, y={self.y}, zone_type={self.zone_type.value}, "
            f"capacity={self.max_drones})"
        )

    def add_neighbor(self, neighbor: Zone):
        """Add a neighboring zone."""
        self.neighbors.append(neighbor)

    def is_full(self) -> bool:
        """Check whether the zone has reached its capacity."""
        return self.current_drones >= self.max_drones

    def is_blocked(self) -> bool:
        """Check whether the zone is blocked."""
        return self.zone_type == ZoneType.BLOCKED
