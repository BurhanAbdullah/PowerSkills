# PowerSkills

PowerSkills is the skill layer on top of [PowerMCP](https://github.com/Power-Agent/PowerMCP). PowerMCP exposes raw software tools. PowerSkills tells an agent which tool to reach for first, what to verify before escalating to advanced studies, and what mitigation playbooks to follow when a study finds a real operating problem.

## How this repo differs from PowerMCP

1. **Progressive disclosure of software tools**
   - Start with the lowest-risk actions first: open or load the case, inspect the model, solve the base case, and only then move to advanced studies.
   - Avoid jumping directly into contingency analysis, dynamics, matrix extraction, or investment optimization before the base case is credible.
2. **Senior engineer mitigation skills**
   - Add issue-driven playbooks for voltage violations, thermal overloads, contingency findings, dynamic stability problems, and planning infeasibilities.
   - Move beyond violation reporting into corrective action, tradeoff discussion, and validation steps.

## Available software skills

These skills mirror the current software list in PowerMCP.

| Skill | Scope | First tools to expose | Advanced tools to expose later |
| --- | --- | --- | --- |
| [ANDES](ANDES/) | Dynamic security and small-signal studies | `run_power_flow`, `get_system_info` | `run_eigenvalue_analysis`, `run_time_domain_simulation` |
| [Egret](Egret/) | Market and operations optimization | `solve_dc_opf` | `solve_ac_opf`, `solve_unit_commitment_problem` |
| [LTSpice](LTSpice/) | Circuit simulation workflow | `create_simulation_session`, `run_simulation` | `list_available_traces`, `plot_specific_traces`, GUI viewing |
| [OpenDSS](OpenDSS/) | Distribution feeder studies | `compile_and_solve`, `get_total_power`, `get_bus_voltages` | `set_load_multiplier`, `run_daily_energy_meter`, `get_harmonic_results` |
| [PSLF](PSLF/) | Transmission power flow and contingencies | `open_case`, `solve_case`, violation checks | topology or device edits, `run_contingency_analysis` |
| [PSSE](PSSE/) | PSSE base-case and API-guided studies | `open_case`, `solve_case` | `lookup_psspy_command`, `search_psspy_commands`, `run_psspy_command` |
| [PowerWorld](PowerWorld/) | Steady-state analysis and sensitivities | `open_case`, `run_powerflow`, result queries | contingencies, parameter changes, PTDF or LODF or Jacobian tools |
| [PyPSA](PyPSA/) | Planning, OPF, and expansion studies | `load_network` or `create_network`, network inspection | `optimize_network`, `optimize_investment`, import or export flows |
| [pandapower](pandapower/) | AC analysis and screening studies | `load_network` or `create_empty_network`, `get_network_info`, `run_power_flow` | `run_contingency_analysis` |

## Available mitigation skills

| Skill | Use when | Typical actions |
| --- | --- | --- |
| [voltage-violation-mitigation](voltage-violation-mitigation/) | Low or high voltage, weak reactive support, tap exhaustion | AVR or Volt-VAR checks, shunts, taps, redispatch, transfer reduction |
| [thermal-overload-mitigation](thermal-overload-mitigation/) | Line or transformer overloads | redispatch, topology switching, phase-shifter control, reinforcement screening |
| [contingency-mitigation](contingency-mitigation/) | N-1 or N-2 violations or weak corrective-action plans | pre-contingency fixes, corrective switching, RAS screening, long-term upgrades |
| [dynamic-stability-mitigation](dynamic-stability-mitigation/) | Poor damping, transient instability, slow voltage recovery | model checks, dispatch relief, AVR or PSS or governor tuning, dynamic VAR support |
| [operations-planning-mitigation](operations-planning-mitigation/) | OPF or UC infeasibility, high curtailment, congestion, reserve shortage | data cleanup, simpler screening solves, flexibility additions, constraint review |

## Repository layout

```text
PowerSkills/
├── <software>/
│   └── SKILL.md
├── pandapower/
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
├── PyPSA/
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── case39.nc
└── <mitigation-skill>/
    └── SKILL.md
```

`pandapower/` and `PyPSA/` already include local scripts and example cases. The other software folders in this redesign are guidance-first skills intended to sit on top of the corresponding PowerMCP servers and native tools.

## Contribution rules

Contributors should use Skill Creator when adding or updating skills.

- Keep `SKILL.md` concise and procedural.
- For software skills, expose tools in this order: load or open -> inspect -> solve -> modify -> advanced studies.
- For mitigation skills, start from an observed problem and list corrective actions in the order a senior engineer would actually try them.
- Prefer contributions in two buckets:
  - better progressive disclosure for an existing PowerMCP software surface
  - better mitigation playbooks that use one or more of those software tools
- If your checkout includes the local Skill Creator helper, validate with `python skill-creator/scripts/quick_validate.py <skill-folder>` before opening a PR.

## Related projects

- [PowerMCP](https://github.com/Power-Agent/PowerMCP) - MCP servers for power-system software
- [Agent Skills](https://agentskills.io/) - open skill format and ecosystem

### Core Team
- [Qian Zhang](https://www.linkedin.com/in/qian-zhang-75323111b/), [Matheus Duarte](https://www.linkedin.com/in/matheusduarte/), [Muhy Eddin Za’ter](https://scholar.google.com/citations?user=_IFFYFAAAAAJ&hl=en)

## License

MIT License
