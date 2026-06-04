from __future__ import annotations

import argparse
import contextlib
import io
import ast
import json
import os
import platform
import resource
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.catalog import BENCHMARKS, Benchmark
from tools.miniconcolic import explore as explore_miniconcolic

PYEXZ3_ROOT = ROOT / "deps" / "PyExZ3"


def _normalize_ru_maxrss(raw_value: int) -> float:
    if platform.system() == "Darwin":
        return raw_value / (1024 * 1024)
    return (raw_value * 1024) / (1024 * 1024)


def _normalize_input_vector(benchmark: Benchmark, raw_inputs: dict[str, Any]) -> dict[str, Any]:
    parameter_map = benchmark.parameter_map()
    return {
        name: parameter_map[name].coerce(raw_inputs[name])
        for name in benchmark.argument_names
    }


def _measure_coverage(benchmark: Benchmark, test_vectors: list[dict[str, Any]]) -> tuple[int, float]:
    covered: set[str] = set()
    collector = benchmark.load_branch_collector()
    for vector in test_vectors:
        arguments = [vector[name] for name in benchmark.argument_names]
        covered.update(collector(*arguments))
    return len(covered), len(covered) / benchmark.total_branches


def _run_miniconcolic(benchmark: Benchmark, max_iterations: int) -> list[dict[str, Any]]:
    return explore_miniconcolic(benchmark.load_function(), benchmark.parameters, max_iterations=max_iterations)


def _run_pyexz3(benchmark: Benchmark, max_iterations: int) -> list[dict[str, Any]]:
    if str(PYEXZ3_ROOT) not in sys.path:
        sys.path.insert(0, str(PYEXZ3_ROOT))
    from symbolic.explore import ExplorationEngine
    from symbolic.loader import loaderFactory

    app = loaderFactory(str(ROOT / "benchmarks" / benchmark.file_name), benchmark.function_name)
    if app is None:
        raise RuntimeError(f"PyExZ3 loader failed for {benchmark.name}")
    engine = ExplorationEngine(app.createInvocation(), solver="z3")
    with contextlib.redirect_stdout(io.StringIO()):
        generated_inputs, return_values, _path = engine.explore(max_iterations)
    results: list[dict[str, Any]] = []
    for index, input_vector in enumerate(generated_inputs):
        if isinstance(input_vector, dict):
            raw_inputs = {name: input_vector[name] for name in benchmark.argument_names}
        else:
            raw_inputs = {name: value for name, value in input_vector}
        concrete_inputs = _normalize_input_vector(benchmark, raw_inputs)
        result_value = return_values[index] if index < len(return_values) else None
        if not isinstance(result_value, (type(None), bool, int, float, str)):
            result_value = repr(result_value)
        results.append(
            {
                "inputs": concrete_inputs,
                "result": result_value,
                "path_length": None,
            }
        )
    return results


def _run_crosshair(benchmark: Benchmark, max_iterations: int) -> list[dict[str, Any]]:
    cmd = [
        str(ROOT / ".venv" / "bin" / "crosshair"),
        "cover",
        f"{benchmark.module_name}.{benchmark.function_name}",
        "--example_output_format=ARG_DICTIONARY",
        "--max_uninteresting_iterations",
        str(max_iterations),
    ]
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    results: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        raw_inputs = ast.literal_eval(line)
        concrete_inputs = _normalize_input_vector(benchmark, raw_inputs)
        results.append({"inputs": concrete_inputs, "result": None, "path_length": None})
    return results


RUNNERS = {
    "mini": _run_miniconcolic,
    "pyexz3": _run_pyexz3,
    "crosshair": _run_crosshair,
}


def _select_benchmarks(suite: str, tool: str) -> tuple[list[Benchmark], list[str]]:
    compatible = [benchmark for benchmark in BENCHMARKS if tool in benchmark.supported_tools]
    if suite == "all":
        selected = compatible
    else:
        selected = [benchmark for benchmark in compatible if benchmark.family == suite]
    skipped = [
        benchmark.name
        for benchmark in BENCHMARKS
        if suite in {"all", benchmark.family} and tool not in benchmark.supported_tools
    ]
    return selected, skipped


def _unique_vectors(vectors: Iterable[dict[str, Any]]) -> int:
    return len({tuple(sorted(vector.items())) for vector in vectors})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", choices=sorted(RUNNERS), required=True)
    parser.add_argument("--max-iterations", type=int, default=20)
    parser.add_argument("--suite", choices=("all", "micro", "industrial"), default="all")
    args = parser.parse_args()

    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    selected_benchmarks, skipped_benchmarks = _select_benchmarks(args.suite, args.tool)

    tracemalloc.start()
    started = time.perf_counter()
    benchmark_rows: list[dict[str, Any]] = []
    total_tests = 0
    covered_branches = 0
    total_branches = 0

    for benchmark in selected_benchmarks:
        generated = RUNNERS[args.tool](benchmark, args.max_iterations)
        vectors = [item["inputs"] for item in generated]
        covered_count, coverage_ratio = _measure_coverage(benchmark, vectors)
        total_tests += _unique_vectors(vectors)
        covered_branches += covered_count
        total_branches += benchmark.total_branches
        benchmark_rows.append(
            {
                "benchmark": benchmark.name,
                "family": benchmark.family,
                "scenario": benchmark.scenario,
                "generated_tests": len(generated),
                "covered_branches": covered_count,
                "branch_coverage": round(coverage_ratio * 100, 2),
                "examples": generated,
            }
        )

    elapsed = time.perf_counter() - started
    _current, peak_heap = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    max_rss = _normalize_ru_maxrss(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    coverage_percent = 0.0 if total_branches == 0 else round((covered_branches / total_branches) * 100, 2)

    payload = {
        "tool": args.tool,
        "suite": args.suite,
        "skipped_benchmarks": skipped_benchmarks,
        "time_seconds": round(elapsed, 4),
        "python_heap_peak_mib": round(peak_heap / (1024 * 1024), 3),
        "peak_rss_mib": round(max_rss, 3),
        "generated_tests": total_tests,
        "branch_coverage_percent": coverage_percent,
        "benchmarks": benchmark_rows,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
