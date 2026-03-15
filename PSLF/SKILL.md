---
name: pslf
description: Progressive-disclosure workflow for PSLF studies. Use when the user asks to open a PSLF case, solve the base case, inspect voltage or overload violations, edit the network, or run contingency analysis through PowerMCP, and when basic case work should come before contingency studies.
---

# PSLF workflow

Start with the current case and base power flow. Use network edits and contingencies only after the solved case is credible.

## Default tool ladder
1. `open_case(case)`
2. `solve_case()`
3. `get_voltage(bus)`, `get_voltage_violations(...)`, and `get_overload_violations(...)` to identify the real issue.
4. `add_shunt(...)`, `add_generator(...)`, `add_load(...)`, `add_branch(...)`, or `add_bus(...)` for controlled model changes.
5. `save_case()` after the edited state is worth keeping.
6. `run_contingency_analysis()` only after the base case is solved and monitored.

## Working rules
- Do not run contingencies on an unsolved or obviously bad base case.
- Prefer the smallest corrective action that addresses the violation.
- Use `voltage-violation-mitigation`, `thermal-overload-mitigation`, or `contingency-mitigation` to decide the order of fixes.

## Deliver
- The case opened and base-case status.
- The key violations found.
- The edits applied and whether the contingency study still fails.
