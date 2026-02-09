---
name: pandapower-analysis
description: Perform power system analysis using pandapower including power flow calculations, contingency analysis, network creation, and result interpretation. Use when the user asks about power flow, load flow, voltage analysis, line loading, transformer analysis, N-1 contingency, or working with pandapower networks.
compatibility: Requires Python 3.10+ and pandapower library
metadata:
  author: PowerSkills
  version: "1.0"
---

# Pandapower Power System Analysis

> **How to use this guide**: Start with Quick Start, then follow the sections in order.
> Each section builds on the previous one. For detailed API docs and worked examples,
> see [references/](#reference).

---

## 1. Quick Start

```python
import pandapower as pp

# Load a network (from file or built-in test case)
net = pp.from_json("network.json")   # from file
net = pp.networks.case39()           # or built-in IEEE 39-bus

# Run power flow
pp.runpp(net)

# Check results
if net.converged:
    print(net.res_bus[['vm_pu', 'va_degree']])   # bus voltages
    print(net.res_line[['loading_percent']])       # line loading
```

**For comprehensive automated analysis**, use `scripts/network_analysis.py` and `scripts/contingency_analysis.py`.

---

## 2. Network Inspection

Before running any analysis, understand the network you are working with.

### Load a Network

```python
# From file
net = pp.from_json("network.json")
net = pp.from_pickle("network.p")

# Built-in IEEE test cases
net = pp.networks.case14()       # 14-bus
net = pp.networks.case_ieee30()  # 30-bus
net = pp.networks.case39()       # 39-bus
net = pp.networks.case118()      # 118-bus
```

### Inspect Network Elements

A pandapower network is a dictionary of pandas DataFrames -- one per element type.

```python
# Element counts
print(f"Buses:          {len(net.bus)}")
print(f"Lines:          {len(net.line)}")
print(f"Transformers:   {len(net.trafo)}")
print(f"Loads:          {len(net.load)}")
print(f"Generators:     {len(net.gen)}")
print(f"External Grids: {len(net.ext_grid)}")

# View element data (each is a pandas DataFrame)
print(net.bus)          # bus names, nominal voltages
print(net.line)         # line parameters, from/to buses
print(net.load)         # active/reactive power at each bus
```

**For automated summaries and analysis**, use the scripts in `pandapower/scripts/`.

---

## 3. Power Flow Analysis

Power flow (load flow) is the fundamental analysis -- it computes voltages, currents, and power flows throughout the network.

### Run Power Flow

```python
pp.runpp(net)                     # Newton-Raphson (default)

# With options
pp.runpp(net,
         algorithm='nr',                # 'nr', 'bfsw', or 'gs'
         calculate_voltage_angles=True,
         tolerance_mva=1e-8)

# DC power flow (linear approximation, faster)
pp.rundcpp(net)
```

### Read Results

After `pp.runpp(net)`, results are stored in `res_*` DataFrames:

| Result Table | Key Columns | What It Tells You |
|---|---|---|
| `net.res_bus` | `vm_pu`, `va_degree` | Bus voltage magnitudes and angles |
| `net.res_line` | `loading_percent`, `p_from_mw`, `pl_mw` | Line power flows, loading, and losses |
| `net.res_trafo` | `loading_percent`, `p_hv_mw`, `pl_mw` | Transformer flows, loading, and losses |
| `net.res_gen` | `p_mw`, `q_mvar` | Generator active/reactive output |
| `net.res_ext_grid` | `p_mw`, `q_mvar` | Slack bus power injection |

```python
print(net.res_bus[['vm_pu', 'va_degree']])
print(net.res_line[['loading_percent', 'p_from_mw', 'pl_mw']])
```

### Check for Violations

```python
# Voltage violations (typical limits: 0.95 -- 1.05 p.u.)
undervoltage = net.res_bus[net.res_bus.vm_pu < 0.95]
overvoltage  = net.res_bus[net.res_bus.vm_pu > 1.05]

# Equipment overloading (> 100% of rating)
overloaded_lines  = net.res_line[net.res_line.loading_percent > 100]
overloaded_trafos = net.res_trafo[net.res_trafo.loading_percent > 100]
```

**For comprehensive automated checks**, use `scripts/network_analysis.py`.

---

## 4. Network Creation

Build a network from scratch when you need to model a custom system.

### Create and Populate

```python
net = pp.create_empty_network(name="My System", f_hz=60.0)

# Buses
bus1 = pp.create_bus(net, vn_kv=110, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=110, name="Load Bus")

# Slack / reference bus
pp.create_ext_grid(net, bus=bus1, vm_pu=1.02, va_degree=0)

# Line (using standard type)
pp.create_line(net, from_bus=bus1, to_bus=bus2,
               length_km=10, std_type="NAYY 4x50 SE")

# Load
pp.create_load(net, bus=bus2, p_mw=2.0, q_mvar=0.5)

# Run power flow
pp.runpp(net)
```

### Save / Load Networks

```python
pp.to_json(net, "network.json")      # JSON (recommended, human-readable)
pp.to_pickle(net, "network.p")       # Pickle (faster for large networks)

net = pp.from_json("network.json")
```

---

## 5. Contingency Analysis

N-1 contingency analysis tests whether the system remains secure when any single element is removed.

### Basic Concept

```python
# Test a single contingency by disconnecting an element
test_net = net.deepcopy()
test_net.line.at[line_idx, 'in_service'] = False
pp.runpp(test_net)

# Check if power flow converged and no violations occurred
```

### For Full N-1 Studies

Use the provided script:

```bash
python scripts/contingency_analysis.py network.json
```

Or import as a module:

```python
from scripts.contingency_analysis import run_n1_analysis
results_df = run_n1_analysis(net, elements=['line', 'trafo'])
```

---

## 6. Advanced Studies

### System Losses

```python
# Calculate losses manually
line_losses = net.res_line.pl_mw.sum()
trafo_losses = net.res_trafo.pl_mw.sum() if len(net.trafo) > 0 else 0
total_losses = line_losses + trafo_losses
```

**For detailed loss analysis**, use `scripts/network_analysis.py`.

### Load Scaling Study

Sweep load levels to find the system's capacity limits.

```python
original_loads = net.load.p_mw.copy()

for scale in [0.5, 1.0, 1.5, 2.0]:
    net.load.p_mw = original_loads * scale
    pp.runpp(net)

    if net.converged:
        print(f"Scale {scale}: Min V = {net.res_bus.vm_pu.min():.3f}, "
              f"Max Loading = {net.res_line.loading_percent.max():.1f}%")

net.load.p_mw = original_loads  # restore
```

### Topology Analysis

```python
import pandapower.topology as top

connected = top.connected_components(net)    # number of islands
unsupplied = top.unsupplied_buses(net)       # buses without supply path
```

---

## Reference

### Provided Scripts

| Script | Purpose | Usage |
|---|---|---|
| `scripts/network_analysis.py` | Network health check and analysis | `from scripts.network_analysis import analyze_network` |
| `scripts/contingency_analysis.py` | N-1 contingency analysis with report | `python scripts/contingency_analysis.py network.json` |

See the scripts in `pandapower/scripts/` for CLI entrypoints and importable APIs.

### Typical Workflows

| Goal | Steps |
|---|---|
| Network health check | Load network → `python scripts/network_analysis.py network.json` |
| N-1 contingency study | Load network → `python scripts/contingency_analysis.py network.json` |
| Custom analysis | Load network → `from scripts.network_analysis import analyze_network` → use results |

### Additional Resources

- **[API Reference](references/API_REFERENCE.md)** -- element tables, result tables, function signatures
- **[Examples](references/EXAMPLES.md)** -- 10 worked examples covering all topics above
- **[Pandapower Docs](https://pandapower.readthedocs.io/)** -- official documentation
