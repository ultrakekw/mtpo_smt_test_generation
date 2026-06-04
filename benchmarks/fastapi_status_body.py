from __future__ import annotations


"""Benchmark extracted from FastAPI's status-code body policy logic.

Source project: FastAPI 0.128.8
Source function: fastapi.utils.is_body_allowed_for_status_code

The original function also accepts wildcard strings such as "2XX" and None.
This benchmark keeps the numeric branch logic only, which is the part relevant
for SMT-based path exploration over scalar values.
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
}


def fastapi_status_body(status_code: int) -> int:
    if status_code < 200:
        return 0
    if status_code == 204:
        return 1
    if status_code == 205:
        return 2
    if status_code == 304:
        return 3
    return 4


fastapi_status_body.symbolic_args = {
    "status_code": 200,
}


def collect_branches(status_code: int) -> set[str]:
    covered: set[str] = set()
    if status_code < 200:
        covered.add("b1_t")
        return covered
    covered.add("b1_f")
    if status_code == 204:
        covered.add("b2_t")
        return covered
    covered.add("b2_f")
    if status_code == 205:
        covered.add("b3_t")
        return covered
    covered.add("b3_f")
    if status_code == 304:
        covered.add("b4_t")
        return covered
    covered.add("b4_f")
    return covered
