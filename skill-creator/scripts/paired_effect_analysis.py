#!/usr/bin/env python3
"""Paired effect-size analysis for skill-creator benchmark results."""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any


def _finite_number(value: Any, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric, got {value!r}")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite, got {value!r}")
    return value


def paired_differences(runs: list[dict[str, Any]], config_a: str,
                       config_b: str, metric: str) -> list[dict[str, Any]]:
    """Return matched A-minus-B differences keyed by (eval_id, run_number)."""
    if not config_a or not config_b:
        raise ValueError("configuration names must be non-empty")
    if config_a == config_b:
        raise ValueError("config-a and config-b must be different")
    keyed: dict[tuple[str, str], dict[str, float]] = {}
    for index, row in enumerate(runs):
        if not isinstance(row, dict):
            raise ValueError(f"runs[{index}] must be an object")
        config = row.get("configuration")
        if config not in (config_a, config_b):
            continue
        if "eval_id" not in row or "run_number" not in row:
            raise ValueError(f"runs[{index}] needs eval_id and run_number")
        key = (str(row["eval_id"]), str(row["run_number"]))
        values = keyed.setdefault(key, {})
        if config in values:
            raise ValueError(f"duplicate run for {config!r} at pair {key!r}")
        result = row.get("result")
        if not isinstance(result, dict) or metric not in result:
            raise ValueError(f"runs[{index}].result is missing metric {metric!r}")
        values[config] = _finite_number(
            result[metric], label=f"runs[{index}].result.{metric}"
        )
    pairs = []
    for key in sorted(keyed):
        values = keyed[key]
        if config_a in values and config_b in values:
            pairs.append({
                "eval_id": key[0], "run_number": key[1],
                "a": values[config_a], "b": values[config_b],
                "difference": values[config_a] - values[config_b],
            })
    if not pairs:
        raise ValueError(f"no matched runs found for {config_a!r} and {config_b!r}")
    return pairs


def _quantile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("cannot calculate a quantile of an empty sample")
    position = (len(values) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return values[lower]
    fraction = position - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


def analyze_paired_effect(pairs: list[dict[str, Any]], *,
                          bootstrap_samples: int = 10_000,
                          seed: int = 2026) -> dict[str, Any]:
    """Estimate paired mean effect, percentile-bootstrap 95% CI, and sign-flip p."""
    if isinstance(bootstrap_samples, bool) or bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be >= 1")
    differences = [
        _finite_number(pair["difference"], label="pair difference")
        for pair in pairs
    ]
    if not differences:
        raise ValueError("at least one matched pair is required")
    n = len(differences)
    mean_effect = statistics.fmean(differences)
    rng = random.Random(seed)
    boot_means = sorted(
        statistics.fmean(rng.choices(differences, k=n))
        for _ in range(bootstrap_samples)
    )
    extreme = 0
    for _ in range(bootstrap_samples):
        permuted = statistics.fmean(
            value if rng.getrandbits(1) else -value for value in differences
        )
        if abs(permuted) >= abs(mean_effect):
            extreme += 1
    return {
        "n_pairs": n,
        "mean_difference": mean_effect,
        "median_difference": statistics.median(differences),
        "stddev_difference": statistics.stdev(differences) if n > 1 else 0.0,
        "ci95_percentile": [_quantile(boot_means, 0.025), _quantile(boot_means, 0.975)],
        "sign_flip_p_value": (extreme + 1) / (bootstrap_samples + 1),
        "bootstrap_samples": bootstrap_samples,
        "seed": seed,
        "interpretation": "positive means configuration A is higher than configuration B",
    }


def analyze_benchmark(benchmark: dict[str, Any], config_a: str, config_b: str,
                      metric: str, *, bootstrap_samples: int = 10_000,
                      seed: int = 2026) -> dict[str, Any]:
    runs = benchmark.get("runs")
    if not isinstance(runs, list):
        raise ValueError("benchmark must contain a 'runs' list")
    pairs = paired_differences(runs, config_a, config_b, metric)
    result = analyze_paired_effect(
        pairs, bootstrap_samples=bootstrap_samples, seed=seed
    )
    result.update({
        "metric": metric,
        "configuration_a": config_a,
        "configuration_b": config_b,
        "matched_pairs": [
            {"eval_id": p["eval_id"], "run_number": p["run_number"]}
            for p in pairs
        ],
        "input_run_rows": len(runs),
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate paired skill benchmark effects with uncertainty."
    )
    parser.add_argument("benchmark_json", type=Path)
    parser.add_argument("--config-a", required=True)
    parser.add_argument("--config-b", required=True)
    parser.add_argument("--metric", default="pass_rate")
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        benchmark = json.loads(args.benchmark_json.read_text(encoding="utf-8"))
        result = analyze_benchmark(
            benchmark, args.config_a, args.config_b, args.metric,
            bootstrap_samples=args.bootstrap_samples, seed=args.seed,
        )
        rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
