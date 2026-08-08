from __future__ import annotations
from enum import Enum


class HubType(Enum):
    START = "start_hub"
    HUB = "hub"
    END = "end_hub"


class ZoneType(Enum):
    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


class Zone:
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
        return (
            f"Zone("
            f"name={self.name}, "
            f"type={self.hub_type.value}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"zone_type={self.zone_type.value}, "
            f"capacity={self.max_drones})"
        )

    def add_neighbor(self, neighbor: Zone):
        self.neighbors.append(neighbor)

    def is_full(self) -> bool:
        return self.current_drones >= self.max_drones

    def is_blocked(self) -> bool:
        return self.zone_type == ZoneType.BLOCKED
