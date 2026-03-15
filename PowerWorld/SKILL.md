---
name: powerworld
description: Progressive-disclosure workflow for PowerWorld studies through PowerMCP. Use when the user asks to open a PowerWorld case, solve the base case, inspect flows or voltages, change model data, run contingency analysis, or compute sensitivity matrices, with basic operations exposed before advanced analytics.
---

# PowerWorld workflow

Expose PowerWorld tools in stages. Start with the base case. Move to contingencies or matrix analytics only after the operating condition is understood.

## Default tool ladder
1. `open_case(case_path)`
2. `run_powerflow(solution_method)`
3. `get_power_flow_results(object_type, additional_fields)` and `get_key_field_list(object_type)`
4. `change_and_confirm_params(...)` or `change_parameters_multiple_element(...)`
5. `analyze_contingencies(option, validate)`
6. `get_ybus()`, `get_jacobian()`, `get_lodf_matrix()`, `get_ptdf_matrix_fast()`, `to_graph()`, `determine_shortest_path()`, or `run_robustness_analysis()`

## Working rules
- Do not run contingencies before the base case solves cleanly.
- Ask for the monitored objects, limits, and fields before large result pulls.
- Use sensitivities or graph tools to rank candidate fixes before applying bulk changes.
- Confirm every model change by re-solving and checking the same monitored quantities.
- Use `voltage-violation-mitigation`, `thermal-overload-mitigation`, or `contingency-mitigation` when violations appear.

## Deliver
- The case, base-case status, and monitored findings.
- Any changes applied and their effect.
- Whether an advanced study or mitigation playbook is required next.
