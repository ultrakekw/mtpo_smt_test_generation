from __future__ import annotations


BRANCHES = {"b1_t", "b1_f", "b2_t", "b2_f", "b3_t", "b3_f"}


def threshold(x: int) -> int:
    if x < -5:
        return -1
    if x == 7:
        return 2
    if x > 20:
        return 3
    return 0


def collect_branches(x: int) -> set[str]:
    covered: set[str] = set()
    if x < -5:
        covered.add("b1_t")
        return covered
    covered.add("b1_f")
    if x == 7:
        covered.add("b2_t")
        return covered
    covered.add("b2_f")
    if x > 20:
        covered.add("b3_t")
        return covered
    covered.add("b3_f")
    return covered
