from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

MODULE_PATH = Path(__file__).with_name("network_analysis.py")
SPEC = importlib.util.spec_from_file_location("network_analysis", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
network_analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(network_analysis)


def _network_with_three_winding_transformer() -> SimpleNamespace:
    empty_results = pd.DataFrame(
        columns=["loading_percent", "pl_mw", "ql_mvar"], dtype=float
    )
    return SimpleNamespace(
        name="three-winding-regression",
        converged=True,
        bus=pd.DataFrame(index=[0, 1, 2]),
        line=pd.DataFrame(index=[]),
        trafo=pd.DataFrame(index=[]),
        trafo3w=pd.DataFrame({"in_service": [True]}, index=[17]),
        load=pd.DataFrame(index=[]),
        gen=pd.DataFrame(index=[]),
        ext_grid=pd.DataFrame(index=[0]),
        res_bus=pd.DataFrame({"vm_pu": [1.0, 1.01, 0.99]}, index=[0, 1, 2]),
        res_line=empty_results.copy(),
        res_trafo=empty_results.copy(),
        res_trafo3w=pd.DataFrame(
            {"loading_percent": [120.0], "pl_mw": [0.3], "ql_mvar": [0.1]},
            index=[17],
        ),
        res_gen=pd.DataFrame({"p_mw": []}, dtype=float),
        res_ext_grid=pd.DataFrame({"p_mw": [10.0]}, index=[0]),
    )


def test_three_winding_transformer_overload_is_reported() -> None:
    net = _network_with_three_winding_transformer()

    result = network_analysis.check_violations(net)

    assert result["has_violations"] is True
    assert result["loading"]["overloaded_trafo3ws"] == [17]
    assert result["loading"]["max_trafo3w_loading"] == 120.0


def test_three_winding_transformer_losses_are_included_in_totals() -> None:
    net = _network_with_three_winding_transformer()

    result = network_analysis.calculate_losses(net)
    summary = network_analysis.summarize_network(net)

    assert result["trafo3w_losses_mw"] == 0.3
    assert result["trafo3w_losses_mvar"] == 0.1
    assert result["total_losses_mw"] == 0.3
    assert result["total_losses_mvar"] == 0.1
    assert summary["elements"]["three_winding_transformers"] == 1
    assert summary["results"]["max_trafo3w_loading"] == 120.0
