---
name: egret
description: Progressive-disclosure workflow for Egret optimization studies. Use when the user asks to run DC OPF, AC OPF, or unit commitment through PowerMCP, and when the agent should solve the simplest credible optimization before escalating to full commitment studies.
---

# Egret workflow

Start with the cheapest model that can answer the question. Do not jump into unit commitment when a single-snapshot OPF will do.

## Default tool ladder
1. `solve_dc_opf(case_file, solver, return_results)` for fast feasibility and congestion screening.
2. `solve_ac_opf(case_file, solver, return_results)` when voltage or reactive realism matters.
3. `solve_unit_commitment_problem(case_file, solver, mipgap, timelimit)` only after the horizon, reserve logic, and commitment assumptions are clear.

## Working rules
- Confirm the case file format, solver, and time horizon before solving.
- Use DC OPF first unless the question explicitly depends on AC feasibility.
- Treat UC as a higher-cost study that needs a clear operational objective.
- Hand off to `operations-planning-mitigation` when the solution is infeasible, too expensive, reserve-deficient, or overly curtailed.
- Validate promising dispatch fixes in an AC tool when voltage limits matter.

## Deliver
- The case, solver, and study type.
- The limiting constraints or binding tradeoffs.
- Whether the next step is AC validation, UC escalation, or mitigation.
