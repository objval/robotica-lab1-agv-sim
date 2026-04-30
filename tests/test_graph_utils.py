from __future__ import annotations

import random

from agv_sim.graph_utils import (
    all_simple_paths_limited,
    bfs_path,
    create_grid_graph,
    dfs_any_path,
    dijkstra_path,
    random_shortest_path,
)


def _is_adjacent_path(path: list[tuple[int, int]]) -> bool:
    for a, b in zip(path, path[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            return False
    return True


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


def test_random_shortest_path_is_shortest_and_adjacent():
    g = create_grid_graph(5, 5)
    rng = random.Random(42)
    path = random_shortest_path(g, (0, 0), (4, 4), rng)

    assert path[0] == (0, 0)
    assert path[-1] == (4, 4)
    assert len(path) == 9  # 8 moves in Manhattan grid
    assert _is_adjacent_path(path)


def test_random_shortest_path_explores_multiple_equivalent_shortest_paths():
    g = create_grid_graph(4, 4)
    rng = random.Random(99)

    observed = set()
    for _ in range(15):
        p = tuple(random_shortest_path(g, (0, 0), (3, 3), rng))
        observed.add(p)

    assert len(observed) >= 2


def test_all_simple_paths_limited_returns_at_least_one_path():
    g = create_grid_graph(4, 3)
    paths = all_simple_paths_limited(g, (0, 0), (3, 2), cutoff=6, max_paths=12)

    assert len(paths) >= 1
    for p in paths:
        assert p[0] == (0, 0)
        assert p[-1] == (3, 2)
        assert _is_adjacent_path(p)
