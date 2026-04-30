from agv_sim.models import SimulationConfig, RobotState
from agv_sim.simulation import AGVSimulation


def test_simulation_delivers_carts():
    sim = AGVSimulation(SimulationConfig(seed=7, max_ticks=900))
    out = sim.run(900)
    assert out["total_deliveries"] > 0


def test_robot_states_valid():
    sim = AGVSimulation(SimulationConfig(seed=1, max_ticks=100))
    sim.run(100)
    valid = {s.value for s in RobotState}
    for r in sim.robots:
        assert r.state.value in valid


def test_battery_bounds():
    sim = AGVSimulation(SimulationConfig(seed=3, max_ticks=500))
    sim.run(500)
    for r in sim.robots:
        assert 0.0 <= r.battery <= 100.0


def test_cart_color_changes_when_assigned():
    sim = AGVSimulation(SimulationConfig(seed=11, max_ticks=5))
    sim.step()  # trigger assignment
    assigned = [c for c in sim.carts if c.assigned_robot_id is not None]
    assert assigned, "Expected at least one assigned cart"
    for c in assigned:
        robot = next(r for r in sim.robots if r.id == c.assigned_robot_id)
        assert c.base_color == robot.color
