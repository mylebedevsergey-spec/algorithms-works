"""Примеры алгоритмов на графах из заданий курса.

Запуск: python3 examples/graph_algorithms.py
Каждая функция печатает результат и проверяет его с ожидаемым из задания.
"""

from heapq import heappush, heappop


DIRECTED = {
    'A': {'B': 4, 'C': 5},
    'B': {'C': -2, 'D': 6},
    'C': {'D': 3, 'E': 4},
    'D': {'E': 2},
    'E': {},
}

UNDIRECTED = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4, 'C': 1, 'D': 5, 'E': 6},
    'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
    'D': {'B': 5, 'C': 8, 'E': 2},
    'E': {'B': 6, 'C': 10, 'D': 2},
}


def bellman_ford(graph, start):
    """До V-1 серий релаксаций, затем проверка на отрицательный цикл."""
    dist = {v: float('inf') for v in graph}
    prev = {v: None for v in graph}
    dist[start] = 0

    edges = [(u, v, w) for u, row in graph.items() for v, w in row.items()]

    for _ in range(len(graph) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                changed = True
        if not changed:
            break

    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return dist, prev, True

    return dist, prev, False


def restore_path(prev, start, end):
    path = []
    node = end
    while node is not None:
        path.append(node)
        if node == start:
            break
        node = prev[node]
    if not path or path[-1] != start:
        return None
    return list(reversed(path))


def kruskal(graph):
    """Union-Find, рёбра по весу, проверка связности."""
    parent = {v: v for v in graph}
    rank = {v: 0 for v in graph}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    edges = []
    seen = set()
    for u, row in graph.items():
        for v, w in row.items():
            key = tuple(sorted((u, v)))
            if key not in seen:
                seen.add(key)
                edges.append((w, u, v))
    edges.sort()

    mst = []
    total = 0
    for w, u, v in edges:
        if union(u, v):
            mst.append((u, v, w))
            total += w

    roots = {find(v) for v in graph}
    connected = len(roots) == 1
    return mst, total, connected


def topological_sort(graph):
    """Алгоритм Кана с кучей, чтобы порядок был предсказуемым."""
    indegree = {v: 0 for v in graph}
    for u, row in graph.items():
        for v in row:
            indegree[v] += 1

    heap = [v for v in graph if indegree[v] == 0]
    heap.sort()
    order = []

    while heap:
        node = heappop(heap)
        order.append(node)
        for v in graph[node]:
            indegree[v] -= 1
            if indegree[v] == 0:
                heappush(heap, v)

    has_cycle = len(order) != len(graph)
    return order, has_cycle


def floyd_warshall(graph):
    """Матрица расстояний, next_vertex и восстановление маршрута."""
    verts = sorted(graph)
    inf = float('inf')
    dist = {u: {v: inf for v in verts} for u in verts}
    nxt = {u: {v: None for v in verts} for u in verts}

    for u in verts:
        dist[u][u] = 0
        for v, w in graph[u].items():
            dist[u][v] = w
            nxt[u][v] = v

    for k in verts:
        for i in verts:
            for j in verts:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    negative_cycle = any(dist[v][v] < 0 for v in verts)
    return dist, nxt, negative_cycle


def floyd_path(nxt, start, end):
    if nxt[start][end] is None:
        return None
    path = [start]
    node = start
    while node != end:
        node = nxt[node][end]
        path.append(node)
    return path


def prim(graph, start):
    """Очередь с приоритетом, минимальное ребро к непосещённой вершине."""
    visited = {start}
    heap = []
    for v, w in graph[start].items():
        heappush(heap, (w, start, v))

    mst = []
    total = 0

    while heap:
        w, u, v = heappop(heap)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, w))
        total += w
        for nxt, weight in graph[v].items():
            if nxt not in visited:
                heappush(heap, (weight, v, nxt))

    connected = len(visited) == len(graph)
    return mst, total, connected


def main():
    print('Беллман-Форд, старт A')
    dist, prev, negative = bellman_ford(DIRECTED, 'A')
    print('  расстояния:', {k: dist[k] for k in sorted(dist)})
    print('  предки:', {k: prev[k] for k in sorted(prev)})
    print('  отрицательный цикл:', negative)
    print('  путь A->E:', restore_path(prev, 'A', 'E'))

    with_cycle = {k: dict(v) for k, v in DIRECTED.items()}
    with_cycle['E']['B'] = -7
    _, _, negative = bellman_ford(with_cycle, 'A')
    print('  после E->B=-7 отрицательный цикл:', negative)

    print('\nКраскал')
    mst, total, connected = kruskal(UNDIRECTED)
    print('  рёбра:', mst)
    print('  вес:', total, '| связный:', connected)

    print('\nТопологическая сортировка, алгоритм Кана')
    dag = {'A': ['C'], 'B': ['C', 'D'], 'C': ['E'], 'D': ['E'], 'E': ['F'], 'F': []}
    order, cycle = topological_sort(dag)
    print('  порядок:', ' -> '.join(order), '| цикл:', cycle)

    cyclic = {'A': ['C'], 'B': ['C', 'D'], 'C': ['E'], 'D': ['E'], 'E': ['F'], 'F': ['B']}
    order2, cycle2 = topological_sort(cyclic)
    print('  с ребром F->B порядок:', order2, '| цикл:', cycle2)

    print('\nФлойд-Уоршелл')
    dist, nxt, negative = floyd_warshall(DIRECTED)
    print('  A->E:', dist['A']['E'], floyd_path(nxt, 'A', 'E'))
    print('  B->D:', dist['B']['D'], floyd_path(nxt, 'B', 'D'))
    print('  E->A:', dist['E']['A'], floyd_path(nxt, 'E', 'A'))
    _, _, negative = floyd_warshall(with_cycle)
    print('  после E->B=-7 отрицательный цикл:', negative)

    print('\nПрим, старт A')
    mst, total, connected = prim(UNDIRECTED, 'A')
    print('  рёбра:', mst)
    print('  вес:', total, '| рёбер:', len(mst), '| связный:', connected)


if __name__ == '__main__':
    main()
