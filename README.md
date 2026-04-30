# robotica-lab1-agv-sim

Complete implementation for **INFO1167 Robótica — Lab #1** (UCT).  
This project simulates 4 AGV robots in a 2D warehouse map using graph-based routing.

## What this project includes

- Full AGV simulation engine with deterministic seeds.
- 4 robots, task allocation, pickup/delivery, return-to-base, charging cycle.
- Graph algorithms (Dijkstra operationally; BFS/DFS included for learning evidence).
- 10° rotation stepping before movement.
- CLI runner + JSON summary output + simulation snapshot image.
- Tests for routing and simulation invariants.
- Requirement traceability document and research pack.

## Quick start

```bash
cd robotica-lab1-agv-sim
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/run_simulation.py --ticks 800 --seed 42
pytest -q
```

## Outputs

After running the simulation:
- `outputs/summary.json` → deliveries, robot states, event log tail, graph examples
- `outputs/snapshot.png` → visual snapshot for presentation/defense

## Project structure

- `src/agv_sim/models.py` — entities and config
- `src/agv_sim/graph_utils.py` — graph creation + Dijkstra/BFS/DFS
- `src/agv_sim/simulation.py` — core AGV state machine
- `src/agv_sim/visualizer.py` — matplotlib snapshot exporter
- `tests/` — automated verification
- `docs/assets/` — original lab PDF + extracted text
- `docs/research/` — polished research and defense docs

## Teacher defense talking points

1. Problem modeled as graph over warehouse grid (nodes = QR cells).
2. Each robot follows shortest path plans (Dijkstra) under state-machine control.
3. Physical realism proxy: orientation changes in 10° increments before movement.
4. Full life-cycle implemented: assign -> pickup -> deliver -> return -> charge -> repeat.
5. Deterministic reproducibility via fixed random seed.

## License

MIT
