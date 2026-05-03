#!/usr/bin/env python3
"""
INFO1167 Robótica Lab #1 — Complete Defense Demo
================================================
One file. Everything. Run this to show the professor the whole project.

Usage:
    python demo.py                    # full demo + VPython animation
    python demo.py --no-vpython       # reports only, skip 3-D animation
    python demo.py --ticks 800        # shorter simulation
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def banner(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def step_run_tests() -> bool:
    banner("STEP 1 / 5 — Running Automated Tests")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True


def step_run_simulation(ticks: int, seed: int, output_dir: Path) -> dict:
    banner("STEP 2 / 5 — Running AGV Simulation")

    from agv_sim.models import SimulationConfig
    from agv_sim.simulation import AGVSimulation

    config = SimulationConfig(
        seed=seed,
        width=10,
        height=8,
        max_ticks=ticks,
        routing_mode="random_shortest",
    )
    sim = AGVSimulation(config)
    summary = sim.run(ticks)

    print(f"  Simulation ticks : {summary['ticks']}")
    print(f"  Total deliveries : {summary['total_deliveries']}")
    print(f"  Robots           : {summary['requirements_signals']['n_robots']}")
    print(f"  Unique colors    : {summary['requirements_signals']['unique_robot_colors']}")
    print(f"  Rotation step    : {summary['requirements_signals']['rotation_step_deg']}°")
    print(f"  Routing mode     : {summary['requirements_signals']['routing_mode']}")

    return sim, summary


def step_generate_artifacts(sim, summary: dict, output_dir: Path) -> dict:
    banner("STEP 3 / 5 — Generating Artifacts")

    from agv_sim.requirements_check import evaluate_requirements
    from agv_sim.visualizer import save_snapshot

    output_dir.mkdir(parents=True, exist_ok=True)

    # Summary JSON
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  Summary JSON     : {summary_path}")

    # Requirements report
    report = evaluate_requirements(sim, summary)
    req_path = output_dir / "requirements_report.json"
    req_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"  Requirements     : {req_path}")

    # Matplotlib snapshot
    img_path = output_dir / "snapshot.png"
    save_snapshot(sim, str(img_path))
    print(f"  Snapshot PNG     : {img_path}")

    return report


def step_print_defense_report(report: dict, summary: dict) -> None:
    banner("STEP 4 / 5 — Defense Report")

    print(f"\n  {'ID':<6} {'Status':<8} {'Requirement'}")
    print(f"  {'-' * 54}")
    for c in report["checks"]:
        status = "PASS" if c["ok"] else "FAIL"
        icon = "✅" if c["ok"] else "❌"
        print(f"  {icon} {c['id']:<4} {status:<8} {c['requirement']}")

    print(f"\n  {'─' * 54}")
    print(
        f"  Pass rate: {report['pass_rate']}%  ({report['passed']}/{len(report['checks'])} checks)"
    )

    # Graph algorithm evidence
    print(f"\n  Graph Algorithm Evidence:")
    ge = summary.get("graph_examples", {})
    print(f"    • BFS path length        : {len(ge.get('bfs_example', []))} nodes")
    print(f"    • Dijkstra path length   : {len(ge.get('dijkstra_example', []))} nodes")
    print(f"    • DFS path length        : {len(ge.get('dfs_example', []))} nodes")
    print(f"    • All paths sample count : {ge.get('all_paths_count_sample', 0)}")
    print(f"    • At least one path      : {ge.get('at_least_one_path', False)}")

    # Cycle evidence
    events = summary.get("events_tail", [])
    deliveries = summary.get("total_deliveries", 0)
    charging = sum(1 for e in events if "started charging" in e)
    ready = sum(1 for e in events if "battery 100%" in e)
    print(f"\n  Cycle Evidence (last {len(events)} ticks):")
    print(f"    • Deliveries completed   : {deliveries}")
    print(f"    • Return-to-base events  : {charging}")
    print(f"    • Battery 100% events    : {ready}")

    print(f"\n  Topics Covered:")
    print(f"    • Python               : ✅")
    print(f"    • Visual Python        : ✅ ( launching next... )")
    print(f"    • Geometría            : ✅ ( atan2, 10° rotation )")
    print(f"    • Grafos — BFS/DFS     : ✅")
    print(f"    • Grafos — Dijkstra    : ✅")
    print(f"    • Grafos — All paths   : ✅")


def step_launch_vpython(ticks: int, seed: int, rate_hz: int) -> None:
    banner("STEP 5 / 5 — Visual Python 3-D Animation")
    print("  Launching VPython warehouse animation...")
    print("  A browser tab should open. Close it to end the demo.\n")
    time.sleep(1)

    from agv_sim.models import SimulationConfig
    from agv_sim.simulation import AGVSimulation
    from agv_sim.vpython_vis import VPythonVisualizer

    config = SimulationConfig(
        seed=seed,
        width=10,
        height=8,
        max_ticks=ticks,
        routing_mode="random_shortest",
    )
    sim = AGVSimulation(config)
    vis = VPythonVisualizer(sim)
    vis.animate(ticks=ticks, rate_hz=rate_hz)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="INFO1167 Lab #1 — Complete Demo",
    )
    parser.add_argument("--ticks", type=int, default=800)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rate", type=int, default=10)
    parser.add_argument("--output-dir", type=str, default="outputs")
    parser.add_argument(
        "--no-vpython",
        action="store_true",
        help="Skip the Visual Python animation (reports only)",
    )
    args = parser.parse_args()

    outdir = Path(args.output_dir)

    # Step 1 — Tests
    if not step_run_tests():
        print("\n❌ Tests failed — aborting demo.")
        sys.exit(1)

    # Step 2 — Simulation
    sim, summary = step_run_simulation(args.ticks, args.seed, outdir)

    # Step 3 — Artifacts
    report = step_generate_artifacts(sim, summary, outdir)

    # Step 4 — Defense report
    step_print_defense_report(report, summary)

    # Step 5 — VPython (last, because it blocks)
    if args.no_vpython:
        banner("STEP 5 / 5 — Visual Python")
        print("  Skipped (--no-vpython).")
        print(f"\n  To launch animation later, run:")
        print(f"    python scripts/run_vpython.py --ticks {args.ticks}")
    else:
        step_launch_vpython(args.ticks, args.seed, args.rate)

    banner("Demo Complete")
    print(f"  All artifacts saved to: {outdir.resolve()}")
    print(f"  Good luck with the defense! 🚀\n")


if __name__ == "__main__":
    main()
