from .parser.parser import Parser
from .algorithm.algorithms import find_paths, assign_paths


def main() -> None:
    parser = Parser("maps/easy/02_simple_fork.txt")
    graph = parser.parse()

    paths = find_paths(graph.start, graph.end)

    assignments = assign_paths(
        paths,
        graph.nb_drones,
    )

    for drone_id, path in enumerate(assignments, start=1):
        print(f"Drone {drone_id} :")

        for zone in path:
            print(zone.name)

        print()


if __name__ == "__main__":
    main()
