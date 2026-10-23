"""Execute the N-1 example documented in the pandapower skill."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "powerskills-tool" / "skills" / "pandapower" / "references" / "EXAMPLES.md"


def test_documented_n1_example_accounts_for_each_line_outage():
    text = EXAMPLES.read_text(encoding="utf-8")
    section = text.split("### Example 8: N-1 Contingency Analysis", 1)[1]
    code = section.split("```python", 1)[1].split("```", 1)[0]
    namespace = {"__name__": "documented_n1_example"}
    exec(compile(code, str(EXAMPLES), "exec"), namespace)

    net = namespace["net"]
    results = namespace["results"]
    assert len(results) == len(net.line)
    assert all(r["status"] in {"converged", "failed", "diverged"} for r in results)
    assert all({"voltage_violations", "line_overloads", "trafo_overloads"} <= r.keys() for r in results)
    assert sum(r["status"] == "converged" for r in results) + sum(
        r["status"] == "failed" for r in results
    ) + sum(r["status"] == "diverged" for r in results) == len(net.line)
