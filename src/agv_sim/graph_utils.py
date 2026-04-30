from __future__ import annotations

import heapq
import random
from typing import Dict, List, Optional, Tuple

import networkx as nx

from .models import Node


def create_grid_graph(width: int, height: int) -> nx.Graph:
    g = nx.Graph()
    for x in range(width):
        for y in range(height):
            g.add_node((x, y))
    for x in range(width):
        for y in range(height):
            if x + 1 < width:
                g.add_edge((x, y), (x + 1, y), weight=1.0)
            if y + 1 < height:
                g.add_edge((x, y), (x, y + 1), weight=1.0)
    return g


def dijkstra_path(graph: nx.Graph, src: Node, dst: Node) -> List[Node]:
    if src == dst:
        return [src]
    queue: List[Tuple[float, Node]] = [(0.0, src)]
    dist: Dict[Node, float] = {src: 0.0}
    prev: Dict[Node, Node] = {}

    while queue:
        d, u = heapq.heappop(queue)
        if u == dst:
            break
        if d > dist.get(u, float("inf")):
            continue
        for v in graph.neighbors(u):
            nd = d + graph[u][v].get("weight", 1.0)
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(queue, (nd, v))

    if dst not in dist:
        return []

    path = [dst]
    cur = dst
    while cur != src:
        cur = prev[cur]
        path.append(cur)
    path.reverse()
    return path


def random_shortest_path(graph: nx.Graph, src: Node, dst: Node, rng: random.Random) -> List[Node]:
    """Return a shortest path but randomize tie-breaks among equivalent shortest options."""
    if src == dst:
        return [src]

    dist_from_src = nx.single_source_dijkstra_path_length(graph, src, weight="weight")
    if dst not in dist_from_src:
        return []

    total_cost = dist_from_src[dst]
    dist_to_dst = nx.single_source_dijkstra_path_length(graph, dst, weight="weight")

    path = [src]
    current = src
    safety = 0
    while current != dst:
        safety += 1
        if safety > graph.number_of_nodes() + 5:
            return []

        candidates: List[Node] = []
        for neighbor in graph.neighbors(current):
            edge_cost = graph[current][neighbor].get("weight", 1.0)
            from_src = dist_from_src.get(current, float("inf")) + edge_cost
            to_dst = dist_to_dst.get(neighbor, float("inf"))
            if abs((from_src + to_dst) - total_cost) < 1e-9:
                candidates.append(neighbor)

        if not candidates:
            return []

        current = rng.choice(candidates)
        path.append(current)

    return path


def bfs_path(graph: nx.Graph, src: Node, dst: Node) -> List[Node]:
    from collections import deque

    if src == dst:
        return [src]
    q = deque([src])
    prev: Dict[Node, Node] = {}
    seen = {src}
    while q:
        u = q.popleft()
        if u == dst:
            break
        for v in graph.neighbors(u):
            if v in seen:
                continue
            seen.add(v)
            prev[v] = u
            q.append(v)
    if dst not in seen:
        return []
    path = [dst]
    cur = dst
    while cur != src:
        cur = prev[cur]
        path.append(cur)
    path.reverse()
    return path


def dfs_any_path(graph: nx.Graph, src: Node, dst: Node) -> List[Node]:
    stack = [(src, [src])]
    seen = set()
    while stack:
        u, path = stack.pop()
        if u == dst:
            return path
        if u in seen:
            continue
        seen.add(u)
        for v in graph.neighbors(u):
            if v not in path:
                stack.append((v, path + [v]))
    return []


def all_simple_paths_limited(
    graph: nx.Graph,
    src: Node,
    dst: Node,
    *,
    cutoff: Optional[int] = None,
    max_paths: int = 20,
) -> List[List[Node]]:
    paths: List[List[Node]] = []
    for idx, path in enumerate(nx.all_simple_paths(graph, src, dst, cutoff=cutoff)):
        paths.append(path)
        if idx + 1 >= max_paths:
            break
    return paths
