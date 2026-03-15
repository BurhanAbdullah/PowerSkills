---
name: pypsa
description: Progressive-disclosure workflow for PyPSA studies. Use when the user asks to load or build a PyPSA network, inspect components, run power flow, solve OPF, or perform investment optimization, and when the agent should expose network inspection and feasibility steps before large optimization studies.
---

# PyPSA workflow

Start by creating or loading a named network handle. Use network inspection before optimization, and use operational optimization before investment optimization.

## Default tool ladder
1. `load_network(file_path)` or `create_network(...)` to create the active network handle.
2. `get_network_info(network_name)` and `get_component_details(...)` to understand topology, assets, and time series.
3. `run_power_flow(network_name, linear=False)` for feasibility checks.
4. `optimize_network(network_name, ...)` for dispatch or operational studies.
5. `optimize_investment(network_name, ...)` for expansion questions.
6. `import_from_csv_folder(...)` or `export_to_csv_folder(...)` once the network state is worth moving.

## Working rules
- Do not jump straight into expansion optimization when a dispatch study can answer the question.
- Use AC or DC power flow to sanity-check a network before relying on optimization outputs.
- Treat PyPSA as a planning and scheduling engine, not the final authority on detailed reactive mitigation.
- Hand off infeasibility, curtailment, and reserve issues to `operations-planning-mitigation`.

## Local assets in this repo
- `PyPSA/case39.nc` for a ready test network.
- `PyPSA/scripts/network_analysis.py` for inspection.
- `PyPSA/scripts/optimization_analysis.py` for OPF result review.
- `PyPSA/scripts/expansion_analysis.py` for capacity expansion studies.
- `PyPSA/scripts/contingency_analysis.py` for local N-1 screening outside PowerMCP.

## Deliver
- The network handle and study type.
- The main feasibility or cost result.
- Whether the next step is mitigation, AC validation, or a larger optimization.
