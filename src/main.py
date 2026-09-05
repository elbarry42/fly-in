from .parser.parser import Parser
from .algorithm.algorithms import find_paths, assign_paths
from .simulation.simulation import Simulation
from .models.drone import Drone


def main() -> None:
    parser = Parser("maps/easy/02_simple_fork.txt")
    graph = parser.parse()

    paths = find_paths(graph.start, graph.end)

    assignments = assign_paths(paths, graph.nb_drones)

    drones: list[Drone] = []

    for drone_id, path in enumerate(assignments, start=1):
        drone = Drone(drone_id, path[0])
        drone.path = path
        drones.append(drone)

    simulation = Simulation(graph, drones)

    for _ in range(5):
        simulation.step()

        print(f"Tour {simulation.turn}")

        for drone in simulation.drones:
            print(
                f"Drone {drone.id} : "
                f"{drone.current_zone.name}"
            )


if __name__ == "__main__":
    main()
