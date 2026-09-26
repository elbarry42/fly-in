from ..models.zone import Zone, ZoneType
from ..models.graph import Graph
from ..models.drone import Drone
from ..models.connection import Connection
from ..algorithm.algorithms import get_connection


class Simulation:
    """Manage the execution of the drone simulation."""

    def __init__(self, graph: Graph, drones: list[Drone]):
        """Initialize the simulation with a graph and drones."""
        self.graph = graph
        self.drones = drones
        self.turn = 0
        self.transit_remaining: dict[int, int] = {}
        self.transit_arrivals: set[int] = set()

        self.history: list[list[str]] = []
        self.snapshots: list[
            list[tuple[int, str, int, bool, str | None, str | None]]
        ] = []
        self._save_snapshot()

    def _finish_transits(
        self,
        occupancy: dict[str, int],
        reserved: dict[str, int],
    ) -> list[str]:
        """Advance restricted movements and finish completed transits."""
        events: list[str] = []

        for drone in self.drones:
            if not drone.in_transit:
                continue

            destination = drone.transit_destination
            connection = drone.transit_connection

            if destination is None:
                raise ValueError(
                    f"Drone {drone.id} has no transit destination"
                )

            if connection is None:
                raise ValueError(
                    f"Drone {drone.id} has no transit connection"
                )

            remaining = self.transit_remaining.get(drone.id)
            if remaining is None:
                raise ValueError(
                    f"Drone {drone.id} has no transit duration"
                )

            remaining -= 1
            self.transit_remaining[drone.id] = remaining

            if remaining > 0:
                events.append(
                    f"D{drone.id}-{self._connection_name(connection)}"
                )
                continue

            connection.current_drones -= 1
            drone.current_zone = destination
            drone.path_index += 1
            drone.in_transit = False
            drone.transit_connection = None
            drone.transit_destination = None
            del self.transit_remaining[drone.id]

            if destination not in (self.graph.start, self.graph.end):
                reserved[destination.name] = (
                    reserved.get(destination.name, 0) - 1
                )
                occupancy[destination.name] = (
                    occupancy.get(destination.name, 0) + 1
                )

            events.append(f"D{drone.id}-{destination.name}")
            self.transit_arrivals.add(drone.id)

            if drone.path_index >= len(drone.path) - 1:
                drone.finished = True

        return events

    def _current_occupancy(self) -> dict[str, int]:
        """Return current occupancy for each zone."""
        occupancy: dict[str, int] = {}

        for drone in self.drones:
            if drone.finished or drone.in_transit:
                continue
            if drone.id in self.transit_arrivals:
                continue

            zone_name = drone.current_zone.name
            occupancy[zone_name] = occupancy.get(zone_name, 0) + 1

        return occupancy

    def _reserved_destinations(self) -> dict[str, int]:
        """Count destination slots reserved by drones in transit."""
        reserved: dict[str, int] = {}

        for drone in self.drones:
            if not drone.in_transit:
                continue

            destination = drone.transit_destination
            if destination is None:
                raise ValueError(
                    f"Drone {drone.id} has no transit destination"
                )

            if destination in (self.graph.start, self.graph.end):
                continue

            reserved[destination.name] = (
                reserved.get(destination.name, 0) + 1
            )

        return reserved

    def _connection_name(self, connection: Connection) -> str:
        """Return the output name of a connection."""
        return f"{connection.start.name}-{connection.end.name}"

    def _connection_key(
        self, start: Zone, end: Zone
    ) -> tuple[str, str]:
        """Return a unique key for an undirected connection."""
        return min(start.name, end.name), max(start.name, end.name)

    def _can_enter_zone(
        self,
        zone: Zone,
        occupancy: dict[str, int],
        reserved: dict[str, int],
    ) -> bool:
        """Check whether a drone can reserve a destination zone."""
        if zone == self.graph.start:
            return True

        if zone == self.graph.end:
            return True

        if zone.zone_type == ZoneType.BLOCKED:
            return False

        occupied = occupancy.get(zone.name, 0)
        reservations = reserved.get(zone.name, 0)

        return occupied + reservations < zone.max_drones

    def _can_use_connection(
        self,
        connection: Connection,
        connection_usage: dict[tuple[str, str], int],
    ) -> bool:
        """Check whether a connection has remaining capacity."""
        key = self._connection_key(connection.start, connection.end)

        active = connection.current_drones
        current_turn = connection_usage.get(key, 0)

        return active + current_turn < connection.max_link_capacity

    def _reserve_zone(
        self, zone: Zone, occupancy: dict[str, int]
    ) -> None:
        """Reserve one place in a zone."""
        if zone == self.graph.start:
            return

        if zone == self.graph.end:
            return

        occupancy[zone.name] = occupancy.get(zone.name, 0) + 1

    def _release_zone(
        self, zone: Zone, occupancy: dict[str, int]
    ) -> None:
        """Release one place in a zone."""
        if zone == self.graph.start:
            return

        if zone == self.graph.end:
            return

        current = occupancy.get(zone.name, 0)

        if current <= 0:
            raise ValueError(
                f"Invalid occupancy for zone '{zone.name}'"
            )

        occupancy[zone.name] = current - 1

    def step(self) -> None:
        """Execute one simulation turn."""
        occupancy = self._current_occupancy()
        reserved = self._reserved_destinations()
        turn_events = self._finish_transits(occupancy, reserved)
        connection_usage: dict[tuple[str, str], int] = {}
        candidates: list[tuple[Drone, Zone, Connection]] = []
        moves: list[tuple[Drone, Zone]] = []
        transit_moves: list[tuple[Drone, Zone, Connection]] = []

        for drone in self.drones:
            if drone.finished or drone.in_transit:
                continue
            if drone.id in self.transit_arrivals:
                continue

            next_index = drone.path_index + 1
            if next_index >= len(drone.path):
                drone.finished = True
                continue

            next_zone = drone.path[next_index]
            if next_zone.zone_type == ZoneType.BLOCKED:
                continue

            connection = get_connection(
                drone.current_zone,
                next_zone,
                self.graph.connections,
            )
            if connection is None:
                raise ValueError(
                    f"No connection between "
                    f"{drone.current_zone.name} and {next_zone.name}"
                )

            if not self._can_use_connection(
                connection, connection_usage
            ):
                continue

            key = self._connection_key(
                drone.current_zone,
                next_zone,
            )
            connection_usage[key] = connection_usage.get(key, 0) + 1
            candidates.append((drone, next_zone, connection))

        for drone, _, _ in candidates:
            self._release_zone(drone.current_zone, occupancy)

        for drone, next_zone, connection in candidates:
            current_zone = drone.current_zone

            if not self._can_enter_zone(
                next_zone, occupancy, reserved
            ):
                self._reserve_zone(current_zone, occupancy)
                key = self._connection_key(
                    current_zone,
                    next_zone,
                )
                connection_usage[key] -= 1
                continue

            if next_zone.zone_type == ZoneType.RESTRICTED:
                transit_moves.append((drone, next_zone, connection))
                connection.current_drones += 1
                reserved[next_zone.name] = (
                    reserved.get(next_zone.name, 0) + 1
                )
            else:
                self._reserve_zone(next_zone, occupancy)
                moves.append((drone, next_zone))

        for drone, next_zone in moves:
            drone.current_zone = next_zone
            drone.path_index += 1
            turn_events.append(f"D{drone.id}-{next_zone.name}")

            if drone.path_index >= len(drone.path) - 1:
                drone.finished = True

        for drone, next_zone, connection in transit_moves:
            drone.in_transit = True
            drone.transit_connection = connection
            drone.transit_destination = next_zone
            self.transit_remaining[drone.id] = 1
            turn_events.append(
                f"D{drone.id}-{self._connection_name(connection)}"
            )

        self.transit_arrivals.clear()

        if not turn_events:
            turn_events.append("")

        self.history.append(turn_events)
        self.turn += 1
        self._save_snapshot()

    def _save_snapshot(self) -> None:
        """Save the complete state of every drone."""
        snapshot: list[
            tuple[int, str, int, bool, str | None, str | None]
        ] = []

        for drone in self.drones:
            destination = (
                drone.transit_destination.name
                if drone.transit_destination is not None
                else None
            )

            connection = None
            if drone.transit_connection is not None:
                connection = (
                    f"{drone.transit_connection.start.name}-"
                    f"{drone.transit_connection.end.name}"
                )

            snapshot.append(
                (
                    drone.id,
                    drone.current_zone.name,
                    drone.path_index,
                    drone.finished,
                    destination,
                    connection,
                )
            )

        self.snapshots.append(snapshot)

    def get_snapshot(
        self, turn: int
    ) -> list[tuple[int, str, int, bool, str | None, str | None]]:
        """Return the drone states for a given turn."""
        if turn < 0 or turn > self.turn:
            raise ValueError(f"Invalid turn: {turn}")

        return self.snapshots[turn]
