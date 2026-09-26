*This project has been created as part of the 42 curriculum by elbarry.*

# Fly-in

## Description

Fly-in is a Python project that routes a fleet of drones through a network of connected zones.

The goal is to move every drone from the unique `start_hub` to the unique `end_hub` in the fewest possible simulation turns while respecting movement, occupancy, capacity, and pathfinding constraints.

The project includes:

* a parser for the Fly-in map format;

* an object-oriented graph model;

* pathfinding and multi-path allocation;

* a turn-based simulation engine;

* zone and connection capacity management;

* normal, priority, restricted, and blocked zones;

* deadlock detection;

* step-by-step simulation history;

* a graphical Pygame visualization.

## Project Structure

```text

fly-in/

├── maps/

│   ├── easy/

│   ├── medium/

│   ├── hard/

│   └── challenger/

├── src/

│   ├── algorithm/

│   │   └── algorithms.py

│   ├── models/

│   │   ├── connection.py

│   │   ├── drone.py

│   │   ├── graph.py

│   │   └── zone.py

│   ├── parser/

│   │   └── parser.py

│   ├── simulation/

│   │   └── simulation.py

│   ├── visualization/

│   │   └── visualizer.py

│   └── main.py

├── mypy.ini

├── Makefile

└── README.md

```

## Instructions

### Installation

```bash

python3 -m pip install pygame mypy flake8

```

### Run

Run one map at a time:

```bash

python3 -m src.main maps/easy/01_linear_path.txt

```

Examples:

```bash

python3 -m src.main maps/easy/02_simple_fork.txt

python3 -m src.main maps/medium/01_dead_end_trap.txt

python3 -m src.main maps/hard/02_capacity_hell.txt

```

### Makefile

```bash

make install

make run MAP=maps/easy/01_linear_path.txt

make check

make debug MAP=maps/easy/01_linear_path.txt

make clean

```

`make check` runs the project's static checks, including `mypy` and `flake8`.

## Map Format

Example:

```text

nb_drones: 5

start_hub: hub 0 0 [color=green]

end_hub: goal 10 10 [color=yellow]

hub: roof1 3 4 [zone=restricted color=red]

hub: roof2 6 2 [zone=normal color=blue]

hub: corridorA 4 3 [zone=priority color=green max_drones=2]

hub: tunnelB 7 4 [zone=normal color=red]

hub: obstacleX 5 5 [zone=blocked color=gray]

connection: hub-roof1

connection: hub-corridorA

connection: roof1-roof2

connection: roof2-goal

connection: corridorA-tunnelB [max_link_capacity=2]

connection: tunnelB-goal

```

Comments start with `#`.

Zone names cannot contain spaces or dashes because connections use `zone1-zone2`.

## Zone Types

| Type         | Movement cost | Behavior                                  |

| ------------ | ------------: | ----------------------------------------- |

| `normal`     |             1 | Standard zone                             |

| `priority`   |             1 | Preferred during path selection when appropriate |

| `restricted` |             2 | Multi-turn movement                       |

| `blocked`    |             — | Cannot be entered or crossed              |

A restricted movement occupies the connection during transit and must arrive at the destination after the required number of turns. It cannot wait on the connection.

## Capacity Rules

* A normal zone contains at most one drone by default.

* `max_drones=N` allows up to `N` drones.

* The start zone has unlimited capacity.

* The end zone has unlimited capacity.

* Drones leaving a zone free capacity during the same turn.

* A drone cannot enter a zone if the resulting occupancy exceeds its capacity.

* `max_link_capacity` limits simultaneous traversal of a connection.

* Drones may move simultaneously when all constraints are respected.

## Algorithm

The graph is represented with `Zone`, `Connection`, `Graph`, and `Drone` objects.

No graph library such as NetworkX or `graphlib` is used. The graph and pathfinding logic are implemented directly in the project.

### Pathfinding

The project uses two complementary pathfinding approaches.

First, Dijkstra's algorithm is used to find a shortest path according to the movement costs of the zones:

```text

normal      -> 1

priority    -> 1

restricted  -> 2

blocked     -> inaccessible

```

The implementation uses a priority queue to process the lowest-cost candidate first.

