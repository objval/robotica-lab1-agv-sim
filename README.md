# robotica-lab1-agv-sim

Complete implementation for **INFO1167 Robótica — Lab #1** (UCT).  
This project simulates 4 AGV robots in a 2D warehouse map using graph-based routing, with explicit requirement checks against the lab rules.

## What this project includes

- Full AGV simulation engine with deterministic seeds.
- 4 robots, random cart assignment, pickup/delivery, return-to-base, charge-to-100%, cycle restart.
- Cart color coupling with assigned robot color (unique robot colors).
- 10° rotation stepping before movement.
- Graph algorithms evidence:
  - BFS (búsqueda en profundidad/anchura context evidence)
  - Dijkstra (ruta más corta)
  - DFS (al menos una ruta)
  - Enumerated simple paths sample (todas las rutas, bounded sample)
- Stage-based orchestrator script for modular execution from one entrypoint.
- Automated tests and machine-readable requirement report.

## One-script modular pipeline (by stage)

Use `scripts/pipeline.py` as the single entrypoint.

```bash
cd robotica-lab1-agv-sim
python3 -m venv .venv
source .venv/bin/activate

# Stage 1: setup dependencies
python scripts/pipeline.py setup

# Stage 2: run tests
python scripts/pipeline.py test

# Stage 3: run simulation
python scripts/pipeline.py simulate --ticks 1000 --seed 42 --routing-mode random_shortest --output-dir outputs

# Stage 4: verify requirements from generated artifacts
python scripts/pipeline.py verify --output-dir outputs

# Run everything in one command
python scripts/pipeline.py all --ticks 1000 --seed 42 --routing-mode random_shortest --output-dir outputs
```

### Routing modes

- `random_shortest` (default): shortest-path intelligence with randomized tie-breaks among equivalent shortest options.
- `dijkstra`: deterministic shortest path.
- `bfs`: breadth-first path (uniform grid, pedagogical mode).

## Outputs

After simulation (`simulate` or `all`):

- `outputs/summary.json` → deliveries, entities, config, graph evidence, requirement signals.
- `outputs/requirements_report.json` → pass/fail checklist for lab rules (R1..R8).
- `outputs/snapshot.png` → visual snapshot for presentation/defense.

## Project structure

- `scripts/pipeline.py` — single stage-based orchestrator (`setup|test|simulate|verify|all`)
- `scripts/run_simulation.py` — simulation execution + output artifact generation
- `src/agv_sim/models.py` — entities and config
- `src/agv_sim/graph_utils.py` — graph creation + BFS/DFS/Dijkstra + random shortest + path enumeration
- `src/agv_sim/simulation.py` — core AGV state machine
- `src/agv_sim/requirements_check.py` — explicit 1:1 lab requirement validator
- `src/agv_sim/visualizer.py` — matplotlib snapshot exporter
- `tests/` — automated verification
- `docs/assets/` — original lab PDF + extracted text
- `docs/research/` — research and defense docs

## Teacher defense talking points (aligned to lab)

1. Warehouse modeled as 2D QR-node graph.
2. Four AGVs start at base nodes and get random cart assignments.
3. Cart color changes to robot color during assignment; resets after delivery.
4. Robots rotate in 10° steps before moving along graph routes.
5. Full cycle implemented: assign -> pickup -> deliver -> return -> charging -> restart.
6. Graph-topic evidence includes DFS, shortest path, and multiple path enumeration.

## License

MIT
