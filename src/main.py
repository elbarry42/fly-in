from .parser.parser import Parser
from .algorithm.algorithms import find_paths


def main() -> None:
    parser = Parser("maps/easy/02_simple_fork.txt")
    graph = parser.parse()

    paths = find_paths(graph.start, graph.end)

    for i, path in enumerate(paths, 1):
        print(f"Chemin {i} :")

        for zone in path:
            print(zone.name)


if __name__ == "__main__":
    main()
