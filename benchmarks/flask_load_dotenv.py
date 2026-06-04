from __future__ import annotations


"""Benchmark extracted from Flask environment-flag parsing logic.

Source project: Flask 3.1.3
Source function: flask.helpers.get_load_dotenv

The original function reads an environment variable and lowercases it before
checking a small set of disabling values. The benchmark isolates the branch
logic into a pure function over explicit scalar arguments.
"""


BRANCHES = {
    "b1_t",
    "b1_f",
    "b2_t",
    "b2_f",
    "b3_t",
    "b3_f",
}


def flask_load_dotenv(val: str, default: bool) -> int:
    if not val:
        if default:
            return 1
        return 0
    if val == "0" or val == "false" or val == "no":
        return 2
    return 3


flask_load_dotenv.symbolic_args = {
    "val": "",
    "default": 1,
}


def collect_branches(val: str, default: bool) -> set[str]:
    covered: set[str] = set()
    if not val:
        covered.add("b1_t")
        if default:
            covered.add("b2_t")
            return covered
        covered.add("b2_f")
        return covered
    covered.add("b1_f")
    if val == "0" or val == "false" or val == "no":
        covered.add("b3_t")
        return covered
    covered.add("b3_f")
    return covered
