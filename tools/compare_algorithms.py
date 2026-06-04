from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"

TOOL_ORDER = ("pyexz3", "crosshair", "mini")
TOOL_LABELS = {
    "pyexz3": "PyExZ3",
    "crosshair": "CrossHair",
    "mini": "Разработанный прототип",
}
SCALAR_METRICS = (
    "time_seconds",
    "python_heap_peak_mib",
    "peak_rss_mib",
    "generated_tests",
    "branch_coverage_percent",
)


def _run_suite(tool: str, suite: str, max_iterations: int) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "run_suite.py"),
        "--tool",
        tool,
        "--suite",
        suite,
        "--max-iterations",
        str(max_iterations),
    ]
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(completed.stdout)


def _mean(values: list[float | int]) -> float:
    return round(float(statistics.mean(values)), 4)


def _stdev(values: list[float | int]) -> float:
    return round(float(statistics.pstdev(values)), 4)


def _aggregate_tool_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    means = {metric: _mean([run[metric] for run in runs]) for metric in SCALAR_METRICS}
    stdevs = {metric: _stdev([run[metric] for run in runs]) for metric in SCALAR_METRICS}

    benchmark_names = [row["benchmark"] for row in runs[0]["benchmarks"]]
    benchmark_rows: list[dict[str, Any]] = []
    for benchmark_name in benchmark_names:
        matching_rows = [
            row
            for run in runs
            for row in run["benchmarks"]
            if row["benchmark"] == benchmark_name
        ]
        sample = matching_rows[0]
        benchmark_rows.append(
            {
                "benchmark": benchmark_name,
                "family": sample["family"],
                "scenario": sample["scenario"],
                "generated_tests_mean": _mean([row["generated_tests"] for row in matching_rows]),
                "covered_branches": sample["covered_branches"],
                "branch_coverage_mean": _mean([row["branch_coverage"] for row in matching_rows]),
                "examples": sample["examples"],
            }
        )

    return {
        "means": means,
        "stdevs": stdevs,
        "skipped_benchmarks": runs[0].get("skipped_benchmarks", []),
        "benchmarks": benchmark_rows,
        "raw_runs": runs,
    }


def _full_coverage_count(tool_summary: dict[str, Any]) -> str:
    total = len(tool_summary["benchmarks"])
    full = sum(1 for row in tool_summary["benchmarks"] if row["branch_coverage_mean"] == 100.0)
    return f"{full}/{total}"


def _format_number(value: Any) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def _print_table(headers: list[str], rows: list[list[Any]]) -> None:
    string_rows = [[_format_number(cell) for cell in row] for row in rows]
    widths = [
        max(len(header), *(len(row[index]) for row in string_rows))
        for index, header in enumerate(headers)
    ]
    separator = "-+-".join("-" * width for width in widths)
    print(" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print(separator)
    for row in string_rows:
        print(" | ".join(row[index].ljust(widths[index]) for index in range(len(headers))))


def _print_summary(payload: dict[str, Any], output_path: Path) -> None:
    suite = payload["config"]["suite"]
    runs = payload["config"]["runs"]
    max_iterations = payload["config"]["max_iterations"]
    print()
    print(f"Сравнение алгоритмов: suite={suite}, runs={runs}, max_iterations={max_iterations}")
    print()

    summary_rows = []
    skipped_rows = []
    for tool in TOOL_ORDER:
        tool_summary = payload["tools"][tool]
        means = tool_summary["means"]
        skipped = tool_summary["skipped_benchmarks"]
        if skipped:
            skipped_rows.append([TOOL_LABELS[tool], ", ".join(skipped)])
        summary_rows.append(
            [
                TOOL_LABELS[tool],
                f"{means['time_seconds']:.2f}",
                f"{means['python_heap_peak_mib']:.2f}",
                f"{means['peak_rss_mib']:.2f}",
                int(means["generated_tests"]),
                f"{means['branch_coverage_percent']:.1f}",
                _full_coverage_count(tool_summary),
            ]
        )
    _print_table(
        [
            "Инструмент",
            "Время, с",
            "Heap, MiB",
            "Peak RSS, MiB",
            "Тесты",
            "Покрытие, %",
            "Полн. покрыто",
        ],
        summary_rows,
    )

    if skipped_rows:
        print()
        print("Пропущенные benchmark-функции")
        _print_table(["Инструмент", "Пропущено"], skipped_rows)

    print()
    print("Покрытие по benchmark-функциям")
    benchmark_rows = []
    for tool in TOOL_ORDER:
        for row in payload["tools"][tool]["benchmarks"]:
            benchmark_rows.append(
                [
                    TOOL_LABELS[tool],
                    row["benchmark"],
                    row["generated_tests_mean"],
                    row["covered_branches"],
                    row["branch_coverage_mean"],
                ]
            )
    _print_table(
        ["Инструмент", "Benchmark", "Тесты", "Покрыто ветвей", "Покрытие, %"],
        benchmark_rows,
    )

    print()
    print(f"JSON сохранен: {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Запускает PyExZ3, CrossHair и Z3-прототип и выводит сравнение."
    )
    parser.add_argument("--suite", choices=("all", "micro", "industrial"), default="all")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--max-iterations", type=int, default=20)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "algorithm_comparison.json",
        help="Путь к JSON-файлу с результатами сравнения.",
    )
    args = parser.parse_args()

    if args.runs < 1:
        raise SystemExit("--runs must be >= 1")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tools_payload: dict[str, Any] = {}
    for tool in TOOL_ORDER:
        print(f"Запуск {TOOL_LABELS[tool]}...", file=sys.stderr)
        runs = [_run_suite(tool, args.suite, args.max_iterations) for _ in range(args.runs)]
        tools_payload[tool] = _aggregate_tool_runs(runs)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config": {
            "suite": args.suite,
            "runs": args.runs,
            "max_iterations": args.max_iterations,
            "tools": list(TOOL_ORDER),
        },
        "tools": tools_payload,
    }

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _print_summary(payload, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
