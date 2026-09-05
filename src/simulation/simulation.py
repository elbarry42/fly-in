from ..models.zone import Zone
from ..models.graph import Graph
from ..models.drone import Drone
from ..models.connection import Connection
from ..algorithm.algorithms import get_connection


class Simulation:
    def __init__(
        self,
        graph: Graph,
        drones: list[Drone]
    ):
        self.graph = graph
        self.drones = drones
        self.turn = 0

    def step(self) -> None:
        occupancy = self._current_occupancy()

        connection_usage: dict[tuple[str, str], int] = {}

        moves: list[tuple[Drone, Zone, Connection]] = []

        for drone in self.drones:
            if drone.finished:
                continue

            next_index = drone.path_index + 1

            if next_index >= len(drone.path):
                drone.finished = True
                continue

            next_zone = drone.path[next_index]

            connection = get_connection(
                drone.current_zone,
                next_zone,
                self.graph.connections
            )

            if connection is None:
                continue

            if not self._can_enter_zone(next_zone, occupancy):
                continue

            if not self._can_use_connection(connection, connection_usage):
                continue

            source_name = drone.current_zone.name
            destination_name = next_zone.name

            connection_key = (
                min(source_name, destination_name),
                max(source_name, destination_name)
            )

            occupancy[source_name] -= 1

            if next_zone != self.graph.end:
                occupancy[destination_name] = (
                    occupancy.get(destination_name, 0) + 1
                )

            connection_usage[connection_key] = (
                connection_usage.get(connection_key, 0) + 1
            )

            moves.append((drone, next_zone, connection))

            for drone, next_zone, _ in moves:
                drone.current_zone = next_zone
                drone.path_index += 1

                if next_zone == drone.path[-1]:
                    drone.finished = True

        self.turn += 1

    def _can_enter_zone(
        self,
        zone: Zone,
        occupancy: dict[str, int]
    ) -> bool:
        if zone == self.graph.start:
            return True
        if zone == self.graph.end:
            return True

        return occupancy.get(zone.name, 0) < zone.max_drones

    def _reserved_zone_count(
        self,
        zone: Zone,
        reserved_zones: dict[str, int]
    ) -> int:
        return reserved_zones.get(zone.name, 0)

    def _current_occupancy(self) -> dict[str, int]:
        occupancy: dict[str, int] = {}

        for drone in self.drones:
            if drone.finished:
                continue

            zone_name = drone.current_zone.name
            occupancy[zone_name] = occupancy.get(zone_name, 0) + 1

        return occupancy

    def _can_use_connection(
            self,
            connection: Connection,
            connection_usage: dict[tuple[str, str], int]
    ) -> bool:
        key = (
            min(connection.start.name, connection.end.name),
            max(connection.start.name, connection.end.name)
        )

        usage = connection_usage.get(key, 0)

        return usage < connection.max_link_capacity
