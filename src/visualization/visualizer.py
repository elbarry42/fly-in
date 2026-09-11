import pygame

from ..simulation.simulation import Simulation
from ..models.zone import HubType, ZoneType, Zone


class Visualizer:
    """Display the Fly-in simulation graph."""

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    FPS = 60

    BACKGROUND = (25, 25, 30)
    CONNECTION_COLOR = (120, 120, 120)
    ZONE_COLOR = (70, 70, 80)
    START_COLOR = (50, 180, 80)
    END_COLOR = (180, 60, 60)
    PRIORITY_COLOR = (220, 180, 50)
    RESTRICTED_COLOR = (180, 100, 220)
    BLOCKED_COLOR = (60, 60, 60)
    TEXT_COLOR = (230, 230, 230)

    ZONE_RADIUS = 25
    MARGIN = 100

    def __init__(self, simulation: Simulation):
        self.simulation = simulation
        self.graph = simulation.graph

        pygame.init()

        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Fly-in")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)

        self.running = True

        self.positions = self._calculate_positions()

    def run(self) -> None:
        """Run the graphical interface."""
        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(self.FPS)

        pygame.quit()

    def _handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _calculate_positions(
        self,
    ) -> dict[str, tuple[int, int]]:
        """Convert map coordinates to screen coordinates."""
        if not self.graph.zones:
            return {}

        min_x = min(zone.x for zone in self.graph.zones.values())
        max_x = max(zone.x for zone in self.graph.zones.values())
        min_y = min(zone.y for zone in self.graph.zones.values())
        max_y = max(zone.y for zone in self.graph.zones.values())

        width = max_x - min_x
        height = max_y - min_y

        available_width = (
            self.WINDOW_WIDTH - 2 * self.MARGIN
        )
        available_height = (
            self.WINDOW_HEIGHT - 2 * self.MARGIN
        )

        scale_x = (
            available_width / width
            if width > 0
            else 1
        )
        scale_y = (
            available_height / height
            if height > 0
            else 1
        )

        scale = min(scale_x, scale_y)

        positions: dict[str, tuple[int, int]] = {}

        for zone in self.graph.zones.values():
            screen_x = int(
                self.MARGIN
                + (zone.x - min_x) * scale
            )

            screen_y = int(
                self.MARGIN
                + (max_y - zone.y) * scale
            )

            positions[zone.name] = (
                screen_x,
                screen_y,
            )

        return positions

    def _draw(self) -> None:
        """Draw the current graphical state."""
        self.screen.fill(self.BACKGROUND)

        self._draw_title()
        self._draw_connections()
        self._draw_zones()

        pygame.display.flip()

    def _draw_title(self) -> None:
        """Draw the application title."""
        title = self.title_font.render(
            "FLY-IN",
            True,
            self.TEXT_COLOR,
        )

        self.screen.blit(
            title,
            (20, 20),
        )

    def _draw_connections(self) -> None:
        """Draw all graph connections."""
        for connection in self.graph.connections:
            start = self.positions[connection.start.name]
            end = self.positions[connection.end.name]

            pygame.draw.line(
                self.screen,
                self.CONNECTION_COLOR,
                start,
                end,
                3,
            )

    def _draw_zones(self) -> None:
        """Draw all graph zones."""
        for zone in self.graph.zones.values():
            position = self.positions[zone.name]
            color = self._get_zone_color(zone)

            pygame.draw.circle(
                self.screen,
                color,
                position,
                self.ZONE_RADIUS,
            )

            pygame.draw.circle(
                self.screen,
                self.TEXT_COLOR,
                position,
                self.ZONE_RADIUS,
                2,
            )

            self._draw_zone_name(
                zone.name,
                position,
            )

    def _get_zone_color(self, zone: Zone) -> tuple[int, int, int]:
        """Return the display color for a zone."""
        if zone.hub_type == HubType.START:
            return self.START_COLOR

        if zone.hub_type == HubType.END:
            return self.END_COLOR

        if zone.zone_type == ZoneType.PRIORITY:
            return self.PRIORITY_COLOR

        if zone.zone_type == ZoneType.RESTRICTED:
            return self.RESTRICTED_COLOR

        if zone.zone_type == ZoneType.BLOCKED:
            return self.BLOCKED_COLOR

        return self.ZONE_COLOR

    def _draw_zone_name(
        self,
        name: str,
        position: tuple[int, int],
    ) -> None:
        """Draw a zone name below its node."""
        text = self.font.render(
            name,
            True,
            self.TEXT_COLOR,
        )

        text_rect = text.get_rect(
            center=(
                position[0],
                position[1] + self.ZONE_RADIUS + 15,
            )
        )

        self.screen.blit(
            text,
            text_rect,
        )
