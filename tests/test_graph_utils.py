from agv_sim.graph_utils import create_grid_graph, dijkstra_path, bfs_path, dfs_any_path


def test_dijkstra_path_on_grid():
    g = create_grid_graph(4, 4)
    p = dijkstra_path(g, (0, 0), (3, 3))
    assert p[0] == (0, 0)
    assert p[-1] == (3, 3)
    # Manhattan shortest length in nodes for 3+3 moves
    assert len(p) == 7


def test_bfs_and_dfs_return_paths():
    g = create_grid_graph(4, 3)
    p1 = bfs_path(g, (0, 0), (3, 2))
    p2 = dfs_any_path(g, (0, 0), (3, 2))
    assert p1[0] == (0, 0) and p1[-1] == (3, 2)
    assert p2[0] == (0, 0) and p2[-1] == (3, 2)
