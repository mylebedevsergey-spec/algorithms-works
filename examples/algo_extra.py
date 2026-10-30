"""Размен, подпоследовательность, многомерная динамика, маршруты, графы, обходы и куча.

Запуск: python3 examples/algo_extra.py
"""

from collections import deque


def min_coins(amount, coins):
    """Минимальное число монет для суммы. inf значит собрать нельзя."""
    inf = float('inf')
    dp = [0] + [inf] * amount
    used = [-1] * (amount + 1)

    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and dp[value - coin] + 1 < dp[value]:
                dp[value] = dp[value - coin] + 1
                used[value] = coin

    if dp[amount] == inf:
        return None, None

    result = []
    rest = amount
    while rest > 0:
        result.append(used[rest])
        rest -= used[rest]
    return dp[amount], result


def count_ways(amount, coins):
    """Сколько способов собрать сумму, порядок монет не важен."""
    dp = [1] + [0] * amount
    for coin in coins:
        for value in range(coin, amount + 1):
            dp[value] += dp[value - coin]
    return dp[amount]


def lis(values):
    """Наибольшая возрастающая подпоследовательность через tails и bisect."""
    from bisect import bisect_left
    tails = []
    for value in values:
        pos = bisect_left(tails, value)
        if pos == len(tails):
            tails.append(value)
        else:
            tails[pos] = value
    return len(tails)


def lcs(a, b):
    """Многомерная динамика, наибольшая общая подпоследовательность."""
    rows, cols = len(a) + 1, len(b) + 1
    dp = [[0] * cols for _ in range(rows)]
    for i in range(1, rows):
        for j in range(1, cols):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    result = []
    i, j = len(a), len(b)
    while i and j:
        if a[i - 1] == b[j - 1]:
            result.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return dp[-1][-1], ''.join(reversed(result))


def count_routes(n):
    """Пункты от 1 до n, шаг на следующий или через один."""
    if n <= 2:
        return [1] * n, 1
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 1
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[1:], dp[n]


def count_routes_constant(n):
    """Тот же ответ, но память O(1)."""
    if n <= 2:
        return 1
    prev, cur = 1, 1
    for _ in range(3, n + 1):
        prev, cur = cur, prev + cur
    return cur


def bfs(graph, start):
    visited = {start}
    order = []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in sorted(graph[node]):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return order


def dfs(graph, start):
    visited = set()
    order = []

    def visit(node):
        visited.add(node)
        order.append(node)
        for neighbour in sorted(graph[node]):
            if neighbour not in visited:
                visit(neighbour)

    visit(start)
    return order


def build_decreasing_heap(values):
    """Убывающая куча: наверху наибольший элемент, дальше значения не растут."""
    heap = list(values)

    def sift_down(index):
        size = len(heap)
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index
            if left < size and heap[left] > heap[largest]:
                largest = left
            if right < size and heap[right] > heap[largest]:
                largest = right
            if largest == index:
                return
            heap[index], heap[largest] = heap[largest], heap[index]
            index = largest

    for index in range(len(heap) // 2 - 1, -1, -1):
        sift_down(index)
    return heap


def heapsort(values):
    """Сортировка кучей, по возрастанию, на месте."""
    heap = list(values)
    size = len(heap)

    def sift(start, end):
        root = start
        while 2 * root + 1 <= end:
            child = 2 * root + 1
            if child + 1 <= end and heap[child] < heap[child + 1]:
                child += 1
            if heap[root] < heap[child]:
                heap[root], heap[child] = heap[child], heap[root]
                root = child
            else:
                return

    for start in range(size // 2 - 1, -1, -1):
        sift(start, size - 1)
    for end in range(size - 1, 0, -1):
        heap[0], heap[end] = heap[end], heap[0]
        sift(0, end - 1)
    return heap


def graph_report(graph):
    print('вершины:', sorted(graph))
    print('порядок:', len(graph), '| размер:', sum(len(v) for v in graph.values()) // 2)
    print('степени:', {v: len(neighbours) for v, neighbours in sorted(graph.items())})
    print('список смежности:')
    for v, neighbours in sorted(graph.items()):
        print('  ', v, '->', ', '.join(sorted(neighbours)))


def shortest_path(graph, start, target):
    prev = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == target:
            break
        for neighbour in sorted(graph[node]):
            if neighbour not in prev:
                prev[neighbour] = node
                queue.append(neighbour)
    if target not in prev:
        return None
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    return list(reversed(path))


def main():
    print('Размен, сумма 11, монеты 1, 5, 6')
    count, coins = min_coins(11, [1, 5, 6])
    print('  монет:', count, '| набор:', coins)
    print('  способов набрать 11:', count_ways(11, [1, 5, 6]))

    print('\nНаибольшая возрастающая подпоследовательность')
    print('  [10, 9, 2, 5, 3, 7, 101, 18] ->', lis([10, 9, 2, 5, 3, 7, 101, 18]))

    print('\nНаибольшая общая подпоследовательность')
    length, word = lcs('AGGTAB', 'GXTXAYB')
    print('  длина:', length, '| подпоследовательность:', word)

    print('\nМаршруты')
    dp, answer = count_routes(7)
    print('  dp:', dp, '| n=7:', answer, '| через O(1):', count_routes_constant(7))

    campus = {
        'A': ['B', 'C'],
        'B': ['A', 'C', 'D'],
        'C': ['A', 'B', 'E'],
        'D': ['B'],
        'E': ['C'],
    }
    print('\nГраф из задания')
    graph_report(campus)
    print('  кратчайший путь A->E:', shortest_path(campus, 'A', 'E'))

    print('\nОбходы')
    print('  BFS:', ' -> '.join(bfs(campus, 'A')))
    print('  DFS:', ' -> '.join(dfs(campus, 'A')))

    data = [9, 4, 7, 1, 8, 2]
    print('\nКуча')
    print('  исходный массив:', data)
    print('  убывающая куча:', build_decreasing_heap(data))
    print('  сортировка кучей:', heapsort(data))


if __name__ == '__main__':
    main()
