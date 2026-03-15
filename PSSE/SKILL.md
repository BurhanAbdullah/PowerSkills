---
name: psse
description: Progressive-disclosure workflow for PSSE studies through PowerMCP. Use when the user asks to open a PSSE case, solve the base case, discover the right PSSPY command, or execute targeted PSSE automation, and when generic API execution should come only after command lookup and base-case validation.
---

# PSSE workflow

Treat PSSE as a layered interface. Start with the built-in base-case tools. Use generic `psspy` execution only after the correct command and argument shape are known.

## Default tool ladder
1. `open_case(case)`
2. `solve_case()`
3. `search_psspy_commands(query, category)` or `lookup_psspy_command(function_name)` to discover the right API entry point.
4. `run_psspy_command(function_name, arguments)` only after the command contract is explicit.

## Working rules
- Do not use `run_psspy_command` as a search tool. Search or look up first.
- Keep every executed command tied to a study objective, not just API curiosity.
- Re-solve or re-check the case after commands that alter topology, controls, or dispatch.
- Use `dynamic-stability-mitigation` for dynamic issues and the steady-state mitigation skills for voltage, thermal, or contingency findings.

## Deliver
- The case, the command path chosen, and why it was needed.
- The arguments passed to the command.
- The study outcome and any required mitigation.
