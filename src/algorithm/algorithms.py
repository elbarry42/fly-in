from heapq import heappop, heappush

from ..models.zone import Zone, ZoneType
from ..models.connection import Connection


def find_shortest_path(start: Zone, end: Zone) -> list[Zone]:
    """Find the lowest-cost path between two zones using Dijkstra."""
    distances: dict[str, int] = {start.name: 0}
    previous: dict[str, Zone | None] = {start.name: None}
    queue: list[tuple[int, str, Zone]] = []
    heappush(queue, (0, start.name, start))

    while queue:
        current_cost, _, current = heappop(queue)
        if current == end:
            break
        if current_cost > distances[current.name]:
            continue

        for neighbor in current.neighbors:
            if neighbor.zone_type == ZoneType.BLOCKED:
                continue
            cost = _movement_cost(neighbor)
            new_cost = current_cost + cost
            if new_cost < distances.get(neighbor.name, float("inf")):
                distances[neighbor.name] = new_cost
                previous[neighbor.name] = current
                heappush(queue, (new_cost, neighbor.name, neighbor))

    if end.name not in distances:
        raise ValueError("No path found between start and end")
    return _rebuild_path(previous, end)


def _movement_cost(zone: Zone) -> int:
    """Return the movement cost of entering a zone."""
    if zone.zone_type == ZoneType.RESTRICTED:
        return 2
    return 1


def _rebuild_path(
    previous: dict[str, Zone | None], end: Zone
) -> list[Zone]:
    """Rebuild the path from the predecessor table."""
    path: list[Zone] = []
    current: Zone | None = end
    while current is not None:
        path.append(current)
        current = previous[current.name]
    path.reverse()
    return path


def find_all_paths(
    current: Zone,
    end: Zone,
    path: list[Zone],
    paths: list[list[Zone]],
) -> None:
    if current == end:
        paths.append(path.copy())
        return

    for neighbor in current.neighbors:
        if neighbor.zone_type == ZoneType.BLOCKED:
            continue
        if neighbor in path:
            continue
        path.append(neighbor)
        find_all_paths(neighbor, end, path, paths)
        path.pop()


def find_paths(start: Zone, end: Zone) -> list[list[Zone]]:
    paths: list[list[Zone]] = []
    find_all_paths(start, end, [start], paths)
    return paths


def path_cost(path: list[Zone], connections: list[Connection]) -> int:
    """Calculate the total movement cost of a path."""
    if len(path) < 2:
        return 0

    total = 0
    for zone in path[1:]:
        if zone.zone_type == ZoneType.BLOCKED:
            return 10**9
        if zone.zone_type == ZoneType.RESTRICTED:
            total += 2
        else:
            total += 1
    return total


def path_score(
    path: list[Zone],
    connections: list[Connection],
) -> tuple[int, int, int, int]:
    """Calculate the score used to compare paths."""
    cost = path_cost(path, connections)
    priority_count = sum(
        1 for zone in path if zone.zone_type == ZoneType.PRIORITY
    )
    restricted_count = sum(
        1 for zone in path if zone.zone_type == ZoneType.RESTRICTED
    )
    return (cost, -priority_count, restricted_count, len(path))


def _connection_load_score(
    path: list[Zone],
    connections: list[Connection],
    connection_loads: dict[tuple[str, str], int],
) -> float:
    """Estimate the congestion created by assigning a drone to a path."""
    score = 0.0
    for i in range(len(path) - 1):
        connection = get_connection(path[i], path[i + 1], connections)
        if connection is None:
            raise ValueError(
                f"No connection between {path[i].name} and "
                f"{path[i + 1].name}"
            )

        key = (
            min(path[i].name, path[i + 1].name),
            max(path[i].name, path[i + 1].name),
        )
        current_load = connection_loads.get(key, 0)
        score += (current_load + 1) / connection.max_link_capacity
    return score


def assign_paths(
    paths: list[list[Zone]],
    nb_drones: int,
    connections: list[Connection] | None = None,
) -> list[list[Zone]]:
    """Distribute drones while limiting connection congestion."""
    if not paths:
        raise ValueError("No path available")
    if nb_drones <= 0:
        raise ValueError("Number of drones must be positive")
    if connections is None:
        connections = []

    valid_paths: list[list[Zone]] = []
    for path in paths:
        if len(path) < 2:
            continue
        if any(
            zone.zone_type == ZoneType.BLOCKED
            for zone in path
        ):
            continue
        valid_paths.append(path)

    if not valid_paths:
        raise ValueError("No valid path available")

    valid_paths.sort(key=lambda path: path_score(path, connections))
    assignments: list[list[Zone]] = []
    connection_loads: dict[tuple[str, str], int] = {}

    for _ in range(nb_drones):
        best_path: list[Zone] | None = None
        best_score: tuple[float, int, int, int] | None = None

        for path in valid_paths:
            congestion = _connection_load_score(
                path, connections, connection_loads
            )
            cost, priority_score, restricted_count, length = path_score(
                path, connections
            )
            score = (
                cost + congestion,
                cost,
                priority_score,
                restricted_count,
            )
            if best_score is None or score < best_score:
                best_score = score
                best_path = path

        if best_path is None:
            raise ValueError("Unable to assign a path to a drone")

        assignments.append(best_path)
        for i in range(len(best_path) - 1):
            key = (
                min(best_path[i].name, best_path[i + 1].name),
                max(best_path[i].name, best_path[i + 1].name),
            )
            connection_loads[key] = connection_loads.get(key, 0) + 1

    return assignments


def get_connection(
    start: Zone,
    end: Zone,
    connections: list[Connection],
) -> Connection | None:
    for connection in connections:
        if connection.start == start and connection.end == end:
            return connection
        if connection.start == end and connection.end == start:
            return connection
    return None


def path_capacity(path: list[Zone], connections: list[Connection]) -> int:
    capacity = float("inf")
    for zone in path:
        capacity = min(capacity, zone.max_drones)

    for i in range(len(path) - 1):
        connection = get_connection(path[i], path[i + 1], connections)
        if connection is None:
            raise ValueError(
                f"No connection between {path[i].name} and "
                f"{path[i + 1].name}"
            )
        capacity = min(capacity, connection.max_link_capacity)

    return int(capacity)
