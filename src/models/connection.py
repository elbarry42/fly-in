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
        self.max_link_capacity = max_link_capacity

    def __str__(self) -> str:
        return(
            f"Connection("
            f"{self.start.name} -> "
            f"{self.end.name}, "
            f"capacity={self.max_link_capacity})"
        )