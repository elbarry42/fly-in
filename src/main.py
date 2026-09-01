from .parser.parser import Parser
from .models.drone import Drone


def main() -> None:
    parser = Parser("maps/easy/01_linear_path.txt")
    graph = parser.parse()

    for zone in graph.zones.values():
        print(zone.name)

        for neighbor in zone.neighbors:
            print(" ->", neighbor.name)

    print("\nConnections :")

    for connection in graph.connections:
        print(connection)

    drone = Drone(1, graph.start)
    print(drone)


if __name__ == "__main__":
    main()