Second, the project can enumerate valid simple paths between the start and end zones using depth-first search (DFS). This provides multiple route candidates instead of relying only on a single shortest path.

Blocked zones are excluded from candidate paths.

Priority zones have the same movement cost as normal zones, but the path
scoring gives preference to paths using priority zones when the other
criteria are comparable. This preference is combined with connection
congestion so that priority routes are not blindly overloaded.

### Path allocation

When several valid paths are available, the project evaluates them using several criteria, including:

* total movement cost;

* priority-zone usage;

* restricted-zone usage;

* path length;

* connection congestion.

The available paths are then distributed among the drones using the path cost, priority preference, and current connection load so that drones are not unnecessarily concentrated on the same route.

The goal is to obtain a good global simulation result while respecting the capacity constraints that are enforced during the simulation.

### Simulation

After paths have been assigned, the simulation executes movements turn by turn.

For each turn, it handles:

1. completion of restricted movements started during previous turns;

2. current zone occupancy;

3. connection usage;

4. destination reservations;

5. normal movements;

6. restricted movements and their transit state;

7. history and snapshots.

The simulation prevents drones from exceeding zone or connection capacities and allows simultaneous movements when they do not conflict.

A deadlock is detected if a complete simulation step produces no progress while drones still need to reach the destination.

## Algorithm Complexity and Trade-offs

The pathfinding design deliberately combines a shortest-path algorithm with multi-path exploration.

Dijkstra's algorithm provides an efficient way to find a minimum-cost path using the graph's movement costs. With a binary heap, its typical complexity is:

```text

O((V + E) log V)

```

where:

* `V` is the number of zones;

* `E` is the number of connections.

The multi-path search uses DFS to enumerate simple paths. Unlike Dijkstra's algorithm, the number of simple paths in a graph can grow exponentially with the graph size.

Therefore, the main trade-off is:

```text

More path candidates

    ↓

More routing choices

    ↓

Potentially better drone distribution

    ↓

Higher computation cost on complex graphs

```

The path-allocation stage also evaluates candidate paths according to their cost, priority preference, and connection congestion. This improves route distribution but adds additional computation compared with selecting one shortest path for every drone.

This trade-off is visible in the provided benchmarks: the Easy, Medium, and Hard maps are solved quickly, while the Challenger map requires significantly more computation because of its more complex path search.

The implementation therefore favors better route selection and capacity-aware distribution over minimizing the path search to a single candidate.

## Simulation Output

The simulation records drone movements turn by turn.

A normal movement is represented as:

```text

D<ID>-<zone>

```

A restricted movement in transit is represented as:

```text

D<ID>-<connection>

```

Example:

```text

D1-roof1 D2-corridorA

D1-roof2 D2-tunnelB

D1-goal D2-goal

```

Drones that do not move during a turn are omitted.

The simulation ends when all drones reach the end zone.

## Visualization

The graphical interface uses Pygame and displays:

* zones and their connections;

* colored zones;

* drone positions;

* the current turn;

* animated movement between turns;

* Previous / Next controls;

* Play / Pause;

* Reset.

Keyboard controls:

| Key           | Action        |

| ------------- | ------------- |

| `Left Arrow`  | Previous turn |

| `Right Arrow` | Next turn     |

| `Space`       | Play / Pause  |

| `R`           | Reset         |

| `Esc`         | Quit          |

The visualization provides a clear view of simultaneous movements, waiting, path distribution, restricted movements, and final delivery.

## Error Handling

The parser validates:

* positive drone count;

* exactly one start and end zone;

* unique zone names;

* integer coordinates;

* valid zone types;

* valid metadata;

* positive capacities;

* connections to previously defined zones;

* duplicate connections;

* malformed input.

Parsing errors produce clear messages indicating the line and cause.

`KeyboardInterrupt` is also handled so that `Ctrl+C` stops the program without an unnecessary traceback.

## Performance

The subject provides the following reference targets:

| Level  | Map                |     Target |

| ------ | ------------------ | ---------: |

| Easy   | Linear path        |  ≤ 6 turns |

| Easy   | Simple fork        |  ≤ 8 turns |

| Easy   | Basic capacity     |  ≤ 6 turns |

| Medium | Dead end trap      | ≤ 12 turns |

