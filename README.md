# PowerSkills

Agent Skills for power system analysis. This repository provides AI agents with specialized knowledge and instructions for performing power system simulations, analysis, and optimization using various power system software tools.

## What are Agent Skills?

Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform tasks more accurately and efficiently. They follow the [Agent Skills specification](https://agentskills.io/specification) and are compatible with Cursor, Claude Code, and other skills-compatible AI agents.

## Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [pandapower](pandapower/) | Power flow analysis, contingency analysis, and network management using pandapower | ✅ Available |
| [PyPSA](PyPSA/) | Power system optimization, capacity expansion, sector coupling, and investment planning using PyPSA. Includes IEEE 39-bus test case (`PyPSA/case39.nc`). | ✅ Available |
| OpenDSS | Distribution system simulation and analysis | Coming soon |
| PSSE | Power system stability analysis | Coming soon |
| PowerWorld | Power system visualization and analysis | Coming soon |

## Project Structure

```
PowerSkills/
├── README.md                          # This file
└── <skill-name>/                      # One folder per skill
    ├── SKILL.md                       # Main skill guide (teaches concepts & API)
    ├── requirements.txt               # Dependencies with pinned versions
    ├── scripts/                       # Agent-friendly analysis tools
    │   └── *.py                       # Python modules (CLI + importable)
    └── references/                    # Detailed reference docs
        ├── API_REFERENCE.md           # Data structures, function signatures
        └── EXAMPLES.md                # Worked examples
```

### Philosophy

**SKILL.md** teaches the underlying software API and concepts using simple inline examples.

**scripts/** provide production-ready tools that agents can call directly:
- Return structured data (dicts/lists) for programmatic decision-making
- Work as both CLI tools and Python modules
- Handle edge cases and error conditions
- Format output for human readability when needed

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

---

## Skill Development Template

Use this template when creating a new skill for a different software tool. The structure follows a **progressive disclosure** pattern: start with the simplest useful action, then layer on complexity.

### Directory Layout

```
<skill-name>/
├── SKILL.md                  # Main entry point (the agent reads this first)
├── requirements.txt          # Pinned dependencies
├── scripts/                  # Ready-to-use scripts
│   └── *.py                  # One script per major workflow
└── references/               # Deep-dive documentation
    ├── API_REFERENCE.md      # Data structures, function signatures, tables
    └── EXAMPLES.md           # Self-contained worked examples
```

### SKILL.md Structure

The main skill file teaches the underlying API using simple inline examples.
It should NOT contain complete scripts - just reference them.

```markdown
---
name: <skill-name>
description: <one-sentence description with trigger keywords>
compatibility: <runtime requirements>
metadata:
  author: PowerSkills
  version: "1.0"
---

# <Tool Name> <Domain> Analysis

> **How to use this guide**: Start with Quick Start, then follow sections in order.
> For production analysis tools, use the scripts in `scripts/`.

## 1. Quick Start
Minimal code (5-10 lines) showing the most basic workflow.
- Load/connect to data
- Run the primary analysis
- Read key results
- Reference scripts/ for automation

## 2. Data Inspection
Understand the data before analyzing it.
- How to load/import data
- How to list and inspect elements
- Key data structures and their fields
- Reference scripts/ for automated summaries

## 3. Core Analysis
The tool's primary analysis capability.
- How to run it (API calls)
- How to read results (data structures)
- How to check for violations (simple inline examples)
- Reference scripts/ for comprehensive checks

## 4. Data Creation / Modification
Build or modify the data model.
- Create from scratch
- Add/remove/modify elements
- Save and export

## 5. Advanced Analysis
More sophisticated studies that build on the core.
- Basic concept with minimal example
- Reference scripts/ for full implementation

## Reference
Summary tables and links.
- Provided scripts (brief table)
- Links to scripts/, references/, external docs
```

**Key principles for SKILL.md:**

| Principle | How |
|---|---|
| Teach concepts, not scripts | Show 3-5 line API examples, not 20-line scripts |
| Progressive disclosure | Number sections 1-N; each builds on the previous |
| Quick Start first | Section 1 should be copy-paste runnable in <30 seconds |
| Inline brevity | If an example exceeds ~10 lines, move it to references/ or scripts/ |
| Reference scripts/ early and often | Point to scripts/ modules/CLIs whenever suggesting automation |

### API_REFERENCE.md Structure

```markdown
# <Tool Name> API Reference

> Quick-reference organized to mirror SKILL.md progression.

## Data Structures
- Overview table of all element/object types
- Column-level detail for each type (name, type, unit, description)

## Result Structures
- What gets produced after analysis
- Column-level detail for each result type

## Key Functions
- Grouped by purpose: I/O, creation, analysis, utilities
- Show function signatures with parameter types
- Parameter option tables where applicable

## Built-in Data / Test Cases
- List of available test networks, sample data, etc.
```

### EXAMPLES.md Structure

```markdown
# <Tool Name> Examples

> N worked examples from basic to advanced. Each is self-contained.

## <Category 1: e.g., Data Inspection>
### Example 1: <Descriptive title>
### Example 2: <Descriptive title>

## <Category 2: e.g., Core Analysis>
### Example 3: <Descriptive title>
...

## <Category N: e.g., Advanced Studies>
### Example N: <Descriptive title>
```

**Key principles for EXAMPLES.md:**

- Group examples by the same categories as SKILL.md sections
- Each example is self-contained (includes imports, data loading)
- Titles describe what you will *learn*, not just what you will *do*
- Progress from simple to complex within each category

### scripts/ Guidelines

**Design for agent use first, human use second.**

Each script should:
- **Return structured data** (dicts/lists, not just printed text)
- Work as both **CLI tool** and **importable Python module**
- Use **consistent function naming**: `analyze_*`, `check_*`, `calculate_*`, `summarize_*`
- Have one clear **main function** that agents should call
- Provide **helper functions** for filtering/formatting results
- Include **docstrings** with Args/Returns documentation

**scripts/ should include:**
- Main function for each script with its return structure
- Example return values (show the dict/list structure)
- Individual helper functions
- CLI usage examples
- Design principles

**Example script structure:**
```python
def analyze_network(net, v_min=0.95, v_max=1.05) -> Dict:
    """Main function - returns structured results."""
    return {'violations': {...}, 'summary': {...}}

def print_analysis_report(results: Dict):
    """Helper - formats results for human readability."""
    pass

if __name__ == "__main__":
    # CLI interface
    result = analyze_network(net)
    print_analysis_report(result)
```

### requirements.txt Guidelines

```
# <Skill Name> Requirements
# Install: pip install -r requirements.txt

core-library>=X.Y.Z
pandas>=1.5.0
numpy>=1.23.0

# Optional (recommended)
matplotlib>=3.5.0
```

### Checklist for a New Skill

- [ ] `SKILL.md` follows numbered progressive disclosure with brief inline examples (no scripts)
- [ ] `SKILL.md` Quick Start section is copy-paste runnable in <30 seconds
- [ ] `SKILL.md` references the `scripts/` tools whenever suggesting automation
- [ ] `scripts/` has clear main functions that return structured data (dicts/lists)
- [ ] `scripts/` functions return structured data (dicts/lists) and have docstrings
- [ ] `scripts/` work as both CLI tools and importable Python modules
- [ ] `references/API_REFERENCE.md` covers all data structures and key functions
- [ ] `references/EXAMPLES.md` has 5-10+ self-contained examples ordered basic to advanced
- [ ] `requirements.txt` has pinned minimum versions
- [ ] All files cross-reference each other consistently

---

## Related Projects

- [PowerMCP](https://github.com/Power-Agent/PowerMCP) - MCP servers for power system software integration with LLMs
- [Agent Skills Specification](https://agentskills.io/) - The open standard for agent skills

## License

MIT License

---

## Acknowledgments

### Core Team

- [Qian Zhang](https://www.linkedin.com/in/qian-zhang-harvard/)
- [Matheus Duarte](https://www.linkedin.com/in/matheusduarte/)
- [Muhy Eddin Za'ter](https://scholar.google.com/citations?user=_IFFYFAAAAAJ&hl=en)

### Special Thanks

- All contributors who help make this project better
- [The Power and AI Initiative (PAI) at Harvard SEAS](https://pai.seas.harvard.edu/)
