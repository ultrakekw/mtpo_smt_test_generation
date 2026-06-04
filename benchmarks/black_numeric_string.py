from __future__ import annotations


"""Benchmark extracted from Black numeric-literal normalization logic.

Source project: Black 25.11.0
Source function: black.numerics.format_float_or_int_string

The original function distinguishes strings with and without a decimal point and
normalizes missing integer or fractional parts. The benchmark preserves the
same branching structure while returning path classes instead of formatted text.
"""


BRANCHES = {
    "b1_t",
    "b1_f",
    "b2_t",
    "b2_f",
    "b3_t",
    "b3_f",
}


def black_numeric_string(text: str) -> int:
    if "." not in text:
        return 0
    if text.startswith("."):
        return 1
    if text.endswith("."):
        return 2
    return 3


black_numeric_string.symbolic_args = {
    "text": "",
}


def collect_branches(text: str) -> set[str]:
    covered: set[str] = set()
    if "." not in text:
        covered.add("b1_t")
        return covered
    covered.add("b1_f")
    if text.startswith("."):
        covered.add("b2_t")
        return covered
    covered.add("b2_f")
    if text.endswith("."):
        covered.add("b3_t")
        return covered
    covered.add("b3_f")
    return covered
