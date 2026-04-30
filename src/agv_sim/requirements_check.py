from __future__ import annotations

from typing import Any, Dict, List

from .simulation import AGVSimulation


def evaluate_requirements(sim: AGVSimulation, summary: Dict[str, Any]) -> Dict[str, Any]:
    unique_colors = {r.color for r in sim.robots}
    all_paths_count = summary.get("graph_examples", {}).get("all_paths_count_sample", 0)

    checks: List[Dict[str, Any]] = [
        {
            "id": "R1",
            "requirement": "Simular 4 robots AGV en mapa 2D",
            "ok": len(sim.robots) == 4 and sim.config.width > 0 and sim.config.height > 0,
            "evidence": {"n_robots": len(sim.robots), "grid": [sim.config.width, sim.config.height]},
        },
        {
            "id": "R2",
            "requirement": "Inicio en bases y búsqueda de carrito asignado aleatoriamente",
            "ok": any("assigned cart" in e for e in sim.events),
            "evidence": {"assignment_events": [e for e in sim.events if "assigned cart" in e][:4]},
        },
        {
            "id": "R3",
            "requirement": "Carrito adopta color único del robot asignado",
            "ok": len(unique_colors) == len(sim.robots),
            "evidence": {"unique_robot_colors": sorted(unique_colors)},
        },
        {
            "id": "R4",
            "requirement": "Rutas dadas por algoritmos de grafos",
            "ok": bool(summary.get("graph_examples", {}).get("dijkstra_example"))
            and bool(summary.get("graph_examples", {}).get("bfs_example"))
            and bool(summary.get("graph_examples", {}).get("dfs_example")),
            "evidence": {
                "dijkstra_len": len(summary.get("graph_examples", {}).get("dijkstra_example", [])),
                "bfs_len": len(summary.get("graph_examples", {}).get("bfs_example", [])),
                "dfs_len": len(summary.get("graph_examples", {}).get("dfs_example", [])),
            },
        },
        {
            "id": "R5",
            "requirement": "Movimiento con variación aleatoria hacia nodo final",
            "ok": sim.config.routing_mode == "random_shortest",
            "evidence": {"routing_mode": sim.config.routing_mode},
        },
        {
            "id": "R6",
            "requirement": "Rotaciones en pasos de 10°",
            "ok": abs(sim.config.rotation_step_deg - 10.0) < 1e-9,
            "evidence": {"rotation_step_deg": sim.config.rotation_step_deg},
        },
        {
            "id": "R7",
            "requirement": "Entrega y retorno a base para carga",
            "ok": summary.get("total_deliveries", 0) > 0
            and any("reached base and started charging" in e for e in sim.events)
            and any("battery 100% and ready" in e for e in sim.events),
            "evidence": {
                "total_deliveries": summary.get("total_deliveries", 0),
                "started_charging_events": [e for e in sim.events if "reached base and started charging" in e][:4],
                "battery_ready_events": [e for e in sim.events if "battery 100% and ready" in e][:4],
            },
        },
        {
            "id": "R8",
            "requirement": "Temas de grafos: profundidad, ruta corta, todas y al menos una ruta",
            "ok": bool(summary.get("graph_examples", {}).get("dfs_example"))
            and bool(summary.get("graph_examples", {}).get("dijkstra_example"))
            and all_paths_count > 0,
            "evidence": {
                "all_paths_count_sample": all_paths_count,
                "at_least_one_path": summary.get("graph_examples", {}).get("at_least_one_path", False),
            },
        },
    ]

    passed = sum(1 for c in checks if c["ok"])
    return {
        "checks": checks,
        "passed": passed,
        "failed": len(checks) - passed,
        "pass_rate": round((passed / len(checks)) * 100.0, 2),
    }
