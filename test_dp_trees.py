"""Проверки ответов из dp_tasks.py и tickets_tree.py."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script):
    result = subprocess.run([sys.executable, str(ROOT / script)], capture_output=True, text=True, check=True)
    return result.stdout


def test_dp():
    out = run('dp_tasks.py')
    assert '144' in out, 'нет ответа для n=10'
    assert '48620' in out, 'нет числа путей 10 на 10'
    assert '4' in out, 'нет длины возрастающей подпоследовательности'
    assert '7' in out, 'нет палиндрома для RACECAR'


def test_trees():
    out = run('tickets_tree.py')
    assert 'BST' in out or 'дерев' in out.lower(), 'нет вывода по дереву'
    assert 'куч' in out.lower() or 'heap' in out.lower(), 'нет вывода по куче'


if __name__ == '__main__':
    test_dp()
    test_trees()
    print('динамика и деревья: ок')
