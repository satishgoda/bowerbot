# Copyright 2026 Binary Core LLC
# SPDX-License-Identifier: Apache-2.0

"""SceneGraphBuilder — the 'Engineer' layer.

Converts the LLM's semantic layout decisions into exact coordinates.
Pure deterministic math — no AI. The LLM says 'grid of 4 tables',
this module computes the actual positions.
"""

from dataclasses import dataclass

from bowerbot.schemas import PlacementCategory


@dataclass
class Placement:
    """A computed placement position."""

    translate: tuple[float, float, float]
    rotate: tuple[float, float, float] = (0.0, 0.0, 0.0)


class SceneGraphBuilder:
    """Computes spatial positions for objects in a scene.

    All coordinate math is here. The LLM never outputs a float —
    it describes relationships, and this class converts them to meters.
    """

    def __init__(
        self,
        room_bounds: tuple[float, float, float] = (10.0, 3.0, 8.0),
    ) -> None:
        self.room_width, self.room_height, self.room_depth = room_bounds

    def compute_placement(
        self,
        category: PlacementCategory,
        surface_height: float = 0.0,
    ) -> float:
        """Compute the Y position based on placement category."""
        match category:
            case PlacementCategory.FLOOR:
                return 0.0
            case PlacementCategory.SURFACE:
                return surface_height
            case PlacementCategory.CEILING:
                return self.room_height
            case PlacementCategory.WALL:
                return 0.0
            case _:
                return 0.0

    def suggest_grid_layout(
        self,
        count: int,
        spacing: float = 2.0,
        center: tuple[float, float] | None = None,
    ) -> list[Placement]:
        """Compute positions for N objects in a grid layout.

        Automatically determines rows/columns to fit the count,
        centered in the room or at the specified center point.
        """
        import math

        if count <= 0:
            return []

        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        cx = center[0] if center else self.room_width / 2
        cz = center[1] if center else self.room_depth / 2

        x_offset = cx - (cols - 1) * spacing / 2
        z_offset = cz - (rows - 1) * spacing / 2

        placements = []
        for i in range(count):
            row = i // cols
            col = i % cols
            x = x_offset + col * spacing
            z = z_offset + row * spacing
            placements.append(Placement(translate=(x, 0.0, z)))

        return placements

    def suggest_wall_layout(
        self,
        count: int,
        wall: str = "back",
        spacing: float = 2.0,
        wall_offset: float = 0.05,
    ) -> list[Placement]:
        """Place objects along a wall."""
        placements = []
        total_span = (count - 1) * spacing

        for i in range(count):
            offset_along = -total_span / 2 + i * spacing

            match wall:
                case "back":
                    x = self.room_width / 2 + offset_along
                    z = wall_offset
                    ry = 0.0
                case "front":
                    x = self.room_width / 2 + offset_along
                    z = self.room_depth - wall_offset
                    ry = 180.0
                case "left":
                    x = wall_offset
                    z = self.room_depth / 2 + offset_along
                    ry = 90.0
                case "right":
                    x = self.room_width - wall_offset
                    z = self.room_depth / 2 + offset_along
                    ry = -90.0
                case _:
                    x, z, ry = 0.0, 0.0, 0.0

            placements.append(Placement(translate=(x, 0.0, z), rotate=(0.0, ry, 0.0)))

        return placements

    def check_collision(
        self,
        pos_a: tuple[float, float, float],
        size_a: tuple[float, float, float],
        pos_b: tuple[float, float, float],
        size_b: tuple[float, float, float],
    ) -> bool:
        """Check if two axis-aligned bounding boxes overlap."""
        for i in range(3):
            half_a = size_a[i] / 2
            half_b = size_b[i] / 2
            if abs(pos_a[i] - pos_b[i]) >= (half_a + half_b):
                return False
        return True
