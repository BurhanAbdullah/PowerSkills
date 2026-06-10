---
name: andes
description: Progressive-disclosure workflow for ANDES dynamic studies. Use whenever the user wants to run ANDES through PowerMCP for power flow, small-signal / eigenvalue analysis, or time-domain simulation — even when they just say "check the damping", "is this stable", "run a fault", or "look at the oscillation modes". Exposes a solved base case before eigenvalue screening and time-domain runs. Reach for this instead of answering ANDES dynamics questions unaided.
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

## Escalation triggers
Quote the failing metric (mode + damping ratio, channel + recovery time) rather than saying "it is unstable".

| Observation | Escalate to |
|---|---|
| Eigenvalue with damping ratio below ~5% or any right-half-plane mode | `dynamic-stability-mitigation` |
| Time-domain run shows growing angles, sustained oscillations, or failed voltage recovery | `dynamic-stability-mitigation` |
| Base power-flow voltages outside [0.95, 1.05] pu | `voltage-violation-mitigation` |
| Frequency nadir, RoCoF, or settling frequency violates its limit after a generation-loss event | `frequency-response-mitigation` |

## Deliver
- The case used and whether the base case solved.
- The dynamic issue being checked.
- The main result and whether mitigation is now required.
