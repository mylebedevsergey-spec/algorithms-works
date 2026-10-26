from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Equipment:
    id: int
    name: str
    room: str
    status: str

    def __str__(self) -> str:
        return f"{self.id:>5} | {self.name[:28]:<28} | {self.room:<6} | {self.status}"

EMPTY = object()   # маркер пустой ячейки (отличается от None — «удалено»)
DELETED = object()  # маркер удалённой ячейки для открытой адресации

class HashTable:
    """Хеш-таблица реестра оборудования с выбором алгоритма разрешения коллизий."""

    METHODS = ("chaining", "linear", "quadratic", "double")

    def __init__(self, method: str = "chaining", capacity: int = 11) -> None:
        if method not in self.METHODS:
            raise ValueError(f"метод должен быть одним из {self.METHODS}")
        self.method = method
        self.capacity = capacity
        self.size = 0
        self.collisions = 0        # коллизии при вставке
        self.insert_collisions = 0 # коллизии при вставке (не сбрасывается)
        self.total_probes = 0      # суммарные пробы при вставке/поиске
        self.lookups = 0           # число операций поиска
        # для цепочек — список списков, для открытой адресации — список ячеек
        self.buckets: List[list] = [[] for _ in range(capacity)] if method == "chaining" else [EMPTY] * capacity

    # ---------- хеш-функции ----------
    def h1(self, key: int) -> int:
        """Основная хеш-функция: сумма цифр ключа, умноженная на 31, по модулю размера.

        Для инвентарных номеров (числа) это даёт хорошее рассеивание и легко объясняется.
        """
        digits_sum = sum(int(d) for d in str(key))
        return (digits_sum * 31) % self.capacity

    def h2(self, key: int) -> int:
        """Вторая хеш-функция для двойного хеширования: взаимно проста с размером таблицы."""
        return 1 + (key % (self.capacity - 1))

    def probe_index(self, key: int, attempt: int) -> int:
        """Адрес на attempt-й пробе для выбранного метода."""
        base = self.h1(key)
        if self.method == "linear":
            return (base + attempt) % self.capacity
        if self.method == "quadratic":
            return (base + attempt * attempt) % self.capacity
        if self.method == "double":
            return (base + attempt * self.h2(key)) % self.capacity
        raise ValueError("для цепочек пробы не нужны")

    # ---------- служебное ----------
    def load_factor(self) -> float:
        return self.size / self.capacity

    def _maybe_rehash(self) -> None:
        """Перестраиваем таблицу при заполнении > 0.7 (удвоение размера)."""
        if self.load_factor() <= 0.7:
            return
        old_items = self.items()
        new_capacity = self.capacity * 2 + 1
        self.__init__(method=self.method, capacity=new_capacity)  # сброс статистики
        for record in old_items:
            self.insert(record, count_stats=False)

    def items(self) -> List[Equipment]:
        if self.method == "chaining":
            return [record for bucket in self.buckets for record in bucket]
        return [cell for cell in self.buckets if cell is not EMPTY and cell is not DELETED]

    # ---------- операции ----------
    def insert(self, record: Equipment, count_stats: bool = True) -> bool:
        """Вставка. False — если ключ уже есть."""
        if self.load_factor() > 0.7:
            self._maybe_rehash()

        if self.method == "chaining":
            bucket = self.buckets[self.h1(record.id)]
            if any(existing.id == record.id for existing in bucket):
                return False
            if bucket:
                self.insert_collisions += 1
            bucket.append(record)
            self.size += 1
            if count_stats:
                self.total_probes += 1
                self.lookups += 1
            return True

        for attempt in range(self.capacity):
            index = self.probe_index(record.id, attempt)
            cell = self.buckets[index]
            if cell is EMPTY or cell is DELETED:
                if attempt > 0:
                    self.insert_collisions += 1
                self.buckets[index] = record
                self.size += 1
                if count_stats:
                    self.total_probes += attempt + 1
                    self.lookups += 1
                return True
            if isinstance(cell, Equipment) and cell.id == record.id:
                return False
        raise RuntimeError("таблица заполнена")

    def search(self, key: int) -> Optional[Equipment]:
        """Поиск по инвентарному номеру."""
        self.lookups += 1
        if self.method == "chaining":
            bucket = self.buckets[self.h1(key)]
            self.total_probes += 1
            for record in bucket:
                if record.id == key:
                    return record
            return None

        for attempt in range(self.capacity):
            index = self.probe_index(key, attempt)
            self.total_probes += 1
            cell = self.buckets[index]
            if cell is EMPTY:
                return None
            if isinstance(cell, Equipment) and cell.id == key:
                return cell
        return None

    def delete(self, key: int) -> bool:
        if self.method == "chaining":
            bucket = self.buckets[self.h1(key)]
            for i, record in enumerate(bucket):
                if record.id == key:
                    bucket.pop(i)
                    self.size -= 1
                    return True
            return False

        for attempt in range(self.capacity):
            index = self.probe_index(key, attempt)
            cell = self.buckets[index]
            if cell is EMPTY:
                return False
            if isinstance(cell, Equipment) and cell.id == key:
                self.buckets[index] = DELETED
                self.size -= 1
                return True
        return False

    def max_cluster(self) -> int:
        """Самая длинная цепочка (для цепочек) или серия занятых ячеек (для пробирования)."""
        if self.method == "chaining":
            return max((len(bucket) for bucket in self.buckets), default=0)
        best = current = 0
        for cell in self.buckets:
            if cell is not EMPTY and cell is not DELETED:
                current += 1
                best = max(best, current)
            else:
                current = 0
        return best

    def avg_probes(self) -> float:
        return self.total_probes / self.lookups if self.lookups else 0.0

    def print_table(self) -> None:
        print(f"  метод: {self.method}, размер таблицы: {self.capacity}, "
              f"элементов: {self.size}, load factor: {self.load_factor():.2f}")
        for i in range(self.capacity):
            cell = self.buckets[i]
            if self.method == "chaining":
                content = " -> ".join(str(r.id) for r in cell) if cell else "—"
            else:
                content = "—" if cell is EMPTY else ("×" if cell is DELETED else str(cell.id))
            print(f"    [{i:>2}] {content}")

