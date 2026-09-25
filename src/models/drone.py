from __future__ import annotations

from .zone import Zone
from .connection import Connection


class Drone:
    def __init__(
        self,
        drone_id: int,
        start: Zone,
    ):
        self.id = drone_id
        self.current_zone = start

        self.path: list[Zone] = []
        self.path_index = 0
        self.finished = False

        # Restricted movement state.
        self.in_transit = False
        self.transit_connection: Connection | None = None
        self.transit_destination: Zone | None = None

    def __str__(self) -> str:
        if self.in_transit:
            destination = (
                self.transit_destination.name
                if self.transit_destination is not None
                else "?"
            )

            return f"Drone(id={self.id}, transit -> {destination})"

        return f"Drone(id={self.id}, zone={self.current_zone.name})"
