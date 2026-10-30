"""Узлы деревьев, куча, очередь с приоритетом, хеш-таблицы и поиск повторов.

Запуск: python3 examples/trees_hash_basics.py
"""

from heapq import heappush, heappop


class Node:
    """Узел бинарного дерева поиска."""

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None

    def __repr__(self):
        return f'Node({self.key})'


class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, key, value=None):
        node = Node(key, value)
        if self.root is None:
            self.root = node
            self.size = 1
            return node

        current = self.root
        while True:
            if key < current.key:
                if current.left is None:
                    current.left = node
                    node.parent = current
                    break
                current = current.left
            elif key > current.key:
                if current.right is None:
                    current.right = node
                    node.parent = current
                    break
                current = current.right
            else:
                current.value = value
                return current

        self.size += 1
        return node

    def search(self, key):
        current = self.root
        while current is not None and current.key != key:
            current = current.left if key < current.key else current.right
        return current

    def inorder(self):
        result = []
        stack = []
        current = self.root
        while stack or current:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append(current.key)
            current = current.right
        return result


class PriorityQueue:
    """Минимальная очередь с приоритетом на куче."""

    def __init__(self):
        self.heap = []

    def push(self, priority, value):
        heappush(self.heap, (priority, value))

    def pop(self):
        if not self.heap:
            raise IndexError('очередь пуста')
        return heappop(self.heap)

    def peek(self):
        return self.heap[0] if self.heap else None

    def __len__(self):
        return len(self.heap)


class ChainedHashTable:
    """Разрешение коллизий методом цепочек."""

    def __init__(self, size=9, hash_fn=None):
        self.size = size
        self.buckets = [[] for _ in range(size)]
        self.hash_fn = hash_fn or (lambda k: k % size)

    def put(self, key, value=None):
        index = self.hash_fn(key) % self.size
        for pair in self.buckets[index]:
            if pair[0] == key:
                pair[1] = value
                return
        self.buckets[index].append([key, value])

    def get(self, key):
        index = self.hash_fn(key) % self.size
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return None

    def view(self):
        return {i: [pair[0] for pair in bucket] for i, bucket in enumerate(self.buckets) if bucket}


class OpenHashTable:
    """Линейное пробирование."""

    def __init__(self, size=9, hash_fn=None):
        self.size = size
        self.slots = [None] * size
        self.hash_fn = hash_fn or (lambda k: k % size)

    def put(self, key, value=None):
        start = self.hash_fn(key) % self.size
        for step in range(self.size):
            index = (start + step) % self.size
            if self.slots[index] is None or self.slots[index][0] == key:
                self.slots[index] = [key, value]
                return index
        raise OverflowError('таблица заполнена')

    def get(self, key):
        start = self.hash_fn(key) % self.size
        for step in range(self.size):
            index = (start + step) % self.size
            if self.slots[index] is None:
                return None
            if self.slots[index][0] == key:
                return self.slots[index][1]
        return None

    def view(self):
        return {i: (slot[0] if slot else None) for i, slot in enumerate(self.slots)}


class AVLNode(Node):
    def __init__(self, key, value=None):
        super().__init__(key, value)
        self.height = 1


def height(node):
    return node.height if node else 0


def update_height(node):
    node.height = 1 + max(height(node.left), height(node.right))


def rotate_right(y):
    x = y.left
    middle = x.right
    x.right = y
    y.left = middle
    if middle:
        middle.parent = y
    x.parent = y.parent
    y.parent = x
    update_height(y)
    update_height(x)
    return x


def rotate_left(x):
    y = x.right
    middle = y.left
    y.left = x
    x.right = middle
    if middle:
        middle.parent = x
    y.parent = x.parent
    x.parent = y
    update_height(x)
    update_height(y)
    return y


def balance(node):
    update_height(node)
    diff = height(node.left) - height(node.right)
    if diff > 1:
        if height(node.left.left) < height(node.left.right):
            node.left = rotate_left(node.left)
        return rotate_right(node)
    if diff < -1:
        if height(node.right.right) < height(node.right.left):
            node.right = rotate_right(node.right)
        return rotate_left(node)
    return node


def avl_insert(node, key):
    if node is None:
        return AVLNode(key)
    if key < node.key:
        node.left = avl_insert(node.left, key)
        node.left.parent = node
    elif key > node.key:
        node.right = avl_insert(node.right, key)
        node.right.parent = node
    else:
        return node
    return balance(node)


def duplicates_bruteforce(values):
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] == values[j]:
                return True
    return False


def duplicates_sort(values):
    ordered = sorted(values)
    for i in range(1, len(ordered)):
        if ordered[i] == ordered[i - 1]:
            return True
    return False


def duplicates_set(values):
    seen = set()
    for value in values:
        if value in seen:
            return True
        seen.add(value)
    return False


def duplicates_bitset(values, k):
    """Если все значения не больше k, хватает массива отметок длины k."""
    marks = bytearray(k + 1)
    for value in values:
        if marks[value]:
            return True
        marks[value] = 1
    return False


def main():
    tree = BST()
    for key in [50, 30, 70, 20, 40, 60, 80]:
        tree.insert(key)
    print('BST, симметричный обход:', tree.inorder())
    print('поиск 40:', tree.search(40), '| поиск 45:', tree.search(45))

    queue = PriorityQueue()
    for priority, task in [(3, 'письмо'), (1, 'сбой'), (2, 'звонок')]:
        queue.push(priority, task)
    print('\nОчередь с приоритетом:', [queue.pop() for _ in range(len(queue))])

    avl_root = None
    for key in [30, 20, 40, 10, 25, 50, 5]:
        avl_root = avl_insert(avl_root, key)
    print('\nAVL, высота корня после вставок:', avl_root.height)

    keys = [67, 13, 49, 24, 40, 33, 58]
    h = lambda k: (11 * k + 4) % 9

    chained = ChainedHashTable(9, h)
    opened = OpenHashTable(9, h)
    for key in keys:
        chained.put(key)
        opened.put(key)

    print('\nХеш-функция (11k+4) mod 9, ключи', keys)
    print('индексы:', {k: h(k) for k in keys})
    print('цепочки:', chained.view())
    print('открытая адресация:', opened.view())

    data = [4, 7, 9, 4, 2]
    print('\nПовторы в', data)
    print('  перебором:', duplicates_bruteforce(data))
    print('  сортировкой:', duplicates_sort(data))
    print('  множеством:', duplicates_set(data))
    print('  массивом отметок:', duplicates_bitset(data, max(data)))


if __name__ == '__main__':
    main()
