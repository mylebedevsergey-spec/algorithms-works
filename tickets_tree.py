from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Ticket:
    id: int
    title: str
    priority: int

    def __str__(self) -> str:
        return f"#{self.id} «{self.title}» (приоритет {self.priority})"

class Node:
    __slots__ = ("ticket", "left", "right")

    def __init__(self, ticket: Ticket):
        self.ticket = ticket
        self.left: Optional["Node"] = None
        self.right: Optional["Node"] = None

class TicketBST:
    """Бинарное дерево поиска по инвентарному id заявки."""

    def __init__(self) -> None:
        self.root: Optional[Node] = None
        self._size = 0

    # ---------- вставка ----------
    def insert(self, ticket: Ticket) -> bool:
        """O(h), где h — высота дерева (в среднем O(log n)). False — если id занят."""
        if self.root is None:
            self.root = Node(ticket)
            self._size = 1
            return True

        current = self.root
        while True:
            if ticket.id == current.ticket.id:
                return False
            if ticket.id < current.ticket.id:
                if current.left is None:
                    current.left = Node(ticket)
                    self._size += 1
                    return True
                current = current.left
            else:
                if current.right is None:
                    current.right = Node(ticket)
                    self._size += 1
                    return True
                current = current.right

    # ---------- поиск ----------
    def search(self, ticket_id: int) -> Optional[Ticket]:
        """O(h): спуск по дереву сравнением id."""
        current = self.root
        while current is not None:
            if ticket_id == current.ticket.id:
                return current.ticket
            current = current.left if ticket_id < current.ticket.id else current.right
        return None

    # ---------- удаление ----------
    def delete(self, ticket_id: int) -> bool:
        """O(h). Три случая: лист, один ребёнок, два ребёнка (замена на преемника)."""
        self.root, deleted = self._delete(self.root, ticket_id)
        if deleted:
            self._size -= 1
        return deleted

    def _delete(self, node: Optional[Node], ticket_id: int):
        if node is None:
            return None, False
        if ticket_id < node.ticket.id:
            node.left, deleted = self._delete(node.left, ticket_id)
            return node, deleted
        if ticket_id > node.ticket.id:
            node.right, deleted = self._delete(node.right, ticket_id)
            return node, deleted

        # нашли узел
        if node.left is None:
            return node.right, True
        if node.right is None:
            return node.left, True
        successor = self._min_node(node.right)
        node.ticket = successor.ticket
        node.right, _ = self._delete(node.right, successor.ticket.id)
        return node, True

    @staticmethod
    def _min_node(node: Node) -> Node:
        while node.left is not None:
            node = node.left
        return node

    # ---------- обходы ----------
    def preorder(self) -> List[Ticket]:
        """Прямой обход: узел → левое → правое. O(n)."""
        result: List[Ticket] = []
        stack = [self.root] if self.root else []
        while stack:
            node = stack.pop()
            result.append(node.ticket)
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)
        return result

    def inorder(self) -> List[Ticket]:
        """Симметричный обход: левое → узел → правое. Даёт id по возрастанию. O(n)."""
        result: List[Ticket] = []
        stack: List[Node] = []
        current = self.root
        while stack or current:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append(current.ticket)
            current = current.right
        return result

    def postorder(self) -> List[Ticket]:
        """Обратный обход: левое → правое → узел. O(n)."""
        result: List[Ticket] = []
        stack = [(self.root, False)] if self.root else []
        while stack:
            node, visited = stack.pop()
            if visited:
                result.append(node.ticket)
                continue
            stack.append((node, True))
            if node.right:
                stack.append((node.right, False))
            if node.left:
                stack.append((node.left, False))
        return result

    def level_order(self) -> List[Ticket]:
        """Уровневый обход (BFS, очередь). O(n)."""
        result: List[Ticket] = []
        queue = [self.root] if self.root else []
        head = 0
        while head < len(queue):
            node = queue[head]
            head += 1
            result.append(node.ticket)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

    # ---------- характеристики ----------
    def height(self) -> int:
        """Высота дерева (число рёбер на самом длинном пути). Итеративный обход. O(n)."""
        if self.root is None:
            return -1
        max_depth = 0
        stack = [(self.root, 0)]
        while stack:
            node, depth = stack.pop()
            max_depth = max(max_depth, depth)
            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))
        return max_depth

    def size(self) -> int:
        return self._size

    def leaves_count(self) -> int:
        """Число листьев. O(n)."""
        if self.root is None:
            return 0
        count = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.left is None and node.right is None:
                count += 1
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)
        return count

    def min_ticket(self) -> Optional[Ticket]:
        return self._min_node(self.root).ticket if self.root else None

    def max_ticket(self) -> Optional[Ticket]:
        if self.root is None:
            return None
        node = self.root
        while node.right:
            node = node.right
        return node.ticket

    def is_valid_bst(self) -> bool:
        """Проверка свойства BST: каждый узел в диапазоне (low, high). O(n)."""
        stack = [(self.root, float("-inf"), float("inf"))]
        while stack:
            node, low, high = stack.pop()
            if node is None:
                continue
            if not (low < node.ticket.id < high):
                return False
            stack.append((node.left, low, node.ticket.id))
            stack.append((node.right, node.ticket.id, high))
        return True

    def tickets_with_priority_at_least(self, threshold: int) -> List[Ticket]:
        """Узлы с приоритетом >= threshold — фильтр по дереву. O(n)."""
        return [t for t in self.inorder() if t.priority >= threshold]

