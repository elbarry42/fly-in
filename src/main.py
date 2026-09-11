import sys

from .parser.parser import Parser
from .algorithm.algorithms import find_paths, assign_paths
from .simulation.simulation import Simulation
from .models.drone import Drone
from .visualization.visualizer import Visualizer


def create_simulation(map_file: str) -> Simulation:
    """Create a simulation from a map file."""
    parser = Parser(map_file)
    graph = parser.parse()

    if graph.start is None or graph.end is None:
        raise ValueError(
            "The map must contain a start and an end zone"
        )

    paths = find_paths(
        graph.start,
        graph.end,
    )

    assignments = assign_paths(
        paths,
        graph.nb_drones,
        graph.connections,
    )

    drones: list[Drone] = []

    for drone_id, path in enumerate(
        assignments,
        start=1,
    ):
        drone = Drone(
            drone_id,
            path[0],
        )

        drone.path = path
        drones.append(drone)

    return Simulation(
        graph,
        drones,
    )


def run_simulation(map_file: str) -> Simulation:
    """Run a complete simulation."""
    simulation = create_simulation(map_file)

    while not all(
        drone.finished
        for drone in simulation.drones
    ):
        before = [
            (
                drone.current_zone.name,
                drone.path_index,
                drone.in_transit,
            )
            for drone in simulation.drones
        ]

        simulation.step()

        after = [
            (
                drone.current_zone.name,
                drone.path_index,
                drone.in_transit,
            )
            for drone in simulation.drones
        ]

        if before == after:
            raise RuntimeError(
                "Simulation deadlock: "
                "no drone can move"
            )

    return simulation


def print_history(simulation: Simulation) -> None:
    """Display the simulation history."""
    for turn_number, events in enumerate(
        simulation.history,
        start=1,
    ):
        print(f"\n=== Turn {turn_number} ===")

        for event in events:
            print(event)


def run_single_map(map_file: str) -> None:
    """Run and display one map."""
    simulation = run_simulation(map_file)

    print(f"\nMap: {map_file}")
    print(f"Total turns: {simulation.turn}")

    visualizer = Visualizer(simulation)
    visualizer.run()


def run_all_maps() -> None:
    """Run all available test maps."""
    maps = [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/easy/03_basic_capacity.txt",
        "maps/medium/01_dead_end_trap.txt",
        "maps/medium/02_circular_loop.txt",
        "maps/medium/03_priority_puzzle.txt",
        "maps/hard/01_maze_nightmare.txt",
        "maps/hard/02_capacity_hell.txt",
        "maps/hard/03_ultimate_challenge.txt",
    ]

    print("=== Fly-in benchmark ===")

    for map_file in maps:
        try:
            simulation = run_simulation(map_file)

            print(
                f"[OK] {map_file}: "
                f"{simulation.turn} tours"
            )

        except (
            ValueError,
            RuntimeError,
            OSError,
        ) as error:
            print(
                f"[FAIL] {map_file}: "
                f"{error}"
            )


def main() -> None:
    """Run the Fly-in program."""
    if len(sys.argv) != 2:
        raise ValueError(
            "Usage: "
            "python3 -m src.main "
            "<map_file|--all>"
        )

    argument = sys.argv[1]

    if argument == "--all":
        run_all_maps()
        return

    run_single_map(argument)


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as error:
        print(
            f"Error: {error}",
            file=sys.stderr,
        )
        sys.exit(1)
