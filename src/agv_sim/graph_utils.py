from __future__ import annotations

import heapq
from typing import Dict, Iterable, List, Tuple

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
