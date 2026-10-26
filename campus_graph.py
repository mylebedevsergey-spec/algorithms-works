import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

INF = float("inf")

@dataclass
class CampusGraph:
    """Неориентированный взвешенный граф кампуса."""

    adjacency: Dict[str, List[Tuple[str, int]]] = field(default_factory=dict)

    # ---------- построение ----------
    def add_vertex(self, name: str) -> None:
        self.adjacency.setdefault(name, [])

    def add_edge(self, a: str, b: str, weight: int, bidirectional: bool = True) -> None:
        """Добавляет маршрут; по умолчанию проход в обе стороны."""
        self.add_vertex(a)
        self.add_vertex(b)
        self.adjacency[a].append((b, weight))
        if bidirectional:
            self.adjacency[b].append((a, weight))

    # ---------- характеристики ----------
    @property
    def vertices(self) -> List[str]:
        return list(self.adjacency)

    def edge_count(self) -> int:
        return sum(len(neighbours) for neighbours in self.adjacency.values()) // 2

    def density(self) -> float:
        v = len(self.adjacency)
        if v < 2:
            return 0.0
        return 2 * self.edge_count() / (v * (v - 1))

    def degree(self, vertex: str) -> int:
        return len(self.adjacency.get(vertex, []))

    def weight_matrix(self) -> List[List[float]]:
        """Матрица весов: 0 на диагонали, INF там, где маршрута нет."""
        names = self.vertices
        index = {name: i for i, name in enumerate(names)}
        n = len(names)
        matrix = [[INF] * n for _ in range(n)]
        for i in range(n):
            matrix[i][i] = 0
        for name, neighbours in self.adjacency.items():
            for other, weight in neighbours:
                matrix[index[name]][index[other]] = weight
        return matrix

    # ---------- обходы ----------
    def bfs(self, start: str) -> List[str]:
        """Обход в ширину: O(V+E). Возвращает порядок посещения."""
        visited = {start}
        queue = [start]
        order = []
        head = 0
        while head < len(queue):
            v = queue[head]
            head += 1
            order.append(v)
            for neighbour, _ in self.adjacency.get(v, []):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
        return order

    def dfs(self, start: str) -> List[str]:
        """Обход в глубину (итеративный стек): O(V+E)."""
        visited = set()
        order = []
        stack = [start]
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            order.append(v)
            for neighbour, _ in sorted(self.adjacency.get(v, []), reverse=True):
                if neighbour not in visited:
                    stack.append(neighbour)
        return order

    def components(self) -> List[List[str]]:
        """Компоненты связности: O(V+E)."""
        seen = set()
        result = []
        for start in self.vertices:
            if start in seen:
                continue
            component = self.bfs(start)
            seen.update(component)
            result.append(component)
        return result

    # ---------- кратчайшие пути ----------
    def dijkstra(self, start: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
        """Кратчайшие расстояния от start: O((V+E) log V)."""
        distances = {v: INF for v in self.vertices}
        previous: Dict[str, Optional[str]] = {v: None for v in self.vertices}
        distances[start] = 0
        heap = [(0, start)]

        while heap:
            current_distance, current = heapq.heappop(heap)
            if current_distance > distances[current]:
                continue
            for neighbour, weight in self.adjacency.get(current, []):
                candidate = current_distance + weight
                if candidate < distances[neighbour]:
                    distances[neighbour] = candidate
                    previous[neighbour] = current
                    heapq.heappush(heap, (candidate, neighbour))
        return distances, previous

    def path_between(self, previous: Dict[str, Optional[str]], target: str) -> List[str]:
        """Восстановление маршрута по массиву предшественников."""
        path: List[str] = []
        current: Optional[str] = target
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        # если путь не начинается со стартовой вершины — вершина недостижима
        return path if path and previous.get(path[0]) is None else path

    def floyd_warshall(self) -> Tuple[List[List[float]], List[List[Optional[int]]]]:
        """Флойд—Уоршелл: O(V^3) времени, O(V^2) памяти.

        Возвращает матрицу расстояний и матрицу «следующей вершины» для
        восстановления пути.
        """
        names = self.vertices
        index = {name: i for i, name in enumerate(names)}
        n = len(names)
        dist = self.weight_matrix()
        next_hop: List[List[Optional[int]]] = [[None] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j and dist[i][j] < INF:
                    next_hop[i][j] = j

        for k in range(n):
            for i in range(n):
                if dist[i][k] == INF:
                    continue
                for j in range(n):
                    through_k = dist[i][k] + dist[k][j]
                    if through_k < dist[i][j]:
                        dist[i][j] = through_k
                        next_hop[i][j] = next_hop[i][k]
        return dist, next_hop

    def restore_path(self, next_hop: List[List[Optional[int]]], start: str, finish: str) -> List[str]:
        names = self.vertices
        index = {name: i for i, name in enumerate(names)}
        i, j = index[start], index[finish]
        if next_hop[i][j] is None:
            return []
        path = [names[i]]
        while i != j:
            i = next_hop[i][j]
            if i is None:
                return []
            path.append(names[i])
        return path

    # ---------- метрики графа ----------
    def eccentricities(self, dist_matrix: List[List[float]]) -> Dict[str, float]:
        names = self.vertices
        return {name: max(dist_matrix[i]) for i, name in enumerate(names)}

    def diameter_radius_center(self, dist_matrix: List[List[float]]) -> Tuple[float, float, List[str]]:
        ecc = self.eccentricities(dist_matrix)
        diameter = max(ecc.values())
        radius = min(ecc.values())
        center = [name for name, value in ecc.items() if value == radius]
        return diameter, radius, center

def build_campus() -> CampusGraph:
    """Сеть маршрутов кампуса (веса — метры)."""
    graph = CampusGraph()
    edges = [
        ("Главный корпус", "Библиотека", 180),
        ("Главный корпус", "Столовая", 240),
        ("Главный корпус", "КПП", 120),
        ("Библиотека", "Лабораторный корпус", 210),
        ("Библиотека", "Спортзал", 320),
        ("Столовая", "Общежитие", 150),
        ("Столовая", "Спортзал", 260),
        ("Лабораторный корпус", "Общежитие", 340),
        ("Лабораторный корпус", "КПП", 290),
        ("Спортзал", "Общежитие", 200),
        ("КПП", "Парковка", 90),
        ("Парковка", "Лабораторный корпус", 260),
    ]
    for a, b, w in edges:
        graph.add_edge(a, b, w)
    return graph

def demo() -> None:
    graph = build_campus()
    names = graph.vertices

    print("=== Граф кампуса ===")
    print(f"Вершин: {len(names)}, рёбер: {graph.edge_count()}, плотность: {graph.density():.2f}")
    for name in names:
        print(f"  {name}: степень {graph.degree(name)}")

    print("\nСписок смежности:")
    for name in names:
        neighbours = ", ".join(f"{other}({w} м)" for other, w in graph.adjacency[name])
        print(f"  {name} -> {neighbours}")

    print("\nМатрица весов (INF — маршрута нет):")
    print("            " + " ".join(f"{n[:6]:>6}" for n in names))
    for i, name in enumerate(names):
        row = " ".join(f"{'inf' if v == INF else v:>6}" for v in graph.weight_matrix()[i])
        print(f"{name[:11]:>11} {row}")

    print("\nBFS от «Главный корпус»:", graph.bfs("Главный корпус"))
    print("DFS от «Главный корпус»:", graph.dfs("Главный корпус"))
    print(f"Компонент связности: {len(graph.components())}")

    distances, previous = graph.dijkstra("Главный корпус")
    print("\nДейкстра от «Главный корпус»:")
    for target in names:
        if target == "Главный корпус":
            continue
        path = graph.path_between(previous, target)
        print(f"  до {target}: {distances[target]} м, маршрут: {' → '.join(path)}")

    dist, next_hop = graph.floyd_warshall()
    print("\nФлойд—Уоршелл, матрица кратчайших расстояний:")
    print("            " + " ".join(f"{n[:6]:>6}" for n in names))
    for i, name in enumerate(names):
        row = " ".join(f"{int(v):>6}" for v in dist[i])
        print(f"{name[:11]:>11} {row}")

    a, b = "Общежитие", "Парковка"
    path = graph.restore_path(next_hop, a, b)
    print(f"\nКратчайший маршрут {a} → {b}: {' → '.join(path)} = {int(dist[names.index(a)][names.index(b)])} м")

    diameter, radius, center = graph.diameter_radius_center(dist)
    print(f"\nДиаметр сети: {int(diameter)} м | радиус: {int(radius)} м | центр: {', '.join(center)}")
    print("Рекомендация: пункт первой помощи логично разместить в центре графа.")

if __name__ == "__main__":
    demo()
