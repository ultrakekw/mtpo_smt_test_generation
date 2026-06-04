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
    "b6_t",
    "b6_f",
}


def industrial_release_channel(ref_name: str, force: bool) -> int:
    if ref_name.startswith("release/"):
        if force:
            return 1
        if ref_name == "release/hotfix":
            return 2
        return 3
    if ref_name.startswith("feature/"):
        return 4
    if ref_name == "main":
        if force:
            return 5
        return 6
    return 0


industrial_release_channel.symbolic_args = {
    "ref_name": "",
    "force": 0,
}


def collect_branches(ref_name: str, force: bool) -> set[str]:
    covered: set[str] = set()
    if ref_name.startswith("release/"):
        covered.add("b1_t")
        if force:
            covered.add("b2_t")
            return covered
        covered.add("b2_f")
        if ref_name == "release/hotfix":
            covered.add("b3_t")
            return covered
        covered.add("b3_f")
        return covered
    covered.add("b1_f")
    if ref_name.startswith("feature/"):
        covered.add("b4_t")
        return covered
    covered.add("b4_f")
    if ref_name == "main":
        covered.add("b5_t")
        if force:
            covered.add("b6_t")
            return covered
        covered.add("b6_f")
        return covered
    covered.add("b5_f")
    return covered
