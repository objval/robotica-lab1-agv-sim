from __future__ import annotations

import math
import random
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple

import networkx as nx

from .graph_utils import bfs_path, create_grid_graph, dfs_any_path, dijkstra_path
from .models import Cart, Node, Robot, RobotState, SimulationConfig


class AGVSimulation:
    """State-machine AGV simulation satisfying INFO1167 Lab #1 constraints."""

    COLORS = ["red", "blue", "green", "orange", "purple", "brown"]

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.rng = random.Random(self.config.seed)
        self.graph: nx.Graph = create_grid_graph(self.config.width, self.config.height)
        self.robots: List[Robot] = []
        self.carts: List[Cart] = []
        self.ticks: int = 0
        self.events: List[str] = []
        self._init_entities()

    def _init_entities(self) -> None:
        corner_bases = [
            (0, 0),
            (self.config.width - 1, 0),
            (0, self.config.height - 1),
            (self.config.width - 1, self.config.height - 1),
        ]
        bases = corner_bases[: self.config.n_robots]
        for i in range(self.config.n_robots):
            base = bases[i % len(bases)]
            self.robots.append(
                Robot(id=i, color=self.COLORS[i], base=base, node=base)
            )

        occupied = {r.base for r in self.robots}
        for i in range(self.config.n_carts):
            node = self._random_node(exclude=occupied)
            occupied.add(node)
            destination = self._random_node(exclude=occupied)
            self.carts.append(
                Cart(id=i, base_color="gray", node=node, destination=destination)
            )

    def _random_node(self, exclude: set[Node]) -> Node:
        while True:
            n = (self.rng.randrange(self.config.width), self.rng.randrange(self.config.height))
            if n not in exclude:
                return n

    def _normalize_angle(self, angle: float) -> float:
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    def _desired_heading(self, current: Node, nxt: Node) -> float:
        dx = nxt[0] - current[0]
        dy = nxt[1] - current[1]
        return math.degrees(math.atan2(dy, dx))

    def _rotate_then_move(self, robot: Robot) -> bool:
        """Returns True if robot moved one node this tick."""
        if len(robot.path) <= 1:
            return False
        target = robot.path[1]
        desired = self._desired_heading(robot.node, target)
        delta = self._normalize_angle(desired - robot.orientation_deg)
        step = self.config.rotation_step_deg
        if abs(delta) > step:
            robot.orientation_deg = self._normalize_angle(robot.orientation_deg + (step if delta > 0 else -step))
            return False

        robot.orientation_deg = desired
        robot.node = target
        robot.path = robot.path[1:]
        robot.battery = max(0.0, robot.battery - self.config.battery_drain_per_move)
        return True

    def _shortest_path(self, src: Node, dst: Node) -> List[Node]:
        return dijkstra_path(self.graph, src, dst)

    def _allocate_idle_robots(self) -> None:
        free_carts = [c for c in self.carts if c.assigned_robot_id is None]
        self.rng.shuffle(free_carts)

        for r in self.robots:
            if r.state not in {RobotState.IDLE_AT_BASE, RobotState.CHARGING}:
                continue
            if r.state == RobotState.CHARGING and r.battery < 100.0:
                continue
            if r.assigned_cart_id is not None:
                continue
            if not free_carts:
                break

            cart = free_carts.pop()
            cart.assigned_robot_id = r.id
            cart.base_color = r.color  # assignment color coupling (lab requirement)
            r.assigned_cart_id = cart.id
            r.state = RobotState.TO_CART
            r.path = self._shortest_path(r.node, cart.node)
            self.events.append(f"tick={self.ticks}: robot {r.id} assigned cart {cart.id}")

    def _cart_by_id(self, cart_id: int) -> Cart:
        return next(c for c in self.carts if c.id == cart_id)

    def _step_robot(self, r: Robot) -> None:
        if r.state == RobotState.CHARGING:
            r.battery = min(100.0, r.battery + self.config.battery_charge_per_tick)
            if r.battery >= 100.0:
                r.state = RobotState.IDLE_AT_BASE
            return

        if r.state == RobotState.IDLE_AT_BASE:
            return

        moved = self._rotate_then_move(r)

        if r.state == RobotState.TO_CART:
            cart = self._cart_by_id(r.assigned_cart_id)
            if r.node == cart.node:
                r.state = RobotState.TO_DESTINATION
                r.path = self._shortest_path(r.node, cart.destination)
                self.events.append(f"tick={self.ticks}: robot {r.id} picked cart {cart.id}")

        elif r.state == RobotState.TO_DESTINATION:
            cart = self._cart_by_id(r.assigned_cart_id)
            cart.node = r.node  # carried with robot
            if r.node == cart.destination:
                cart.delivered_count += 1
                r.completed_deliveries += 1
                self.events.append(f"tick={self.ticks}: robot {r.id} delivered cart {cart.id}")

                # Reset cart for next cycle (random new pickup+dropoff)
                occupied = {rb.node for rb in self.robots}
                cart.node = self._random_node(exclude=occupied)
                cart.destination = self._random_node(exclude=occupied | {cart.node})
                cart.assigned_robot_id = None
                cart.base_color = "gray"  # reset to original color after release

                r.assigned_cart_id = None
                r.state = RobotState.RETURN_TO_BASE
                r.path = self._shortest_path(r.node, r.base)

        elif r.state == RobotState.RETURN_TO_BASE:
            if r.node == r.base:
                r.state = RobotState.CHARGING

    def step(self) -> None:
        self._allocate_idle_robots()
        for r in self.robots:
            self._step_robot(r)
        self.ticks += 1

    def run(self, ticks: Optional[int] = None) -> Dict:
        limit = ticks if ticks is not None else self.config.max_ticks
        for _ in range(limit):
            self.step()
        return self.summary()

    def summary(self) -> Dict:
        return {
            "ticks": self.ticks,
            "robots": [asdict(r) for r in self.robots],
            "carts": [asdict(c) for c in self.carts],
            "total_deliveries": sum(r.completed_deliveries for r in self.robots),
            "events_tail": self.events[-20:],
            "graph_examples": {
                "bfs_example": bfs_path(self.graph, (0, 0), (self.config.width - 1, self.config.height - 1))[:8],
                "dijkstra_example": dijkstra_path(self.graph, (0, 0), (self.config.width - 1, self.config.height - 1))[:8],
                "dfs_example": dfs_any_path(self.graph, (0, 0), (self.config.width - 1, self.config.height - 1))[:8],
            },
        }
