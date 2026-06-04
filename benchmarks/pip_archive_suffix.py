from __future__ import annotations


"""Benchmark extracted from pip archive-file detection rules.

Source project: pip 26.0.1
Source function: pip._internal.utils.filetypes.is_archive_file

The original helper computes a normalized extension and checks membership in
pip's archive extension groups. The benchmark keeps those real extension groups
but rewrites the check as a pure suffix decision tree over a filename string.
"""


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


def pip_archive_suffix(name: str) -> int:
    if not name:
        return -1
    if name.endswith(".whl") or name.endswith(".zip"):
        return 1
    if name.endswith(".tar.gz") or name.endswith(".tgz") or name.endswith(".tar"):
        return 2
    if name.endswith(".tar.bz2") or name.endswith(".tbz"):
        return 3
    if (
        name.endswith(".tar.xz")
        or name.endswith(".txz")
        or name.endswith(".tlz")
        or name.endswith(".tar.lz")
        or name.endswith(".tar.lzma")
    ):
        return 4
    return 0


pip_archive_suffix.symbolic_args = {
    "name": "",
}


def collect_branches(name: str) -> set[str]:
    covered: set[str] = set()
    if not name:
        covered.add("b1_t")
        return covered
    covered.add("b1_f")
    if name.endswith(".whl") or name.endswith(".zip"):
        covered.add("b2_t")
        return covered
    covered.add("b2_f")
    if name.endswith(".tar.gz") or name.endswith(".tgz") or name.endswith(".tar"):
        covered.add("b3_t")
        return covered
    covered.add("b3_f")
    if name.endswith(".tar.bz2") or name.endswith(".tbz"):
        covered.add("b4_t")
        return covered
    covered.add("b4_f")
    if (
        name.endswith(".tar.xz")
        or name.endswith(".txz")
        or name.endswith(".tlz")
        or name.endswith(".tar.lz")
        or name.endswith(".tar.lzma")
    ):
        covered.add("b5_t")
        return covered
    covered.add("b5_f")
    return covered
