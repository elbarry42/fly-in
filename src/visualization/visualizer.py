import pygame

from ..models.zone import HubType, Zone, ZoneType
from ..simulation.simulation import Simulation
from ..models.connection import Connection


class Visualizer:
    """Display and control the Fly-in simulation."""

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    FPS = 60

    BACKGROUND = (25, 25, 30)
    CONNECTION_COLOR = (100, 100, 110)
    TEXT_COLOR = (235, 235, 235)
    BUTTON_COLOR = (55, 55, 65)
    BUTTON_HOVER_COLOR = (75, 75, 90)
    BUTTON_BORDER_COLOR = (150, 150, 160)

    ZONE_RADIUS = 25
    DRONE_RADIUS = 12

    MARGIN_X = 100
    MARGIN_Y = 150

    BUTTON_WIDTH = 140
    BUTTON_HEIGHT = 40
    BUTTON_GAP = 15

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
        self.button_font = pygame.font.Font(None, 22)

        self.running = True

        # Current displayed simulation turn.
        self.current_turn = 0

        # Animation between two simulation turns.
        self.animation_progress = 0.0
        self.animation_duration = 0.8

        # Automatic playback.
        self.playing = False
        self.pause_requested = False

        self.hovered_zone: Zone | None = None
        self.hovered_connection: Connection | None = None
        self.selected_zone: Zone | None = None
        self.selected_connection: Connection | None = None

        self.positions = self._calculate_positions()

        self.previous_button = pygame.Rect(
            300,
            720,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )

        self.next_button = pygame.Rect(
            455,
            720,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )

        self.play_button = pygame.Rect(
            610,
            720,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )

        self.reset_button = pygame.Rect(
            765,
            720,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT,
        )

    def run(self) -> None:
        """Run the graphical interface."""
        while self.running:
            delta_time = self.clock.tick(self.FPS) / 1000.0

            self._handle_events()
            self._update(delta_time)
            self._draw()

        pygame.quit()

    def _handle_events(self) -> None:
        """Handle keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_mouse_click(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_mouse_click(event.pos)

    def _handle_mouse_motion(
        self,
        position: tuple[int, int],
    ) -> None:
        """Update the object currently under the mouse."""
        self.hovered_zone = self._find_zone_at(position)

        if self.hovered_zone is not None:
            self.hovered_connection = None
            return

        self.hovered_connection = self._find_connection_at(
            position
        )

    def _handle_keyboard(self, key: int) -> None:
        """Handle keyboard controls."""
        if key == pygame.K_RIGHT:
            self._next_turn()

        elif key == pygame.K_LEFT:
            self._previous_turn()

        elif key == pygame.K_SPACE:
            self._toggle_play()

        elif key == pygame.K_r:
            self._reset()

        elif key == pygame.K_ESCAPE:
            self.running = False

    def _handle_mouse_click(
        self,
        position: tuple[int, int],
    ) -> None:
        """Handle clicks on controls and graph objects."""
        if self.previous_button.collidepoint(position):
            self._previous_turn()
            return

        if self.next_button.collidepoint(position):
            self._next_turn()
            return

        if self.play_button.collidepoint(position):
            self._toggle_play()
            return

        if self.reset_button.collidepoint(position):
            self._reset()
            return

        zone = self._find_zone_at(position)

        if zone is not None:
            self.selected_zone = zone
            self.selected_connection = None
            return

        connection = self._find_connection_at(position)

        if connection is not None:
            self.selected_connection = connection
            self.selected_zone = None
            return

        self.selected_zone = None
        self.selected_connection = None

    def _find_zone_at(
        self,
        position: tuple[int, int],
    ) -> Zone | None:
        """Return the zone under the mouse."""
        mouse_x, mouse_y = position

        for zone in self.graph.zones.values():
            zone_x, zone_y = self.positions[zone.name]

            dx = mouse_x - zone_x
            dy = mouse_y - zone_y

            distance_squared = dx * dx + dy * dy

            if distance_squared <= self.ZONE_RADIUS ** 2:
                return zone

        return None

    def _find_connection_at(
        self,
        position: tuple[int, int],
    ) -> Connection | None:
        """Return the connection under the mouse."""
        for connection in self.graph.connections:
            start = self.positions[connection.start.name]
            end = self.positions[connection.end.name]

            distance = self._point_to_segment_distance(
                position,
                start,
                end,
            )

            if distance <= 8:
                return connection

        return None

    def _point_to_segment_distance(
        self,
        point: tuple[int, int],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> float:
        """Calculate the distance from a point to a segment."""
        px, py = point
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        length_squared = dx * dx + dy * dy

        if length_squared == 0:
            distance_x = px - x1
            distance_y = py - y1

            return (
                distance_x * distance_x
                + distance_y * distance_y
            ) ** 0.5

        projection = (
            (px - x1) * dx
            + (py - y1) * dy
        ) / length_squared

        projection = max(
            0.0,
            min(1.0, projection),
        )

        closest_x = x1 + projection * dx
        closest_y = y1 + projection * dy

        distance_x = px - closest_x
        distance_y = py - closest_y

        return (
            distance_x * distance_x
            + distance_y * distance_y
        ) ** 0.5

    def _next_turn(self) -> None:
        """Display the next simulation turn immediately."""
        if self.current_turn >= self.simulation.turn:
            return

        self.playing = False
        self.pause_requested = False
        self.current_turn += 1
        self.animation_progress = 1.0

    def _previous_turn(self) -> None:
        """Display the previous simulation turn immediately."""
        if self.current_turn <= 0:
            return

        self.playing = False
        self.pause_requested = False
        self.current_turn -= 1
        self.animation_progress = 1.0

    def _toggle_play(self) -> None:
        """Start or pause automatic playback."""
        if self.playing:
            self.pause_requested = True
            return

        if self.current_turn >= self.simulation.turn:
            return

        self.pause_requested = False
        self.playing = True
        self.animation_progress = 0.0

    def _reset(self) -> None:
        """Reset the visualizer to the initial state."""
        self.current_turn = 0
        self.animation_progress = 1.0
        self.playing = False
        self.pause_requested = False

    def _update(self, delta_time: float) -> None:
        """Update automatic animation between simulation turns."""
        if not self.playing:
            return

        if self.current_turn >= self.simulation.turn:
            self.playing = False
            self.pause_requested = False
            self.animation_progress = 1.0
            return

        self.animation_progress += (
            delta_time / self.animation_duration
        )

        if self.animation_progress < 1.0:
            return

        self.animation_progress = 1.0
        self.current_turn += 1

        if self.pause_requested:
            self.playing = False
            self.pause_requested = False
            return

        if self.current_turn >= self.simulation.turn:
            self.playing = False
            return

        self.animation_progress = 0.0

    def _calculate_positions(
        self,
    ) -> dict[str, tuple[int, int]]:
        """Calculate screen positions from map coordinates."""
        if not self.graph.zones:
            return {}

        zones = list(self.graph.zones.values())

        min_x = min(zone.x for zone in zones)
        max_x = max(zone.x for zone in zones)
        min_y = min(zone.y for zone in zones)
        max_y = max(zone.y for zone in zones)

        coordinate_width = max_x - min_x
        coordinate_height = max_y - min_y

        available_width = self.WINDOW_WIDTH - 2 * self.MARGIN_X
        available_height = (
            self.WINDOW_HEIGHT
            - self.MARGIN_Y
            - 150
        )

        if coordinate_width > 0:
            scale_x = available_width / coordinate_width
        else:
            scale_x = 1.0

        if coordinate_height > 0:
            scale_y = available_height / coordinate_height
        else:
            scale_y = 1.0

        if coordinate_width > 0 and coordinate_height > 0:
            scale = min(scale_x, scale_y)
        elif coordinate_width > 0:
            scale = scale_x
        elif coordinate_height > 0:
            scale = scale_y
        else:
            scale = 1.0

        map_width = coordinate_width * scale
        map_height = coordinate_height * scale

        offset_x = (
            self.WINDOW_WIDTH - map_width
        ) / 2

        offset_y = (
            self.WINDOW_HEIGHT - map_height
        ) / 2

        positions: dict[str, tuple[int, int]] = {}

        for zone in zones:
            screen_x = int(
                offset_x
                + (zone.x - min_x) * scale
            )

            screen_y = int(
                offset_y
                + (max_y - zone.y) * scale
            )

            positions[zone.name] = (
                screen_x,
                screen_y,
            )

        return positions

    def _draw(self) -> None:
        """Draw the complete interface."""
        self.screen.fill(self.BACKGROUND)

        self._draw_title()
        self._draw_connections()
        self._draw_zones()
        self._draw_drones()
        self._draw_controls()
        self._draw_information_panel()

        pygame.display.flip()

    def _draw_information_panel(self) -> None:
        """Draw information about the selected or hovered object."""
        zone = (
            self.selected_zone
            if self.selected_zone is not None
            else self.hovered_zone
        )

        connection = (
            self.selected_connection
            if self.selected_connection is not None
            else self.hovered_connection
        )

        if zone is not None:
            self._draw_zone_information(zone)
        elif connection is not None:
            self._draw_connection_information(connection)

    def _draw_zone_information(
        self,
        zone: Zone,
    ) -> None:
        """Display information about a zone."""
        panel = pygame.Rect(
            self.WINDOW_WIDTH - 280,
            20,
            250,
            150,
        )

        pygame.draw.rect(
            self.screen,
            (45, 45, 55),
            panel,
            border_radius=10,
        )

        pygame.draw.rect(
            self.screen,
            self.TEXT_COLOR,
            panel,
            width=2,
            border_radius=10,
        )

        lines = [
            zone.name,
            f"Type: {zone.zone_type.value}",
            f"Capacity: {zone.max_drones}",
            f"Drones: {zone.current_drones}",
        ]

        self._draw_information_lines(lines, panel)

    def _draw_connection_information(
        self,
        connection: Connection,
    ) -> None:
        """Display information about a connection."""
        panel = pygame.Rect(
            self.WINDOW_WIDTH - 300,
            20,
            270,
            150,
        )

        pygame.draw.rect(
            self.screen,
            (45, 45, 55),
            panel,
            border_radius=10,
        )

        pygame.draw.rect(
            self.screen,
            self.TEXT_COLOR,
            panel,
            width=2,
            border_radius=10,
        )

        lines = [
            "Connection",
            (
                f"{connection.start.name} "
                f"<-> {connection.end.name}"
            ),
            f"Capacity: {connection.max_link_capacity}",
            f"In transit: {connection.current_drones}",
        ]

        self._draw_information_lines(lines, panel)

    def _draw_information_lines(
        self,
        lines: list[str],
        panel: pygame.Rect,
    ) -> None:
        """Draw information lines inside a panel."""
        y = panel.top + 15

        for index, line in enumerate(lines):
            font = (
                self.title_font
                if index == 0
                else self.font
            )

            text = font.render(
                line,
                True,
                self.TEXT_COLOR,
            )

            self.screen.blit(
                text,
                (panel.left + 15, y),
            )

            y += 35 if index == 0 else 25

    def _draw_title(self) -> None:
        """Draw the title and current turn."""
        title = self.title_font.render(
            "FLY-IN",
            True,
            self.TEXT_COLOR,
        )

        self.screen.blit(title, (25, 20))

        turn_text = self.font.render(
            (
                f"Turn {self.current_turn} / "
                f"{self.simulation.turn}"
            ),
            True,
            self.TEXT_COLOR,
        )

        self.screen.blit(turn_text, (25, 60))

    def _draw_connections(self) -> None:
        """Draw all graph connections."""
        for connection in self.graph.connections:
            start = self.positions[connection.start.name]
            end = self.positions[connection.end.name]

            if (
                connection == self.hovered_connection
                or connection == self.selected_connection
            ):
                pygame.draw.line(
                    self.screen,
                    (240, 240, 240),
                    start,
                    end,
                    7,
                )
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

            if (
                zone == self.hovered_zone
                or zone == self.selected_zone
            ):
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    position,
                    self.ZONE_RADIUS + 6,
                    3,
                )
            pygame.draw.circle(
                self.screen,
                self._get_zone_color(zone),
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

    def _get_zone_color(
        self,
        zone: Zone,
    ) -> tuple[int, int, int]:
        """Return the display color for a zone."""
        if zone.color is not None:
            return self._parse_color(zone.color)

        if zone.hub_type == HubType.START:
            return (50, 180, 80)

        if zone.hub_type == HubType.END:
            return (180, 60, 60)

        if zone.zone_type == ZoneType.PRIORITY:
            return (220, 180, 50)

        if zone.zone_type == ZoneType.RESTRICTED:
            return (180, 100, 220)

        if zone.zone_type == ZoneType.BLOCKED:
            return (60, 60, 60)

        return (70, 70, 80)

    def _parse_color(
        self,
        color: str,
    ) -> tuple[int, int, int]:
        """Convert a map color into RGB."""
        colors = {
            "red": (200, 60, 60),
            "green": (50, 180, 80),
            "blue": (60, 100, 200),
            "yellow": (220, 190, 50),
            "gray": (100, 100, 100),
            "grey": (100, 100, 100),
            "purple": (170, 90, 190),
            "orange": (220, 130, 50),
            "white": (230, 230, 230),
            "black": (20, 20, 20),
        }

        return colors.get(
            color.lower(),
            (100, 100, 100),
        )

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

        self.screen.blit(text, text_rect)

    def _draw_drones(self) -> None:
        """Draw drones at their current or interpolated positions."""
        snapshot = self.simulation.get_snapshot(
            self.current_turn
        )

        if self.current_turn == 0:
            previous_snapshot = snapshot
        else:
            previous_snapshot = self.simulation.get_snapshot(
                self.current_turn - 1
            )

        previous_states = {
            state[0]: state
            for state in previous_snapshot
        }

        for state in snapshot:
            drone_id = state[0]
            current_zone_name = state[1]
            destination_name = state[4]

            previous_state = previous_states.get(drone_id)

            if previous_state is None:
                continue

            previous_zone_name = previous_state[1]

            if self.current_turn == 0:
                start_name = current_zone_name
                end_name = current_zone_name

            elif destination_name is not None:
                # Restricted transit:
                # the drone starts from its current zone
                # and moves along the connection.
                start_name = current_zone_name
                end_name = destination_name

            else:
                # Normal movement:
                # interpolate between the previous and
                # current simulation zones.
                start_name = previous_zone_name
                end_name = current_zone_name

            start_position = self.positions.get(start_name)
            end_position = self.positions.get(end_name)

            if start_position is None or end_position is None:
                continue

            progress = self.animation_progress

            x = int(
                start_position[0]
                + (
                    end_position[0]
                    - start_position[0]
                ) * progress
            )

            y = int(
                start_position[1]
                + (
                    end_position[1]
                    - start_position[1]
                ) * progress
            )

            self._draw_drone(
                drone_id,
                (x, y),
            )

    def _draw_drone(
        self,
        drone_id: int,
        position: tuple[int, int],
    ) -> None:
        """Draw one drone."""
        pygame.draw.circle(
            self.screen,
            (245, 245, 245),
            position,
            self.DRONE_RADIUS,
        )

        pygame.draw.circle(
            self.screen,
            (30, 30, 30),
            position,
            self.DRONE_RADIUS,
            2,
        )

        text = self.font.render(
            str(drone_id),
            True,
            (30, 30, 30),
        )

        text_rect = text.get_rect(
            center=position,
        )

        self.screen.blit(text, text_rect)

    def _draw_controls(self) -> None:
        """Draw simulation control buttons."""
        buttons = [
            (self.previous_button, "◀ Previous"),
            (self.next_button, "Next ▶"),
            (
                self.play_button,
                "Pause" if self.playing else "▶ Play",
            ),
            (self.reset_button, "↻ Reset"),
        ]

        mouse_position = pygame.mouse.get_pos()

        for rectangle, label in buttons:
            if rectangle.collidepoint(mouse_position):
                color = self.BUTTON_HOVER_COLOR
            else:
                color = self.BUTTON_COLOR

            pygame.draw.rect(
                self.screen,
                color,
                rectangle,
                border_radius=8,
            )

            pygame.draw.rect(
                self.screen,
                self.BUTTON_BORDER_COLOR,
                rectangle,
                width=2,
                border_radius=8,
            )

            text = self.button_font.render(
                label,
                True,
                self.TEXT_COLOR,
            )

            text_rect = text.get_rect(
                center=rectangle.center,
            )

            self.screen.blit(
                text,
                text_rect,
            )
