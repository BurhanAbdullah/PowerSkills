# PowerSkills

Agent Skills for power system analysis. This repository provides AI agents with specialized knowledge and instructions for performing power system simulations, analysis, and optimization using various power system software tools.

## What are Agent Skills?

Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform tasks more accurately and efficiently. They follow the [Agent Skills specification](https://agentskills.io/specification) and are compatible with Cursor, Claude Code, and other skills-compatible AI agents.

## Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [pandapower](pandapower/) | Power flow analysis, contingency analysis, and network management using pandapower | Available |
| OpenDSS | Distribution system simulation and analysis | Coming soon |
| PyPSA | Power system analysis with renewable integration | Coming soon |
| PSSE | Power system stability analysis | Coming soon |
| PowerWorld | Power system visualization and analysis | Coming soon |

## Project Structure

```
PowerSkills/
├── README.md
├── common/
│   └── __init__.py
└── pandapower/
    ├── SKILL.md
    ├── README.md
    └── references/
        ├── API_REFERENCE.md
        └── EXAMPLES.md
```

## Usage

### With Cursor

Skills in this repository can be used directly with Cursor. The agent will automatically discover and apply relevant skills based on the task context.

### With Claude Code

Register skills by pointing to the skill directory containing the `SKILL.md` file.

### With Other Compatible Agents

Follow the agent's documentation for registering external skills.

## Requirements

- Python 3.10+
- Specific power system libraries (see individual skill documentation)

## Related Projects

- [PowerMCP](https://github.com/Power-Agent/PowerMCP) - MCP servers for power system software integration with LLMs
- [Agent Skills Specification](https://agentskills.io/) - The open standard for agent skills

## License

MIT License