| Medium | Circular loop      | ≤ 15 turns |

| Medium | Priority puzzle    | ≤ 12 turns |

| Hard   | Maze nightmare     | ≤ 30 turns |

| Hard   | Capacity hell      | ≤ 35 turns |

| Hard   | Ultimate challenge | ≤ 45 turns |

The Challenger map is optional; its reference record is 45 turns.

### Benchmark Results

The provided maps were tested with their expected drone counts.

| Level      | Map                  |   Result |

| ---------- | -------------------- | -------: |

| Easy       | Linear path          |  4 turns |

| Easy       | Simple fork          |  4 turns |

| Easy       | Basic capacity       |  4 turns |

| Medium     | Dead end trap        |  8 turns |

| Medium     | Circular loop        |  9 turns |

| Medium     | Priority puzzle      |  6 turns |

| Hard       | Maze nightmare       | 13 turns |

| Hard       | Capacity hell        | 16 turns |

| Hard       | Ultimate challenge   | 26 turns |

| Challenger | The Impossible Dream | 45 turns |

Additional stress tests were performed with 10, 20, and 50 drones on the Easy, Medium, and Hard maps.

All stress-test simulations completed successfully without deadlock or runtime failure.

The benchmark results demonstrate that the implementation remains responsive with higher drone counts on the provided maps.

## Code Quality

The project follows the mandatory requirements:

* Python 3.10+;

* object-oriented design;

* type hints;

* `mypy`;

* `flake8`;

* PEP 257-style docstrings;

* explicit exception handling;

* no external graph library.

Run checks with:

```bash

make check

```

## Testing

The repository contains Easy, Medium, Hard, and optional Challenger maps.

They cover:

* linear routing;

* forks and multiple paths;

* capacity constraints;

* dead ends;

* circular paths;

* priority zones;

* restricted movement;

* complex mazes.

Maps are executed individually so each simulation can be inspected.

Additional performance tests were performed with 10, 20, and 50 drones to evaluate behavior under higher loads.

## Example

### Example Input

The following example uses a simple linear path with two drones:

```text

nb_drones: 2

start_hub: start 0 0 [color=green]

hub: waypoint1 1 0 [color=blue]

hub: waypoint2 2 0 [color=blue]

end_hub: goal 3 0 [color=red]

connection: start-waypoint1

connection: waypoint1-waypoint2

connection: waypoint2-goal

```

### Run

```bash

python3 -m src.main maps/easy/01_linear_path.txt

```

### Expected Simulation

With the default capacity of one drone per intermediate zone, the drones move through the linear path while respecting zone occupancy.

```text

Turn 1

D1-waypoint1

Turn 2

D1-waypoint2 D2-waypoint1

Turn 3

D1-goal D2-waypoint2

Turn 4

D2-goal

```

The simulation completes after **4 turns**, when both drones have reached the `end_hub`.

The program parses the map, builds the graph, computes paths, assigns drones, runs the simulation, reports the total number of turns, and opens the graphical visualization.

## Resources

* Fly-in subject specification provided by the 42 curriculum.

* Python documentation: https://docs.python.org/3/

* Python exceptions: https://docs.python.org/3/tutorial/errors.html

* Python typing: https://docs.python.org/3/library/typing.html

* mypy: https://mypy.readthedocs.io/

* flake8: https://flake8.pycqa.org/

* Pygame: https://www.pygame.org/docs/

## AI Usage

AI tools were used as a development assistant for:

* understanding the subject requirements;

* discussing project architecture;

* reviewing parser, algorithm, simulation, and visualization logic;

* explaining Python and type-checking concepts;

* debugging errors;

* improving exception handling;

* designing and reviewing the Pygame visualization;

* preparing project documentation.

AI suggestions were reviewed, adapted, tested, and validated manually.

The final implementation was checked through project execution, simulation tests, `mypy`, and `flake8`.

## Subject Compliance

The implementation provides the mandatory components described by the subject:

* input parser;

* pathfinding;

* multi-drone routing;

* turn-based simulation;

* occupancy and capacity rules;

* movement costs;

* restricted movement;

* deadlock handling;

* graphical visualization;

* step-by-step simulation history;

* error handling;

* object-oriented architecture;

* type checking and linting.