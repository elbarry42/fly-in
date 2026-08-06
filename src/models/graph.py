from .zone import Zone
from .connection import Connection


class Graph:
    def __init__(self):
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    def add_zone(self, zone: Zone):
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection):
        self.connections.append(connection)
