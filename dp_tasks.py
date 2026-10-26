from typing import List, Tuple

def count_binary_no_adjacent_ones(n: int) -> int:
    """Задача 1. O(n) времени, O(1) памяти.

    dp0[i] — сколько последовательностей длины i заканчиваются на 0,
    dp1[i] — заканчиваются на 1. Тогда
        dp0[i] = dp0[i-1] + dp1[i-1]   (к любому хвосту можно дописать 0)
        dp1[i] = dp0[i-1]              (единицу можно дописать только после нуля)
    Ответ: dp0[n] + dp1[n]. Это числа Фибоначчи: F(n+2).
    """
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    dp0, dp1 = 1, 0  # пустая последовательность: длина 0
    for _ in range(n):
        dp0, dp1 = dp0 + dp1, dp0
    return dp0 + dp1

def count_grid_paths(n: int, m: int) -> int:
    """Задача 2. O(n*m) времени, O(min(n,m)) памяти.

    paths[i][j] = paths[i-1][j] + paths[i][j-1];
    в первой строке и первом столбце ровно один путь.
    Храним одну строку: слева уже посчитано, сверху — старое значение.
    """
    if n <= 0 or m <= 0:
        return 0
    row = [1] * m
    for _ in range(1, n):
        for j in range(1, m):
            row[j] += row[j - 1]
    return row[m - 1]

def min_cost_path(grid: List[List[int]]) -> Tuple[int, List[Tuple[int, int]]]:
    """Задача 3. O(n*m) времени, O(n*m) памяти (нужно для восстановления пути).

    dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) —
    пришли сверху, слева или по диагонали. Путь восстанавливаем обратным ходом.
    """
    if not grid or not grid[0]:
        return 0, []
    n, m = len(grid), len(grid[0])
    dp = [[0] * m for _ in range(n)]
    dp[0][0] = grid[0][0]

    for j in range(1, m):
        dp[0][j] = dp[0][j - 1] + grid[0][j]
    for i in range(1, n):
        dp[i][0] = dp[i - 1][0] + grid[i][0]
    for i in range(1, n):
        for j in range(1, m):
            dp[i][j] = grid[i][j] + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    path = []
    i, j = n - 1, m - 1
    while True:
        path.append((i, j))
        if i == 0 and j == 0:
            break
        candidates = []
        if i > 0:
            candidates.append((dp[i - 1][j], i - 1, j))
        if j > 0:
            candidates.append((dp[i][j - 1], i, j - 1))
        if i > 0 and j > 0:
            candidates.append((dp[i - 1][j - 1], i - 1, j - 1))
        _, i, j = min(candidates)

    return dp[-1][-1], list(reversed(path))

def lis_length(sequence: List[int]) -> int:
    """Задача 4. O(n log n) времени, O(n) памяти.

    tails[k] — минимально возможное последнее число возрастающей
    подпоследовательности длины k+1. Для каждого x ищем бинпоиском
    первое место, где tails[pos] >= x, и заменяем tails[pos] = x.
    """
    import bisect

    tails: List[int] = []
    for x in sequence:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)

def longest_palindromic_subsequence(s: str) -> int:
    """Задача 5. O(n^2) времени, O(n^2) памяти.

    dp[i][j] — длина наибольшего палиндрома в s[i..j].
    Если s[i] == s[j], то dp[i][j] = dp[i+1][j-1] + 2,
    иначе dp[i][j] = max(dp[i+1][j], dp[i][j-1]).
    """
    n = len(s)
    if n == 0:
        return 0
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    for length in range(2, n + 1):
        for i in range(0, n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = 2 if length == 2 else dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]

if __name__ == "__main__":
    print("Задача 1: последовательности без двух единиц подряд")
    for n in range(0, 11):
        print(f"  n={n:2d} -> {count_binary_no_adjacent_ones(n)}")

    print("\nЗадача 2: число путей по полю n×m (вправо/вниз)")
    for n, m in [(1, 1), (2, 2), (3, 3), (3, 7), (10, 10)]:
        print(f"  {n}×{m} -> {count_grid_paths(n, m)}")

    print("\nЗадача 3: маршрут минимального веса (вправо/вниз/по диагонали)")
    grid = [
        [1, 3, 1, 2],
        [2, 1, 4, 1],
        [5, 2, 1, 3],
        [1, 4, 2, 1],
    ]
    cost, path = min_cost_path(grid)
    print(f"  вес = {cost}, путь = {path}")

    print("\nЗадача 4: длина наибольшей строго возрастающей подпоследовательности")
    for seq in ([10, 9, 2, 5, 3, 7, 101, 18], [1, 2, 3, 4], [5, 4, 3, 2]):
        print(f"  {seq} -> {lis_length(seq)}")

    print("\nЗадача 5: наибольший палиндром вычёркиванием букв")
    for s in ("ACGTGTA", "ABCD", "AAAA", "RACECAR"):
        print(f"  {s} -> {longest_palindromic_subsequence(s)}")
