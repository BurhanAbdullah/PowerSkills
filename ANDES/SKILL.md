---
name: andes
description: Progressive-disclosure workflow for ANDES studies. Use when the user asks to run ANDES through PowerMCP for power flow, small-signal stability, or time-domain simulation, and when the agent should expose base-case steps before advanced dynamic analysis.
---

# ANDES workflow

Expose ANDES tools in stages. Do not jump into dynamics until the base case is loaded, solved, and understood.

## Default tool ladder
1. `run_power_flow(file_path)` to load the case and solve the steady-state point.
2. `get_system_info()` to summarize buses, generators, dynamic states, and controls.
3. `run_eigenvalue_analysis(file_path)` to screen oscillatory modes and poor damping.
4. `run_time_domain_simulation(step_size, t_end)` only after the disturbance and success criteria are explicit.

## Working rules
- Re-run the base power flow after any model or dispatch change before dynamic work.
- State the disturbance, clearing time, monitored channels, and pass or fail criteria before time-domain runs.
- Treat eigenvalue results as screening. Confirm critical cases in time domain.
- Hand off to `dynamic-stability-mitigation` when damping, angle stability, or voltage recovery is unacceptable.

## Deliver
- The case used and whether the base case solved.
- The dynamic issue being checked.
- The main result and whether mitigation is now required.
