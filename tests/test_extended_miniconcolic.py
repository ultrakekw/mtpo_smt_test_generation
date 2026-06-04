from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.catalog import BENCHMARKS
from tools.miniconcolic import explore
from tools.run_suite import _measure_coverage, _run_pyexz3, _select_benchmarks


def _covered_branch_count(benchmark_name: str, vectors: list[dict[str, object]]) -> int:
    benchmark = next(item for item in BENCHMARKS if item.name == benchmark_name)
    collector = benchmark.load_branch_collector()
    covered: set[str] = set()
    for vector in vectors:
        args = [vector[name] for name in benchmark.argument_names]
        covered.update(collector(*args))
    return len(covered)


def test_miniconcolic_covers_industrial_string_and_bool_benchmarks() -> None:
    industrial = [benchmark for benchmark in BENCHMARKS if benchmark.family == "industrial"]
    for benchmark in industrial:
        results = explore(benchmark.load_function(), benchmark.parameters, max_iterations=20)
        vectors = [row["inputs"] for row in results]
        assert _covered_branch_count(benchmark.name, vectors) == benchmark.total_branches


def test_miniconcolic_preserves_runtime_types_for_extended_benchmarks() -> None:
    benchmark = next(item for item in BENCHMARKS if item.name == "flask_load_dotenv")
    results = explore(benchmark.load_function(), benchmark.parameters, max_iterations=20)
    assert any(isinstance(row["inputs"]["val"], str) for row in results)
    assert any(isinstance(row["inputs"]["default"], bool) for row in results)


def test_pyexz3_selection_includes_int_bool_and_string_industrial_benchmarks() -> None:
    selected, skipped = _select_benchmarks("all", "pyexz3")
    selected_names = {benchmark.name for benchmark in selected}
    assert "fastapi_status_body" in selected_names
    assert "flask_load_dotenv" in selected_names
    assert "pip_archive_suffix" in selected_names
    assert "werkzeug_server_name" in selected_names
    assert "black_numeric_string" in selected_names
    assert not skipped


def test_pyexz3_covers_industrial_int_bool_and_string_benchmarks() -> None:
    industrial = [benchmark for benchmark in BENCHMARKS if benchmark.family == "industrial"]
    for benchmark in industrial:
        generated = _run_pyexz3(benchmark, max_iterations=20)
        vectors = [row["inputs"] for row in generated]
        covered_count, coverage_ratio = _measure_coverage(benchmark, vectors)
        assert covered_count == benchmark.total_branches
        assert coverage_ratio == 1.0
