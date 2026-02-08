# Pandapower Analysis Skill

This skill enables AI agents to perform power system analysis using [pandapower](https://github.com/e2nIEE/pandapower), an open-source Python library for power system modeling, analysis, and optimization.

## Requirements

- Python 3.10+
- pandapower (`pip install pandapower`)

## Capabilities

| Capability | Description |
|------------|-------------|
| Network Creation | Create power system networks from scratch or load from files |
| Power Flow Analysis | Run AC power flow using Newton-Raphson or backward/forward sweep |
| Contingency Analysis | Perform N-1 and N-2 security assessments |
| Network Inspection | Query network topology, element data, and results |
| Result Interpretation | Identify voltage violations, line overloads, and losses |

## Skill Files

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Main skill instructions and quick reference |
| [references/API_REFERENCE.md](references/API_REFERENCE.md) | Detailed pandapower API documentation |
| [references/EXAMPLES.md](references/EXAMPLES.md) | Practical usage examples |

## Example Prompts

- "Load the IEEE 14-bus test case and run power flow analysis"
- "Perform N-1 contingency analysis on my network and identify any violations"
- "Create a simple 3-bus network with a generator, load, and transmission line"
- "Check for voltage violations and overloaded lines in the power flow results"
- "What is the total system loss in my network?"

## Related Resources

- [Pandapower Documentation](https://pandapower.readthedocs.io/)
- [Pandapower GitHub](https://github.com/e2nIEE/pandapower)
- [PowerMCP Pandapower Server](https://github.com/Power-Agent/PowerMCP/tree/main/pandapower)
