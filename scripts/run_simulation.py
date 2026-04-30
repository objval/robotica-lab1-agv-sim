#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agv_sim.models import SimulationConfig
from agv_sim.simulation import AGVSimulation
from agv_sim.visualizer import save_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AGV Lab #1 simulation")
    parser.add_argument("--ticks", type=int, default=600)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--width", type=int, default=10)
    parser.add_argument("--height", type=int, default=8)
    parser.add_argument("--output-dir", type=str, default="outputs")
    args = parser.parse_args()

    config = SimulationConfig(
        seed=args.seed,
        width=args.width,
        height=args.height,
        max_ticks=args.ticks,
    )
    sim = AGVSimulation(config)
    summary = sim.run(args.ticks)

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    summary_path = outdir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    img_path = outdir / "snapshot.png"
    save_snapshot(sim, str(img_path))

    print(f"Simulation complete. Deliveries={summary['total_deliveries']}")
    print(f"Summary: {summary_path}")
    print(f"Snapshot: {img_path}")


if __name__ == "__main__":
    main()
