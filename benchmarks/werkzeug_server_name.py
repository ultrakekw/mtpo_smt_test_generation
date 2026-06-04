from __future__ import annotations


"""Benchmark extracted from Werkzeug routing host normalization logic.

Source project: Werkzeug 3.1.8
Source file: werkzeug.routing.map

The original code lowercases the server name and strips the standard port for
HTTP/WS and HTTPS/WSS schemes. The benchmark isolates the routing-relevant
branch logic into a pure classifier.
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


def werkzeug_server_name(scheme: str, server_name: str) -> int:
    if scheme == "http" or scheme == "ws":
        if server_name.endswith(":80"):
            return 1
        return 2
    if scheme == "https" or scheme == "wss":
        if server_name.endswith(":443"):
            return 3
        return 4
    return 0


werkzeug_server_name.symbolic_args = {
    "scheme": "",
    "server_name": "",
}


def collect_branches(scheme: str, server_name: str) -> set[str]:
    covered: set[str] = set()
    if scheme == "http" or scheme == "ws":
        covered.add("b1_t")
        if server_name.endswith(":80"):
            covered.add("b2_t")
            return covered
        covered.add("b2_f")
        return covered
    covered.add("b1_f")
    if scheme == "https" or scheme == "wss":
        covered.add("b3_t")
        if server_name.endswith(":443"):
            covered.add("b4_t")
            return covered
        covered.add("b4_f")
        return covered
    covered.add("b3_f")
    return covered
