# Pandapower Analysis Scripts

Agent-friendly scripts for power system analysis. Scripts are designed to:
- Return structured data (dicts/lists) for programmatic decision-making
- Work as both CLI tools and importable Python modules

---

## Scripts

### `network_analysis.py` -- Network Health Check & Analysis

**Main function**: `analyze_network(net, v_min=0.95, v_max=1.05, loading_limit=100.0)`

Returns a structured dict with **summary**, **violations**, and **losses**.

CLI:

```bash
python network_analysis.py network.json
```

---

### `contingency_analysis.py` -- N-1 Contingency Analysis

**Main function**: `analyze_n1(net, elements=['line', 'trafo'])`

Returns a list of per-contingency dicts and helpers for filtering and reporting.

CLI:

```bash
python contingency_analysis.py network.json
```

---

## Quick Start (Agent Workflow)

```python
import pandapower as pp
from network_analysis import analyze_network
from contingency_analysis import analyze_n1, get_critical_contingencies

net = pp.from_json("network.json")
pp.runpp(net)

baseline = analyze_network(net)

# Run N-1
n1 = analyze_n1(net)
critical = get_critical_contingencies(n1)
```

---

## Installation

```bash
pip install -r ../requirements.txt
```
