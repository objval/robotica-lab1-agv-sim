from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt

from .simulation import AGVSimulation


def save_snapshot(sim: AGVSimulation, output_path: str) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title(f"AGV Warehouse Simulation Snapshot (tick={sim.ticks})")
    ax.set_xlim(-1, sim.config.width)
    ax.set_ylim(-1, sim.config.height)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)

    # Carts
    for c in sim.carts:
        ax.scatter(c.node[0], c.node[1], marker="s", s=120, color=c.base_color, edgecolors="black")
        ax.scatter(c.destination[0], c.destination[1], marker="x", s=100, color="black")

    # Robots + bases
    for r in sim.robots:
        ax.scatter(r.base[0], r.base[1], marker="^", s=160, color=r.color, alpha=0.3)
        ax.scatter(r.node[0], r.node[1], marker="o", s=180, color=r.color, edgecolors="black")
        ax.text(r.node[0] + 0.1, r.node[1] + 0.1, f"R{r.id}", fontsize=9)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    return str(p)
