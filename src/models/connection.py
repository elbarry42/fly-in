from .zone import Zone


class Connection:
    def __init__(
        self,
        start: Zone,
        end: Zone,
        max_link_capacity: int = 1
    ):
        self.start = start
        self.end = end

        self.current_drones = 0
        self.max_link_capacity = max_link_capacity

    def __str__(self) -> str:
        return(
            f"Connection("
            f"{self.start.name} -> "
            f"{self.end.name}, "
            f"capacity={self.max_link_capacity})"
        )

    def is_full(self) -> bool:
        return self.current_drones >= self.max_link_capacity

    def contains(self, zone: Zone) -> bool:
        return zone == self.start or zone == self.end

    def other(self, zone: Zone) -> Zone:
        if zone == self.start:
            return self.end
        return self.start
