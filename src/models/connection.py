from .zone import Zone


class Connection:
    """Represent a connection between two zones."""

    def __init__(
        self,
        start: Zone,
        end: Zone,
        max_link_capacity: int = 1
    ):
        """Initialize a connection between two zones."""
        self.start = start
        self.end = end

        self.current_drones = 0
        self.max_link_capacity = max_link_capacity

    def __str__(self) -> str:
        """Return a readable representation of the connection."""
        return (
            f"Connection("
            f"{self.start.name} -> "
            f"{self.end.name}, "
            f"capacity={self.max_link_capacity})"
        )

    def is_full(self) -> bool:
        """Check whether the connection has reached its capacity."""
        return self.current_drones >= self.max_link_capacity

    def contains(self, zone: Zone) -> bool:
        """Check whether a zone belongs to this connection."""
        return zone == self.start or zone == self.end

    def other(self, zone: Zone) -> Zone:
        """Return the zone at the opposite end of the connection."""
        if zone == self.start:
            return self.end
        return self.start
