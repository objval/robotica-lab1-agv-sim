from __future__ import annotations

import math
from typing import Dict

from agv_sim.simulation import AGVSimulation


_COLOR_MAP: Dict[str, str] = {
    "red": "red",
    "blue": "blue",
    "green": "green",
    "orange": "orange",
    "purple": "purple",
    "brown": "brown",
    "gray": "gray",
}


def _vp_color(name: str):
    """Resolve a string colour name to a VPython colour object."""
    from vpython import color  # type: ignore[import-untyped]

    mapping = {
        "red": color.red,
        "blue": color.blue,
        "green": color.green,
        "orange": color.orange,
        "purple": color.purple,
        "brown": color.brown,
        "gray": color.gray(0.5),
    }
    return mapping.get(name, color.white)


class VPythonVisualizer:
    """Real-time Visual Python 3-D animation for the AGV simulation.

    This satisfies the *Visual Python* topic explicitly listed in Lab #1.
    """

    def __init__(self, sim: AGVSimulation) -> None:
        from vpython import (  # type: ignore[import-untyped]
            box,
            canvas,
            color,
            curve,
            cylinder,
            ring,
            vector,
        )

        self.sim = sim
        cfg = sim.config
        w, h = cfg.width, cfg.height

        self.scene = canvas(
            title="INFO1167 AGV Lab #1 — Visual Python",
            width=900,
            height=700,
        )
        self.scene.background = color.white
        # Top-down orthographic-style view
        self.scene.camera.pos = vector(w / 2, max(w, h) * 1.2, h / 2)
        self.scene.camera.axis = vector(0, -max(w, h) * 1.2, 0)

        # Warehouse grid
        self._grid_lines: list = []
        for x in range(w + 1):
            self._grid_lines.append(
                curve(
                    pos=[vector(x, 0, 0), vector(x, 0, h)],
                    color=color.gray(0.7),
                    radius=0.02,
                )
            )
        for y in range(h + 1):
            self._grid_lines.append(
                curve(
                    pos=[vector(0, 0, y), vector(w, 0, y)],
                    color=color.gray(0.7),
                    radius=0.02,
                )
            )

        # Floor plane
        box(
            pos=vector(w / 2, -0.05, h / 2),
            size=vector(w, 0.1, h),
            color=color.gray(0.95),
        )

        self.robot_objs: Dict[int, object] = {}
        self.dir_objs: Dict[int, object] = {}
        self.base_objs: Dict[int, object] = {}
        self.cart_objs: Dict[int, object] = {}
        self.dest_objs: Dict[int, object] = {}

        for r in sim.robots:
            # Base marker (faint pillar)
            self.base_objs[r.id] = cylinder(
                pos=vector(r.base[0], 0.01, r.base[1]),
                axis=vector(0, 0.3, 0),
                radius=0.35,
                color=_vp_color(r.color),
                opacity=0.3,
            )
            # Robot body
            self.robot_objs[r.id] = cylinder(
                pos=vector(r.node[0], 0.2, r.node[1]),
                axis=vector(0, 0.4, 0),
                radius=0.25,
                color=_vp_color(r.color),
            )
            # Direction arrow (geometry evidence: heading vector)
            self.dir_objs[r.id] = cylinder(
                pos=vector(r.node[0], 0.35, r.node[1]),
                axis=vector(0.3, 0, 0),
                radius=0.04,
                color=color.black,
            )

        for c in sim.carts:
            self.cart_objs[c.id] = box(
                pos=vector(c.node[0], 0.15, c.node[1]),
                size=vector(0.35, 0.3, 0.35),
                color=_vp_color(c.base_color),
            )
            self.dest_objs[c.id] = ring(
                pos=vector(c.destination[0], 0.01, c.destination[1]),
                axis=vector(0, 1, 0),
                radius=0.3,
                thickness=0.05,
                color=color.black,
            )

    def update(self) -> None:
        """Refresh object positions / colours to match the current simulation state."""
        from vpython import vector  # type: ignore[import-untyped]

        for r in self.sim.robots:
            self.robot_objs[r.id].pos = vector(r.node[0], 0.2, r.node[1])

            # Geometry: rotate heading indicator by orientation_deg
            rad = math.radians(r.orientation_deg)
            self.dir_objs[r.id].pos = vector(r.node[0], 0.35, r.node[1])
            self.dir_objs[r.id].axis = vector(
                math.cos(rad) * 0.4, 0, math.sin(rad) * 0.4
            )

        for c in self.sim.carts:
            self.cart_objs[c.id].pos = vector(c.node[0], 0.15, c.node[1])
            self.cart_objs[c.id].color = _vp_color(c.base_color)
            self.dest_objs[c.id].pos = vector(
                c.destination[0], 0.01, c.destination[1]
            )

    def animate(self, ticks: int | None = None, rate_hz: int = 10) -> None:
        """Run the simulation forward while animating in VPython."""
        from vpython import rate  # type: ignore[import-untyped]

        limit = ticks if ticks is not None else self.sim.config.max_ticks
        for _ in range(limit):
            rate(rate_hz)
            self.sim.step()
            self.update()
