from ..models.graph import Graph
from ..models.connection import Connection
from ..models.zone import Zone, HubType


class Parser:
    def __init__(self, filename: str):
        self.filename = filename
        self.graph = Graph()

    def parse(self) -> Graph:
        with open(self.filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                if line.startswith("nb_drones"):
                    continue
                if line.startswith("connection"):
                    self._parse_connection(line)
                    continue
                self._parse_zone(line)
        return self.graph

    def _parse_zone(self, line: str):
        left, right = line.split(":")
        hub_type = HubType(left.strip())
        parts = right.strip().split()

        name=parts[0]
        x=int(parts[1])
        y=int(parts[2])

        zone = Zone(
            name=name,
            hub_type=hub_type,
            x=x,
            y=y,
        )
        self.graph.add_zone(zone)

    def _parse_connection(self, line: str):
        left, right = line.split(":")

        start_name, end_name = right.strip().split("-")

        start_zone = self.graph.zones[start_name]
        end_zone = self.graph.zones[end_name]

        connection = Connection(start_zone, end_zone)

        self.graph.add_connection(connection)

        start_zone.add_neighbor(end_zone)
        end_zone.add_neighbor(start_zone)

        

