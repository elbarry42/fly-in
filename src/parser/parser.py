from __future__ import annotations

import re

from ..models.graph import Graph
from ..models.connection import Connection
from ..models.zone import Zone, HubType, ZoneType


class Parser:
    """Parse a Fly-in map file into a Graph."""

    ZONE_NAME_PATTERN = re.compile(r"^[^\s-]+$")
    INTEGER_PATTERN = re.compile(r"^-?\d+$")
    MAX_DRONES = 100
    MIN_COORDINATE = -50
    MAX_COORDINATE = 50

    def __init__(self, filename: str):
        self.filename = filename
        self.graph = Graph()
        self._connection_keys: set[tuple[str, str]] = set()
        self._seen_nb_drones = False
        self._start_count = 0
        self._end_count = 0

    def parse(self) -> Graph:
        """Parse the map and return the resulting graph."""
        try:
            with open(self.filename, "r") as file:
                first_line_read = False

                for line_number, raw_line in enumerate(file, start=1):
                    line = raw_line.split("#", 1)[0].strip()

                    if not line:
                        continue

                    if not first_line_read:
                        first_line_read = True

                        if not line.startswith("nb_drones:"):
                            raise ValueError(
                                f"Line {line_number}: "
                                "first line must define nb_drones"
                            )

                    try:
                        self._parse_line(line, line_number)
                    except ValueError as error:
                        raise ValueError(
                            f"Line {line_number}: {error}"
                        ) from error

        except FileNotFoundError as error:
            raise ValueError(f"File '{self.filename}' not found") from error
        except OSError as error:
            raise ValueError(
                f"Unable to read '{self.filename}': {error}"
            ) from error

        self._validate_graph()

        return self.graph

    def _parse_line(self, line: str, line_number: int) -> None:
        """Parse one non-empty, non-comment line."""
        if line.startswith("nb_drones"):
            if self._seen_nb_drones:
                raise ValueError("nb_drones can only be defined once")
            self._parse_nb_drones(line)
            self._seen_nb_drones = True
            return

        if line.startswith("connection"):
            self._parse_connection(line)
            return

        self._parse_zone(line)

    def _parse_nb_drones(self, line: str) -> None:
        """Parse the number of drones."""
        parts = line.split(":", 1)

        if len(parts) != 2 or parts[0].strip() != "nb_drones":
            raise ValueError("invalid nb_drones syntax")

        value = parts[1].strip()

        if not value or not self.INTEGER_PATTERN.fullmatch(value):
            raise ValueError("nb_drones must be a positive integer")

        nb_drones = int(value)

        if nb_drones <= 0:
            raise ValueError("nb_drones must be a positive integer")

        if nb_drones > self.MAX_DRONES:
            raise ValueError("nb_drones cannot exceed 100")

        self.graph.nb_drones = nb_drones

    def _parse_zone(self, line: str) -> None:
        """Parse a zone definition."""
        if ":" not in line:
            raise ValueError("missing ':' in zone definition")

        left, right = line.split(":", 1)

        try:
            hub_type = HubType(left.strip())
        except ValueError as error:
            raise ValueError(
                f"invalid zone type '{left.strip()}'"
            ) from error

        zone_data, options = self._split_metadata(right)

        parts = zone_data.strip().split()

        if len(parts) != 3:
            raise ValueError("zone must contain exactly: <name> <x> <y>")

        name, x_value, y_value = parts

        self._validate_zone_name(name)

        x = self._parse_integer(x_value, "x coordinate")
        y = self._parse_integer(y_value, "y coordinate")

        if not self.MIN_COORDINATE <= x <= self.MAX_COORDINATE:
            raise ValueError("x coordinate must be between -50 and 50")

        if not self.MIN_COORDINATE <= y <= self.MAX_COORDINATE:
            raise ValueError("y coordinate must be between -50 and 50")

        zone = Zone(name=name, hub_type=hub_type, x=x, y=y)

        self._parse_zone_options(zone, options)

        if hub_type == HubType.START:
            self._start_count += 1

        if hub_type == HubType.END:
            self._end_count += 1

        self._validate_coordinates(x, y)
        self.graph.add_zone(zone)

    def _parse_connection(self, line: str) -> None:
        """Parse a connection definition."""
        if ":" not in line:
            raise ValueError("missing ':' in connection definition")

        left, right = line.split(":", 1)

        if left.strip() != "connection":
            raise ValueError("invalid connection syntax")

        zone_data, options = self._split_metadata(right)

        parts = zone_data.strip().split("-")

        if len(parts) != 2:
            raise ValueError("connection must use: <zone1>-<zone2>")

        start_name, end_name = (part.strip() for part in parts)

        if not start_name or not end_name:
            raise ValueError("connection contains an empty zone name")

        if start_name == end_name:
            raise ValueError("a zone cannot be connected to itself")

        if not self.graph.has_zone(start_name):
            raise ValueError(f"unknown zone '{start_name}'")

        if not self.graph.has_zone(end_name):
            raise ValueError(f"unknown zone '{end_name}'")

        key = (min(start_name, end_name), max(start_name, end_name))

        if key in self._connection_keys:
            raise ValueError(
                f"duplicate connection '{start_name}-{end_name}'"
            )

        start_zone = self.graph.get_zone(start_name)
        end_zone = self.graph.get_zone(end_name)

        connection = Connection(start_zone, end_zone)

        self._parse_connection_options(connection, options)

        self.graph.add_connection(connection)

        start_zone.add_neighbor(end_zone)
        end_zone.add_neighbor(start_zone)

        self._connection_keys.add(key)

    def _split_metadata(self, text: str) -> tuple[str, str]:
        """Split map data from its optional metadata block."""
        text = text.strip()

        if "[" not in text:
            return text, ""

        if "]" not in text:
            raise ValueError("metadata block is not closed")

        if text.count("[") != 1 or text.count("]") != 1:
            raise ValueError("invalid metadata block")

        data, metadata = text.split("[", 1)

        parts = metadata.rsplit("]", 1)

        if len(parts) != 2 or parts[1].strip():
            raise ValueError("invalid metadata block")

        return data.strip(), parts[0].strip()

    def _parse_zone_options(
        self,
        zone: Zone,
        options: str,
    ) -> None:
        """Parse zone metadata."""
        if not options:
            return

        seen_keys: set[str] = set()

        for part in options.split():
            if "=" not in part:
                raise ValueError(f"invalid zone option '{part}'")

            key, value = part.split("=", 1)

            if not key or not value:
                raise ValueError(f"invalid zone option '{part}'")

            if key in seen_keys:
                raise ValueError(f"duplicate zone option '{key}'")

            seen_keys.add(key)

            if key == "color":
                zone.color = value

            elif key == "zone":
                try:
                    zone.zone_type = ZoneType(value)
                except ValueError as error:
                    raise ValueError(
                        f"invalid zone type '{value}'"
                    ) from error

            elif key == "max_drones":
                if zone.hub_type in (HubType.START, HubType.END):
                    continue

                capacity = self._parse_integer(value, "max_drones")

                if capacity <= 0:
                    raise ValueError("max_drones must be positive")

                zone.max_drones = capacity

            else:
                raise ValueError(f"unknown zone option '{key}'")

    def _parse_connection_options(
        self,
        connection: Connection,
        options: str,
    ) -> None:
        """Parse connection metadata."""
        if not options:
            return

        seen_keys: set[str] = set()

        for part in options.split():
            if "=" not in part:
                raise ValueError(f"invalid connection option '{part}'")

            key, value = part.split("=", 1)

            if not key or not value:
                raise ValueError(f"invalid connection option '{part}'")

            if key in seen_keys:
                raise ValueError(f"duplicate connection option '{key}'")

            seen_keys.add(key)

            if key == "max_link_capacity":
                capacity = self._parse_integer(
                    value,
                    "max_link_capacity",
                )

                if capacity <= 0:
                    raise ValueError("max_link_capacity must be positive")

                connection.max_link_capacity = capacity

            else:
                raise ValueError(f"unknown connection option '{key}'")

    def _validate_zone_name(self, name: str) -> None:
        """Validate a zone name."""
        if not self.ZONE_NAME_PATTERN.fullmatch(name):
            raise ValueError(f"invalid zone name '{name}'")

    def _validate_coordinates(self, x: int, y: int) -> None:
        """Validate that zone coordinates are unique."""
        for zone in self.graph.zones.values():
            if zone.x == x and zone.y == y:
                raise ValueError(f"duplicate coordinates ({x}, {y})")

    def _parse_integer(
        self,
        value: str,
        field_name: str,
    ) -> int:
        """Parse an integer value."""
        if not self.INTEGER_PATTERN.fullmatch(value):
            raise ValueError(f"{field_name} must be an integer")

        return int(value)

    def _validate_graph(self) -> None:
        """Validate global map constraints."""
        if not self._seen_nb_drones:
            raise ValueError("missing nb_drones definition")

        if self._start_count != 1:
            raise ValueError(
                f"expected exactly one start_hub, found {self._start_count}"
            )

        if self._end_count != 1:
            raise ValueError(
                f"expected exactly one end_hub, found {self._end_count}"
            )
