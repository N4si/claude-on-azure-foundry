"""
pytest suite — these tests FAIL against the original buggy_code.py.
After analyze.py applies Claude's fix, all three should pass.
"""

import pytest
from buggy_code import calculate_average, find_duplicates, merge_configs


def test_average_empty_list():
    """Empty list should return 0, not raise ZeroDivisionError."""
    assert calculate_average([]) == 0


def test_average_normal():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0


def test_find_duplicates_basic():
    result = find_duplicates(["a", "b", "a", "c", "b", "b"])
    assert sorted(result) == ["a", "b"]


def test_find_duplicates_none():
    assert find_duplicates([1, 2, 3]) == []


def test_merge_configs_no_mutation():
    """merge_configs must not mutate the base dict."""
    base = {"db": {"host": "localhost", "port": 5432}, "debug": False}
    original_base = {"db": {"host": "localhost", "port": 5432}, "debug": False}
    merge_configs(base, {"debug": True})
    assert base == original_base, "base dict was mutated"


def test_merge_configs_deep():
    base     = {"db": {"host": "localhost", "port": 5432}}
    override = {"db": {"port": 5433, "name": "prod"}}
    result   = merge_configs(base, override)
    assert result == {"db": {"host": "localhost", "port": 5433, "name": "prod"}}
