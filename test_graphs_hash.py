"""Проверки ответов из campus_graph.py и hash_registry.py."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script):
    result = subprocess.run([sys.executable, str(ROOT / script)], capture_output=True, text=True, check=True)
    return result.stdout


def test_graphs():
    out = run('campus_graph.py')
    assert 'Дейкстр' in out or 'dijkstra' in out.lower(), 'нет блока Дейкстры'
    assert 'Флойд' in out or 'floyd' in out.lower(), 'нет блока Флойда'
    assert 'центр' in out.lower(), 'не посчитан центр графа'


def test_hash():
    out = run('hash_registry.py')
    assert 'коллиз' in out.lower(), 'нет статистики коллизий'
    assert 'проб' in out.lower(), 'нет данных по пробам при поиске'


if __name__ == '__main__':
    test_graphs()
    test_hash()
    print('графы и хеш: ок')
