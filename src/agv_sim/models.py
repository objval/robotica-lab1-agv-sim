from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

Node = Tuple[int, int]


class RobotState(str, Enum):
    IDLE_AT_BASE = "idle_at_base"
    TO_CART = "to_cart"
    TO_DESTINATION = "to_destination"
    RETURN_TO_BASE = "return_to_base"
    CHARGING = "charging"


@dataclass
class Cart:
    id: int
    base_color: str
    node: Node
    destination: Node
    assigned_robot_id: Optional[int] = None
    delivered_count: int = 0


@dataclass
class Robot:
    id: int
    color: str
    base: Node
    node: Node
    orientation_deg: float = 0.0
    battery: float = 100.0
    state: RobotState = RobotState.IDLE_AT_BASE
    assigned_cart_id: Optional[int] = None
    path: List[Node] = field(default_factory=list)
    completed_deliveries: int = 0


@dataclass
class SimulationConfig:
    width: int = 10
    height: int = 8
    n_robots: int = 4
    n_carts: int = 4
    rotation_step_deg: float = 10.0
    battery_drain_per_move: float = 0.8
    battery_charge_per_tick: float = 5.0
    seed: int = 42
    max_ticks: int = 1500
