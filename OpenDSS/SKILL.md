---
name: opendss
description: Progressive-disclosure workflow for OpenDSS feeder studies. Use when the user asks to compile a DSS model, solve a distribution circuit, inspect feeder voltages or power, run load multipliers, or perform daily or harmonic studies through PowerMCP, with base-case checks before advanced scenarios.
---

# OpenDSS workflow

Start with a solved feeder. Do not jump to daily or harmonic studies until the base feeder compiles and the voltage profile is understood.

## Default tool ladder
1. `compile_and_solve(dss_file)` to load and solve the circuit.
2. `get_total_power()` and `get_bus_voltages()` to confirm the base operating point.
3. `set_load_multiplier(load_mult)` for simple scenario sweeps.
4. `run_daily_energy_meter(meter_name, hours)` for daily feeder behavior.
5. `get_harmonic_results(load_name, harmonic)` only after the harmonic question is well scoped.

## Working rules
- Fix compile or solve errors before any scenario analysis.
- For voltage issues, inspect the weak buses first and then use `voltage-violation-mitigation`.
- Separate load-growth screening from harmonic analysis; they answer different questions.
- Keep feeder, meter, and load names explicit in the response.

## Deliver
- The compiled feeder and base-case status.
- The voltage or power quantities checked.
- Any scenario result and whether mitigation is needed.
