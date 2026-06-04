from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"


SUITE_TOOLS = {
    "micro": ("pyexz3", "crosshair", "mini"),
    "industrial": ("pyexz3", "crosshair", "mini"),
}


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


def _aggregate_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    scalar_keys = [
        "time_seconds",
        "python_heap_peak_mib",
        "peak_rss_mib",
        "generated_tests",
        "branch_coverage_percent",
    ]
    means = {
        key: round(statistics.mean(run[key] for run in runs), 4)
        for key in scalar_keys
    }
    stdevs = {
        key: round(statistics.pstdev(run[key] for run in runs), 4)
        for key in scalar_keys
    }

    benchmark_names = [row["benchmark"] for row in runs[0]["benchmarks"]]
    benchmark_rows: list[dict[str, Any]] = []
    for benchmark_name in benchmark_names:
        matching_rows = []
        for run in runs:
            for row in run["benchmarks"]:
                if row["benchmark"] == benchmark_name:
                    matching_rows.append(row)
                    break
        sample = matching_rows[0]
        benchmark_rows.append(
            {
                "benchmark": benchmark_name,
                "family": sample["family"],
                "scenario": sample["scenario"],
                "generated_tests": round(statistics.mean(row["generated_tests"] for row in matching_rows), 2),
                "covered_branches": sample["covered_branches"],
                "branch_coverage": round(statistics.mean(row["branch_coverage"] for row in matching_rows), 2),
                "examples": sample["examples"],
            }
        )

    return {
        "means": means,
        "stdevs": stdevs,
        "benchmarks": benchmark_rows,
        "skipped_benchmarks": runs[0].get("skipped_benchmarks", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--max-iterations", type=int, default=20)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    combined_summary: dict[str, Any] = {}
    for suite, tools in SUITE_TOOLS.items():
        suite_summary: dict[str, Any] = {}
        for tool in tools:
            runs: list[dict[str, Any]] = []
            for run_index in range(1, args.runs + 1):
                payload = _run_suite(tool, suite, args.max_iterations)
                output_path = RESULTS_DIR / f"{suite}_{tool}_run_{run_index}.json"
                output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                runs.append(payload)
            suite_summary[tool] = _aggregate_runs(runs)
        combined_summary[suite] = suite_summary
        suite_output = RESULTS_DIR / f"{suite}_summary.json"
        suite_output.write_text(json.dumps(suite_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    combined_output = RESULTS_DIR / "extended_summary.json"
    combined_output.write_text(json.dumps(combined_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(combined_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
