"""Проверки для программ по графам и хеш-таблицам.

Запуск: python3 test_graphs_hash.py
Тесты дергают сами скрипты через subprocess и смотрят, что в выводе есть
ожидаемые числа. Так проверяется не только код функций, но и то, что
программа целиком доходит до конца.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run_script(name: str) -> str:
    result = subprocess.run(
        [sys.executable, str(HERE / name)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise AssertionError(f"{name} упал: {result.stderr.strip()[:400]}")
    return result.stdout


class CampusGraphTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.out = run_script("campus_graph.py")

    def test_dijkstra_gives_distance_to_parking(self):
        self.assertIn("Общежитие → Парковка", self.out)
        self.assertIn("= 600 м", self.out)

    def test_floyd_warshall_builds_matrix(self):
        self.assertIn("Флойд", self.out)
        distances = re.findall(r"\b(710|600|490)\b", self.out)
        self.assertTrue(distances, "в выводе нет расстояний из матрицы Флойда")

    def test_diameter_and_center_present(self):
        self.assertIn("Диаметр сети: 710 м", self.out)
        self.assertIn("радиус: 490 м", self.out)
        self.assertIn("центр: Столовая", self.out)

    def test_both_traversals_printed(self):
        self.assertIn("BFS", self.out)
        self.assertIn("DFS", self.out)
        self.assertIn("Дейкстра", self.out)

    def test_eight_vertices_twelve_edges(self):
        self.assertIn("8", self.out)
        self.assertIn("12", self.out)


class HashRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.out = run_script("hash_registry.py")

    def test_all_four_methods_compared(self):
        for method in ("chaining", "linear", "quadratic", "double"):
            self.assertIn(method, self.out)

    def test_collision_count_is_seven(self):
        rows = [line for line in self.out.splitlines() if line.strip().startswith("chaining")]
        self.assertTrue(rows, "нет строки сравнения для chaining")
        self.assertIn("7", rows[0])

    def test_average_probes_present(self):
        numbers = re.findall(r"\b\d\.\d{2}\b", self.out)
        for expected in ("1.00", "2.36", "1.88", "1.68"):
            self.assertIn(expected, numbers)

    def test_longest_cluster(self):
        self.assertIn("максимальная цепочка/кластер: 4", self.out)

    def test_delete_and_search_after_delete(self):
        self.assertIn("удаление id=3072: True", self.out)
        self.assertIn("повторный поиск: None", self.out)

    def test_equipment_has_required_fields(self):
        sys.path.insert(0, str(HERE))
        from hash_registry import Equipment

        fields = set(Equipment.__dataclass_fields__)
        self.assertEqual(fields, {"id", "name", "room", "status"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
