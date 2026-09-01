from ..models.graph import Graph
from ..models.connection import Connection
from ..models.zone import Zone, HubType, ZoneType


class Parser:
    def __init__(self, filename: str):
        self.filename = filename
        self.graph = Graph()

    def parse(self) -> Graph:
        try:
            with open(self.filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("#"):
                        continue
                    elif line.startswith("nb_drones"):
                        self._parse_nb_drones(line)
                        continue
                    elif line.startswith("connection"):
                        self._parse_connection(line)
                        continue
                    self._parse_zone(line)
        except FileNotFoundError:
            raise ValueError(f"File '{self.filename}' not found")
        if self.graph.start is None:
            raise ValueError("Missing start_hub")

        if self.graph.end is None:
            raise ValueError("Missing end_hub")

        if self.graph.nb_drones <= 0:
            raise ValueError("Invalid number of drones")
        return self.graph

    def _parse_zone(self, line: str):
        left, right = line.split(":", 1)
        if "[" in right:
            zone_data, options = right.split("[", 1)
        else:
            zone_data = right
            options = ""

        hub_type = HubType(left.strip())

        name, x, y = zone_data.strip().split()

        zone = Zone(
            name=name,
            hub_type=hub_type,
            x=int(x),
            y=int(y),
        )
        self._parse_zone_options(zone, options)
        self.graph.add_zone(zone)

    def _parse_connection(self, line: str):
        _, right = line.split(":", 1)
        if "[" in right:
            zone_data, options = right.split("[", 1)
        else:
            zone_data = right
            options = ""

        start_name, end_name = zone_data.strip().split("-")

        if not self.graph.has_zone(start_name):
            raise ValueError(f"Unknown zone: {start_name}")
        if not self.graph.has_zone(end_name):
            raise ValueError(f"Unknown zone: {end_name}")

        start_zone = self.graph.get_zone(start_name)
        end_zone = self.graph.get_zone(end_name)

        connection = Connection(start_zone, end_zone)

        self._parse_connection_options(connection, options)
        self.graph.add_connection(connection)

        start_zone.add_neighbor(end_zone)
        end_zone.add_neighbor(start_zone)

    def _parse_nb_drones(self, line: str):
        _, value = line.split(":")
        self.graph.nb_drones = int(value.strip())

    def _parse_zone_options(self, zone: Zone, options: str):
        options = options.removesuffix("]")
        if not options:
            return

        parts = options.split()
        for part in parts:
            if "=" not in part:
                raise ValueError(f"Invalid zone option: {part}")

            key, value = part.split("=", 1)
            if key == "color":
                zone.color = value
            elif key == "zone":
                zone.zone_type = ZoneType(value)
            elif key == "max_drones":
                zone.max_drones = int(value)
            else:
                raise ValueError(f"Unknown zone option: {key}")

    def _parse_connection_options(
        self,
        connection: Connection,
        options: str,
    ):
        options = options.removesuffix("]")
        if not options:
            return

        parts = options.split()
        for part in parts:
            if "=" not in part:
                raise ValueError(f"Invalid connection option: {part}")
            key, value = part.split("=", 1)
            if key == "max_link_capacity":
                connection.max_link_capacity = int(value)
            else:
                raise ValueError(f"Unknown connection option: {key}")
