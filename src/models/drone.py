from .zone import Zone


class Drone:
    def __init__(self, drone_id: int, start: Zone):
        self.id = drone_id
        self.current_zone = start
        self.path: list[Zone] = []
        self.path_index = 0
        self.finished = False

    def __str__(self) -> str:
        return (
            f"Drone(id={self.id}, "
            f"zone={self.current_zone.name})"
        )
