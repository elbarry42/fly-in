from .models.zone import Zone
from .parser.parser import Parser
from .models.connection import Connection
from .models.graph import Graph


def main() -> None:
    # graph = Graph()

    # start = Zone("start", "start_hub", 0, 0)
    # a = Zone("A", "hub", 1, 0)
    # end = Zone("end", "end_hub", 2, 0)

    # graph.add_zone(start)
    # graph.add_zone(a)
    # graph.add_zone(end)

    # connection1 = Connection(start, a)
    # connection2 = Connection(a, end)

    # graph.connections.append(connection1)
    # graph.connections.append(connection2)

    # print("===== ZONES =====")
    # for zone in graph.zones.values():
    #     print(zone.name, zone.hub_type, zone.x, zone.y)

    # print("\n===== CONNECTIONS =====")
    # for connection in graph.connections:
    #     print(f"{connection.start.name} -> {connection.end.name}")
    parser = Parser("maps/easy/01_linear_path.txt")
    graph = parser.parse()

    for zone in graph.zones.values():
        print(zone.name)

        for neighbor in zone.neighbors:
            print(" ->", neighbor.name)

    print("\nConnections :")

    for connection in graph.connections:
        print(connection)


if __name__ == "__main__":
    main()