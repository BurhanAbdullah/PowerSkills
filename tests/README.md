## Skill contract verification

Run the repository-wide contract checks with:

```bash
python -m unittest discover -s tests -v
```

The checks verify the expected software and engineering skill catalogs, the base-case-first workflow, escalation section/target names, documented local assets and script paths, and examples that can be compared with actual MCP-registered Python tool functions.

For direct PowerMCP signature verification, set `POWER_MCP_REPO` to a local PowerMCP checkout before running the suite:

```bash
POWER_MCP_REPO=../PowerMCP python -m unittest discover -s tests -v
```

These are contract/regression checks, not a claim that vendor solvers are installed or that a proprietary simulation has been run.
