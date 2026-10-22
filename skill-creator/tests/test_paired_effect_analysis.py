import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "paired_effect_analysis.py"
SPEC = importlib.util.spec_from_file_location("paired_effect_analysis", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def rows():
    return [
        {"eval_id": 1, "configuration": "with_skill", "run_number": 1,
         "result": {"pass_rate": 0.9, "time_seconds": 4}},
        {"eval_id": 1, "configuration": "without_skill", "run_number": 1,
         "result": {"pass_rate": 0.7, "time_seconds": 5}},
        {"eval_id": 1, "configuration": "with_skill", "run_number": 2,
         "result": {"pass_rate": 0.8, "time_seconds": 6}},
        {"eval_id": 1, "configuration": "without_skill", "run_number": 2,
         "result": {"pass_rate": 0.6, "time_seconds": 7}},
    ]


def test_pairs_match_eval_and_run_and_use_a_minus_b():
    pairs = MODULE.paired_differences(rows(), "with_skill", "without_skill", "pass_rate")
    assert all(math.isclose(p["difference"], 0.2) for p in pairs)
    assert pairs[0]["eval_id"] == "1"


def test_unmatched_runs_are_excluded():
    data = rows() + [{"eval_id": 2, "configuration": "with_skill",
                      "run_number": 1, "result": {"pass_rate": 1.0}}]
    assert len(MODULE.paired_differences(
        data, "with_skill", "without_skill", "pass_rate")) == 2


def test_no_matched_pairs_fails_loudly():
    try:
        MODULE.paired_differences([rows()[0]], "with_skill", "without_skill", "pass_rate")
    except ValueError as exc:
        assert "no matched runs" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_duplicate_pair_is_rejected():
    try:
        MODULE.paired_differences(rows() + [rows()[0]], "with_skill", "without_skill", "pass_rate")
    except ValueError as exc:
        assert "duplicate run" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_same_configuration_is_rejected():
    try:
        MODULE.paired_differences(rows(), "with_skill", "with_skill", "pass_rate")
    except ValueError as exc:
        assert "must be different" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_missing_metric_is_rejected():
    try:
        MODULE.paired_differences(
            [{"eval_id": 1, "run_number": 1, "configuration": "A", "result": {}}],
            "A", "B", "pass_rate")
    except ValueError as exc:
        assert "missing metric" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_boolean_nan_and_infinity_are_rejected():
    for value in (True, float("nan"), float("inf")):
        data = [{"eval_id": 1, "run_number": 1, "configuration": "A",
                 "result": {"m": value}},
                {"eval_id": 1, "run_number": 1, "configuration": "B",
                 "result": {"m": 0}}]
        try:
            MODULE.paired_differences(data, "A", "B", "m")
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected invalid value {value!r} to fail")


def test_analysis_is_reproducible_and_reports_ci_and_p_value():
    pairs = MODULE.paired_differences(rows(), "with_skill", "without_skill", "pass_rate")
    a = MODULE.analyze_paired_effect(pairs, bootstrap_samples=500, seed=17)
    b = MODULE.analyze_paired_effect(pairs, bootstrap_samples=500, seed=17)
    assert a == b
    assert math.isclose(a["mean_difference"], 0.2)
    assert a["n_pairs"] == 2
    assert a["ci95_percentile"][0] <= 0.2 + 1e-12
    assert a["ci95_percentile"][1] >= 0.2 - 1e-12
    assert 0 < a["sign_flip_p_value"] <= 1


def test_single_pair_has_zero_sample_standard_deviation():
    result = MODULE.analyze_paired_effect([{"difference": 0.25}], bootstrap_samples=50)
    assert result["stddev_difference"] == 0.0
    assert result["mean_difference"] == 0.25


def test_invalid_bootstrap_count_is_rejected():
    try:
        MODULE.analyze_paired_effect([{"difference": 0.1}], bootstrap_samples=0)
    except ValueError as exc:
        assert ">= 1" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_cli_writes_json_result(tmp_path):
    source, output = tmp_path / "benchmark.json", tmp_path / "effect.json"
    source.write_text(json.dumps({"runs": rows()}), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(source), "--config-a", "with_skill",
         "--config-b", "without_skill", "--bootstrap-samples", "100",
         "--output", str(output)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["n_pairs"] == 2


def test_cli_returns_nonzero_for_invalid_benchmark(tmp_path):
    source = tmp_path / "benchmark.json"
    source.write_text('{"runs": []}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(source), "--config-a", "A",
         "--config-b", "B", "--bootstrap-samples", "20"],
        capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "no matched runs" in result.stderr
