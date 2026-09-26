from .zone import Zone, HubType
from .connection import Connection


class Graph:
    """Represent the zones and connections of the simulation map."""

    def __init__(self):
        """Initialize an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

        self.start: Zone | None = None
        self.end: Zone | None = None

        self.nb_drones = 0

    def add_zone(self, zone: Zone):
        """Add a zone to the graph."""
        if self.has_zone(zone.name):
            raise ValueError(f"Zone '{zone.name}' already exists")

        self.zones[zone.name] = zone

        if zone.hub_type == HubType.START:
            self.start = zone
        elif zone.hub_type == HubType.END:
            self.end = zone

    def add_connection(self, connection: Connection):
        """Add a connection to the graph."""
        self.connections.append(connection)

    def get_zone(self, name: str) -> Zone:
        """Return a zone from its name."""
        return self.zones[name]

    def has_zone(self, name: str) -> bool:
        """Check whether a zone exists in the graph."""
        return name in self.zones
