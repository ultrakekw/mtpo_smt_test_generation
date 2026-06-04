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
    "b7_t",
    "b7_f",
    "b8_t",
    "b8_f",
}


def industrial_route_policy(method: str, path: str, authenticated: bool) -> int:
    if method == "GET":
        if path.startswith("/health"):
            return 1
        if path.startswith("/admin"):
            if authenticated:
                return 2
            return 3
        return 4
    if method == "POST":
        if path == "/login":
            if authenticated:
                return 5
            return 6
        if path.startswith("/api/"):
            return 7
        return 8
    return 0


industrial_route_policy.symbolic_args = {
    "method": "",
    "path": "",
    "authenticated": 0,
}


def collect_branches(method: str, path: str, authenticated: bool) -> set[str]:
    covered: set[str] = set()
    if method == "GET":
        covered.add("b1_t")
        if path.startswith("/health"):
            covered.add("b2_t")
            return covered
        covered.add("b2_f")
        if path.startswith("/admin"):
            covered.add("b3_t")
            if authenticated:
                covered.add("b4_t")
                return covered
            covered.add("b4_f")
            return covered
        covered.add("b3_f")
        return covered
    covered.add("b1_f")
    if method == "POST":
        covered.add("b5_t")
        if path == "/login":
            covered.add("b6_t")
            if authenticated:
                covered.add("b7_t")
                return covered
            covered.add("b7_f")
            return covered
        covered.add("b6_f")
        if path.startswith("/api/"):
            covered.add("b8_t")
            return covered
        covered.add("b8_f")
        return covered
    covered.add("b5_f")
    return covered
