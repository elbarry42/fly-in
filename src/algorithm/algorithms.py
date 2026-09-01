from heapq import heappop, heappush
from ..models.zone import Zone, ZoneType


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


def _rebuild_path(previous: dict[str, Zone | None], end: Zone) -> list[Zone]:
    """Rebuild the path from the predecessor table."""
    path: list[Zone] = []
    current: Zone | None = end

    while current is not None:
        path.append(current)
        current = previous[current.name]

    path.reverse()
    return path


def find_all_paths() -> list[Zone]:
    