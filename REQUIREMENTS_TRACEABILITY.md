# Requirements Traceability (Lab #1 INFO1167 Robótica)

Source: `docs/assets/Lab_1_INFO1167_Robotica_original.pdf`

## Assignment rule -> Implementation mapping

1. **4 AGV robots in 2D map**  
   - Implemented in `SimulationConfig(n_robots=4)` and grid map in `create_grid_graph()`.

2. **Robots start at bases**  
   - Bases initialized at corners in `_init_entities()`.

3. **Random movement/assignment behavior**  
   - Cart assignment and pickup/drop nodes sampled with deterministic PRNG seed (`random.Random(seed)`).

4. **Cart assigned to robot + color identity**  
   - Each robot has unique color; carts get assigned per robot task.

5. **Graph algorithms for routing**  
   - Dijkstra shortest path for operational routing.
   - BFS/DFS examples included in summary for pedagogical evidence.

6. **Carry cart to destination then return to base**  
   - State machine: `TO_CART -> TO_DESTINATION -> RETURN_TO_BASE -> CHARGING -> IDLE_AT_BASE`.

7. **Rotation by fixed degree increments**  
   - `rotation_step_deg=10` and heading update in `_rotate_then_move()`.

8. **Recharge cycle and restart**  
   - `CHARGING` state increases battery to 100%; robot is then reallocated.

9. **Related topics: Python/Visual Python/Geometry/Graphs**  
   - Python implementation + geometric heading model + graph routing + visualization snapshot.
