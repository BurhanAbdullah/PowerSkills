from __future__ import annotations

from types import SimpleNamespace

from optimization_analysis import check_optimization_status


def test_pypsa_1x_success_tuple_is_used() -> None:
    network = SimpleNamespace(objective=123.0)

    result = check_optimization_status(network, ("ok", "optimal"))

    assert result["optimized"] is True
    assert result["converged"] is True
    assert result["status"] == "ok"
    assert result["termination_condition"] == "optimal"


def test_pypsa_1x_failed_termination_is_not_reported_as_converged() -> None:
    network = SimpleNamespace(objective=123.0)

    result = check_optimization_status(network, ("ok", "infeasible"))

    assert result["converged"] is False
    assert result["termination_condition"] == "infeasible"


def test_unknown_status_fails_closed_even_when_objective_exists() -> None:
    network = SimpleNamespace(objective=123.0)

    result = check_optimization_status(network)

    assert result["optimized"] is True
    assert result["converged"] is False
    assert result["status"] == "unknown"


def test_legacy_status_dictionary_remains_supported() -> None:
    network = SimpleNamespace(
        objective=123.0,
        status={"status": "ok", "solver": "highs"},
    )

    result = check_optimization_status(network)

    assert result["converged"] is True
    assert result["solver"] == "highs"


def test_legacy_failed_status_is_not_converged() -> None:
    network = SimpleNamespace(
        objective=123.0,
        status={"status": "warning", "solver": "highs"},
    )

    result = check_optimization_status(network)

    assert result["converged"] is False


def test_network_without_objective_is_not_run() -> None:
    result = check_optimization_status(SimpleNamespace(objective=None))

    assert result == {
        "optimized": False,
        "converged": False,
        "status": "not_run",
    }


def test_model_status_is_used_when_available() -> None:
    network = SimpleNamespace(
        objective=123.0,
        model=SimpleNamespace(status="ok", termination_condition="optimal"),
    )

    result = check_optimization_status(network)

    assert result["converged"] is True
