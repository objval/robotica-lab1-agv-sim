#!/usr/bin/env python3
"""Run the AGV simulation with a live Visual Python animation.

This is the entry-point for the *Visual Python* topic required by Lab #1.
"""
from __future__ import annotations

import argparse

from agv_sim.models import SimulationConfig
from agv_sim.simulation import AGVSimulation
from agv_sim.vpython_vis import VPythonVisualizer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run AGV Lab #1 simulation with Visual Python animation"
    )
    parser.add_argument("--ticks", type=int, default=600)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--width", type=int, default=10)
    parser.add_argument("--height", type=int, default=8)
    parser.add_argument(
        "--rate", type=int, default=10, help="VPython animation rate (Hz)"
    )
    parser.add_argument(
        "--routing-mode",
        type=str,
        default="random_shortest",
        choices=["random_shortest", "dijkstra", "bfs"],
    )
    args = parser.parse_args()

    config = SimulationConfig(
        seed=args.seed,
        width=args.width,
        height=args.height,
        max_ticks=args.ticks,
        routing_mode=args.routing_mode,
    )
    sim = AGVSimulation(config)
    vis = VPythonVisualizer(sim)
    vis.animate(ticks=args.ticks, rate_hz=args.rate)


if __name__ == "__main__":
    main()