def seed_data() -> List[Equipment]:
    return [
        Equipment(1024, "Проектор Epson EB-X51", "305", "рабочее"),
        Equipment(2048, "Ноутбук Lenovo ThinkPad", "208", "рабочее"),
        Equipment(3072, "МФУ HP LaserJet M428", "101", "требует ремонта"),
        Equipment(4096, "Интерактивная панель", "301", "рабочее"),
        Equipment(5120, "Коммутатор Cisco 2960", "серверная", "рабочее"),
        Equipment(6144, "Точка доступа Ubiquiti", "3 этаж", "рабочее"),
        Equipment(7168, "Монитор Dell P2419H", "207", "списано"),
        Equipment(8192, "Системный блок HP ProDesk", "209", "рабочее"),
        Equipment(9216, "Принтер Kyocera ECOSYS", "102", "рабочее"),
        Equipment(10240, "Сканер Canon LiDE 400", "библиотека", "рабочее"),
        Equipment(11264, "ИБП APC Smart-UPS", "серверная", "рабочее"),
        Equipment(12288, "Веб-камера Logitech C920", "310", "рабочее"),
        Equipment(13312, "Микрофон Rode NT-USB", "студия", "рабочее"),
        Equipment(14336, "Графический планшет Wacom", "дизайн-класс", "рабочее"),
        Equipment(15360, "3D-принтер Creality Ender 3", "лаборатория", "требует ремонта"),
        Equipment(16384, "Паяльная станция", "лаборатория", "рабочее"),
        Equipment(17408, "Осциллограф Rigol", "лаборатория", "рабочее"),
        Equipment(18432, "Роутер MikroTik hAP", "серверная", "рабочее"),
        Equipment(19456, "Плоттер HP DesignJet", "305", "списано"),
        Equipment(20480, "Документ-камера AVer", "302", "рабочее"),
    ]

def demo() -> None:
    records = seed_data()

    print("=== Реестр оборудования ===")
    print(f"{'id':>5} | {'наименование':<28} | {'аудитория':<6} | состояние")
    print("-" * 72)
    for record in records:
        print(record)

    summary = []
    for method in HashTable.METHODS:
        table = HashTable(method=method, capacity=11)
        for record in records:
            table.insert(record, count_stats=False)
        # отдельно считаем статистику поиска
        table.collisions = 0
        table.total_probes = 0
        table.lookups = 0
        for record in seed_data():
            table.search(record.id)
        for miss in (1111, 2222, 3333, 4444, 5555):
            table.search(miss)

        print("\n" + "=" * 72)
        print(f"Алгоритм: {method}")
        table.print_table()
        print(f"  коллизий при вставке: {table.insert_collisions}")
        print(f"  среднее число проб при поиске: {table.avg_probes():.2f}")
        print(f"  максимальная цепочка/кластер: {table.max_cluster()}")
        summary.append((method, table.insert_collisions, table.avg_probes(), table.max_cluster()))

        # удаление и повторный поиск
        removed = table.delete(3072)
        print(f"  удаление id=3072: {removed}; повторный поиск: {table.search(3072)}")

    print("\n=== Сравнение методов ===")
    print(f"{'метод':<10} | {'коллизии':>9} | {'ср. пробы':>9} | {'макс. кластер':>13}")
    print("-" * 52)
    for method, collisions, avg, cluster in summary:
        print(f"{method:<10} | {collisions:>9} | {avg:>9.2f} | {cluster:>13}")

if __name__ == "__main__":
    demo()
