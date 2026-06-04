from __future__ import annotations


BRANCHES = {
    "b1_t",
    "b1_f",
    "b2_t",
    "b2_f",
    "b3_t",
    "b3_f",
    "b4_t",
    "b4_f",
    "b5_t",
    "b5_f",
}


def industrial_filename_policy(name: str, allow_hidden: bool) -> int:
    if not name:
        return -1
    if name.startswith("."):
        if allow_hidden:
            return 1
        return 2
    if name == "Dockerfile":
        return 3
    if name.startswith("tmp_"):
        return 4
    return 0


industrial_filename_policy.symbolic_args = {
    "name": "",
    "allow_hidden": 0,
}


def collect_branches(name: str, allow_hidden: bool) -> set[str]:
    covered: set[str] = set()
    if not name:
        covered.add("b1_t")
        return covered
    covered.add("b1_f")
    if name.startswith("."):
        covered.add("b2_t")
        if allow_hidden:
            covered.add("b3_t")
            return covered
        covered.add("b3_f")
        return covered
    covered.add("b2_f")
    if name == "Dockerfile":
        covered.add("b4_t")
        return covered
    covered.add("b4_f")
    if name.startswith("tmp_"):
        covered.add("b5_t")
        return covered
    covered.add("b5_f")
    return covered
