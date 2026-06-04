from __future__ import annotations


BRANCHES = {"b1_t", "b1_f", "b2_t", "b2_f", "b3_t", "b3_f", "b4_t", "b4_f", "b5_t", "b5_f", "b6_t", "b6_f"}


def loop_bucket(x: int, y: int) -> int:
    if x < 0:
        return -1
    if y < 0:
        return -1
    steps = 0
    while x > 0 and y > 0 and steps < 3:
        if x > y:
            x -= 2
        else:
            y -= 2
        steps += 1
    if steps == 0:
        return 0
    if x == y:
        return 1
    return 2


def collect_branches(x: int, y: int) -> set[str]:
    covered: set[str] = set()
    if x < 0:
        covered.add("b1_t")
        return covered
    covered.add("b1_f")
    if y < 0:
        covered.add("b2_t")
        return covered
    covered.add("b2_f")
    if x > 0 and y > 0 and 0 < 3:
        covered.add("b3_t")
        if x > y:
            covered.add("b4_t")
            x -= 2
        else:
            covered.add("b4_f")
            y -= 2
        steps = 1
        while x > 0 and y > 0 and steps < 3:
            if x > y:
                x -= 2
            else:
                y -= 2
            steps += 1
    else:
        covered.add("b3_f")
        steps = 0
    if steps == 0:
        covered.add("b5_t")
        return covered
    covered.add("b5_f")
    if x == y:
        covered.add("b6_t")
        return covered
    covered.add("b6_f")
    return covered
