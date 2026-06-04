from __future__ import annotations


BRANCHES = {"b1_t", "b1_f", "b2_t", "b2_f", "b3_t", "b3_f", "b4_t", "b4_f"}


def pair_relation(x: int, y: int) -> int:
    if x + y == 10:
        if x > y:
            return 1
        return 2
    if x - y > 8:
        return 3
    if x * y == 12:
        return 4
    return 0


def collect_branches(x: int, y: int) -> set[str]:
    covered: set[str] = set()
    if x + y == 10:
        covered.add("b1_t")
        if x > y:
            covered.add("b2_t")
            return covered
        covered.add("b2_f")
        return covered
    covered.add("b1_f")
    if x - y > 8:
        covered.add("b3_t")
        return covered
    covered.add("b3_f")
    if x * y == 12:
        covered.add("b4_t")
        return covered
    covered.add("b4_f")
    return covered
