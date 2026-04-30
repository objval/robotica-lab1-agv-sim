#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]


def run_cmd(cmd: List[str], *, cwd: Path = ROOT) -> None:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def stage_setup(python_exec: str) -> None:
    run_cmd([python_exec, "-m", "pip", "install", "-e", ".[dev]"])


def stage_test(python_exec: str) -> None:
    run_cmd([python_exec, "-m", "pytest", "-q"])


def stage_simulate(
    python_exec: str,
    ticks: int,
    seed: int,
    width: int,
    height: int,
    output_dir: str,
    routing_mode: str,
) -> None:
    run_cmd(
        [
            python_exec,
            "scripts/run_simulation.py",
            "--ticks",
            str(ticks),
            "--seed",
            str(seed),
            "--width",
            str(width),
            "--height",
            str(height),
            "--output-dir",
            output_dir,
            "--routing-mode",
            routing_mode,
        ]
    )


def stage_verify(output_dir: str, strict: bool) -> Dict:
    out = ROOT / output_dir
    req_path = out / "requirements_report.json"
    sum_path = out / "summary.json"

    if not req_path.exists():
        raise SystemExit(f"Missing requirements report: {req_path}")
    if not sum_path.exists():
        raise SystemExit(f"Missing simulation summary: {sum_path}")

    report = json.loads(req_path.read_text(encoding="utf-8"))
    summary = json.loads(sum_path.read_text(encoding="utf-8"))

    print("\n=== REQUIREMENT CHECKS ===")
    for c in report["checks"]:
        status = "PASS" if c["ok"] else "FAIL"
        print(f"[{status}] {c['id']} - {c['requirement']}")

    print("\n=== SIM SUMMARY ===")
    print(f"Ticks: {summary['ticks']}")
    print(f"Deliveries: {summary['total_deliveries']}")
    print(f"Routing mode: {summary['requirements_signals']['routing_mode']}")
    print(f"Requirement pass rate: {report['pass_rate']}% ({report['passed']}/{len(report['checks'])})")

    if strict and report["failed"] > 0:
        raise SystemExit(2)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage-based pipeline for INFO1167 AGV Lab #1")
    parser.add_argument(
        "stage",
        choices=["setup", "test", "simulate", "verify", "all"],
        help="Pipeline stage to run",
    )
    parser.add_argument("--python", default=sys.executable, help="Python executable to use")
    parser.add_argument("--ticks", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--width", type=int, default=10)
    parser.add_argument("--height", type=int, default=8)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument(
        "--routing-mode",
        default="random_shortest",
        choices=["random_shortest", "dijkstra", "bfs"],
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="When stage=all, skip dependency installation",
    )
    parser.add_argument(
        "--non-strict",
        action="store_true",
        help="When verifying, do not fail process if requirement check has failures",
    )
    args = parser.parse_args()

    strict = not args.non_strict

    if args.stage == "setup":
        stage_setup(args.python)
        return

    if args.stage == "test":
        stage_test(args.python)
        return

    if args.stage == "simulate":
        stage_simulate(
            args.python,
            args.ticks,
            args.seed,
            args.width,
            args.height,
            args.output_dir,
            args.routing_mode,
        )
        return

    if args.stage == "verify":
        stage_verify(args.output_dir, strict)
        return

    # stage=all
    if not args.skip_setup:
        stage_setup(args.python)
    stage_test(args.python)
    stage_simulate(
        args.python,
        args.ticks,
        args.seed,
        args.width,
        args.height,
        args.output_dir,
        args.routing_mode,
    )
    stage_verify(args.output_dir, strict)


if __name__ == "__main__":
    main()