class MaxHeap:
    """Максимальная двоичная куча в массиве: дети узла i — 2i+1 и 2i+2."""

    def __init__(self, items: Optional[List[Ticket]] = None) -> None:
        self.data: List[Ticket] = list(items or [])
        if self.data:
            self.build_max_heap()

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    def _sift_down(self, i: int) -> None:
        """Восстановление свойства кучи вниз: O(log n)."""
        n = len(self.data)
        while True:
            largest = i
            left, right = self._left(i), self._right(i)
            if left < n and self.data[left].priority > self.data[largest].priority:
                largest = left
            if right < n and self.data[right].priority > self.data[largest].priority:
                largest = right
            if largest == i:
                return
            self.data[i], self.data[largest] = self.data[largest], self.data[i]
            i = largest

    def _sift_up(self, i: int) -> None:
        """Восстановление свойства кучи вверх: O(log n)."""
        while i > 0 and self.data[self._parent(i)].priority < self.data[i].priority:
            parent = self._parent(i)
            self.data[i], self.data[parent] = self.data[parent], self.data[i]
            i = parent

    def build_max_heap(self) -> None:
        """Построение кучи из неупорядоченного массива: O(n)."""
        for i in range(len(self.data) // 2 - 1, -1, -1):
            self._sift_down(i)

    def push(self, ticket: Ticket) -> None:
        self.data.append(ticket)
        self._sift_up(len(self.data) - 1)

    def pop_max(self) -> Optional[Ticket]:
        """Извлечение максимального элемента: O(log n)."""
        if not self.data:
            return None
        top = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0)
        return top

    def peek(self) -> Optional[Ticket]:
        return self.data[0] if self.data else None

    def is_valid_heap(self) -> bool:
        for i in range(len(self.data)):
            for child in (self._left(i), self._right(i)):
                if child < len(self.data) and self.data[child].priority > self.data[i].priority:
                    return False
        return True

def heapsort(tickets: List[Ticket], descending: bool = False) -> List[Ticket]:
    """Сортировка кучей: O(n log n) времени, O(1) дополнительной памяти.

    Строим максимальную кучу, затем n раз меняем корень с последним элементом
    и просеиваем корень вниз по уменьшающейся части массива.
    По умолчанию сортируем по возрастанию приоритета, descending=True — по убыванию.
    """
    heap = MaxHeap(list(tickets))
    arr = heap.data
    for end in range(len(arr) - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        # просеиваем корень вниз в пределах arr[0..end)
        i, n = 0, end
        while True:
            largest = i
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and arr[left].priority > arr[largest].priority:
                largest = left
            if right < n and arr[right].priority > arr[largest].priority:
                largest = right
            if largest == i:
                break
            arr[i], arr[largest] = arr[largest], arr[i]
            i = largest
    return list(reversed(arr)) if descending else arr

def demo() -> None:
    tickets = [
        Ticket(42, "Не открывается почта", 3),
        Ticket(17, "Забыл пароль от VPN", 7),
        Ticket(88, "Медленно грузится 1С", 5),
        Ticket(5, "Не печатает принтер", 9),
        Ticket(63, "Нужен доступ к папке", 2),
        Ticket(29, "Сбой телефонии", 10),
        Ticket(71, "Установить Office", 1),
        Ticket(34, "Wi-Fi в аудитории 305", 8),
        Ticket(50, "Переустановить ОС", 6),
        Ticket(12, "Заявка на монитор", 4),
    ]
    bst = TicketBST()
    for ticket in tickets:
        bst.insert(ticket)

    print("=== Бинарное дерево поиска заявок ===")
    print("Прямой обход:    ", [t.id for t in bst.preorder()])
    print("Симметричный:    ", [t.id for t in bst.inorder()])
    print("Обратный обход:  ", [t.id for t in bst.postorder()])
    print("Уровневый обход: ", [t.id for t in bst.level_order()])
    print(f"Высота: {bst.height()} | размер: {bst.size()} | листьев: {bst.leaves_count()}")
    print(f"Минимум: {bst.min_ticket()} | максимум: {bst.max_ticket()}")
    print("Свойство BST выполняется:", bst.is_valid_bst())

    found = bst.search(88)
    print("Поиск #88:", found if found else "не найдено")
    print("Удаление #88:", bst.delete(88), "| после удаления размер:", bst.size())
    print("Удаление #17 (два ребёнка):", bst.delete(17))
    print("Симметричный обход после удалений:", [t.id for t in bst.inorder()])
    print("Свойство BST после удалений:", bst.is_valid_bst())

    print("\n=== Максимальная куча по приоритету ===")
    heap = MaxHeap(tickets)
    print("Корень кучи (самая срочная заявка):", heap.peek())
    print("Куча валидна:", heap.is_valid_heap())
    print("Извлекаем три самые срочные:")
    for _ in range(3):
        print("   ", heap.pop_max())
    print("Куча валидна после извлечений:", heap.is_valid_heap())

    print("\n=== Heapsort: итоговый отчёт ===")
    by_priority = heapsort(tickets)
    print("По возрастанию приоритета:")
    for ticket in by_priority:
        print(f"   {ticket.priority:2d} — {ticket}")
    print("\nПо убыванию приоритета (сначала самые срочные):")
    for ticket in heapsort(tickets, descending=True):
        print(f"   {ticket.priority:2d} — #{ticket.id} {ticket.title}")

if __name__ == "__main__":
    demo()
