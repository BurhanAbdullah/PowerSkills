---
name: pandapower-analysis
description: Perform power system analysis using pandapower including power flow calculations, contingency analysis, network creation, and result interpretation. Use when the user asks about power flow, load flow, voltage analysis, line loading, transformer analysis, N-1 contingency, or working with pandapower networks.
compatibility: Requires Python 3.10+ and pandapower library
metadata:
  author: PowerSkills
  version: "2.0"
---

# Pandapower Power System Analysis

> **Progressive disclosure guide**: Start with Quick Start, then explore as needed.
> For complex analysis, use the provided scripts in `scripts/`.

## Quick Start

**Load network and run power flow:**

```python
import pandapower as pp

# Load from file or use test network
net = pp.from_json("network.json")  # or pp.networks.case14()

# Run power flow
pp.runpp(net)

# Check convergence
if net.converged:
    print("✓ Power flow converged")
    print(net.res_bus[['vm_pu', 'va_degree']])
else:
    print("❌ Power flow failed")
```

**Quick health check using provided script:**

```bash
python scripts/quick_check.py network.json
```

---

## Level 1: Basic Analysis

### Load Networks

```python
# From file
net = pp.from_json("network.json")
net = pp.from_pickle("network.p")

# Test networks
net = pp.networks.case14()      # IEEE 14-bus
net = pp.networks.case_ieee30() # IEEE 30-bus
net = pp.networks.case39()      # IEEE 39-bus
```

### Run Power Flow

```python
# Standard power flow
pp.runpp(net)

# With options
pp.runpp(net, 
         algorithm='nr',              # Newton-Raphson (default)
         calculate_voltage_angles=True,
         tolerance_mva=1e-8)
```

### Check for Violations

```python
# Voltage violations (0.95 - 1.05 p.u.)
undervoltage = net.res_bus[net.res_bus.vm_pu < 0.95]
overvoltage = net.res_bus[net.res_bus.vm_pu > 1.05]

# Equipment overloading
overloaded_lines = net.res_line[net.res_line.loading_percent > 100]
overloaded_trafos = net.res_trafo[net.res_trafo.loading_percent > 100]
```

**Use the comprehensive check script:**

```python
from scripts.network_analysis import run_comprehensive_check

results = run_comprehensive_check(net, verbose=True)
# Returns: voltage violations, loading violations, system losses
```

---

## Level 2: Network Building

### Create New Network

```python
net = pp.create_empty_network(name="My System", f_hz=60.0)

# Add buses
bus1 = pp.create_bus(net, vn_kv=110, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=110, name="Load Bus")

# Add slack (reference bus)
pp.create_ext_grid(net, bus=bus1, vm_pu=1.02, va_degree=0)

# Add line
pp.create_line(net, from_bus=bus1, to_bus=bus2, 
               length_km=10, std_type="NAYY 4x50 SE")

# Add load
pp.create_load(net, bus=bus2, p_mw=2.0, q_mvar=0.5)

# Run power flow
pp.runpp(net)
```

### Save Networks

```python
pp.to_json(net, "network.json")    # JSON (recommended)
pp.to_pickle(net, "network.p")     # Pickle (faster)
```

---

## Level 3: Advanced Analysis

### N-1 Contingency Analysis

**Use the comprehensive contingency script:**

```python
from scripts.contingency_analysis import run_n1_analysis, generate_contingency_report

# Run N-1 analysis for all lines and transformers
results_df = run_n1_analysis(net, elements=['line', 'trafo'], verbose=True)

# Generate report
report = generate_contingency_report(results_df, output_file='n1_report.txt')
print(report)
```

**Or run from command line:**

```bash
python scripts/contingency_analysis.py network.json
```

**Manual N-1 check (for custom logic):**

```python
original_net = net.deepcopy()

for line_idx in net.line.index:
    test_net = original_net.deepcopy()
    test_net.line.at[line_idx, 'in_service'] = False  # Disconnect line
    
    pp.runpp(test_net)
    
    if not test_net.converged:
        print(f"⚠️ Line {line_idx} outage: Power flow diverged")
    elif test_net.res_bus.vm_pu.min() < 0.95:
        print(f"⚠️ Line {line_idx} outage: Voltage violation")
```

### System Loss Analysis

```python
from scripts.network_analysis import calculate_system_losses

losses = calculate_system_losses(net)
print(f"Total losses: {losses['total_losses_mw']:.2f} MW ({losses['loss_percentage']:.2f}%)")
print(f"  Line losses: {losses['line_losses_mw']:.2f} MW")
print(f"  Trafo losses: {losses['trafo_losses_mw']:.2f} MW")
```

### Load Scaling Study

```python
scaling_factors = [0.5, 1.0, 1.5, 2.0]
original_loads = net.load.p_mw.copy()

for scale in scaling_factors:
    net.load.p_mw = original_loads * scale
    pp.runpp(net)
    
    if net.converged:
        print(f"Scale {scale}: Min V = {net.res_bus.vm_pu.min():.3f}, "
              f"Max Loading = {net.res_line.loading_percent.max():.1f}%")

# Restore original loads
net.load.p_mw = original_loads
```

---

## Result Tables Reference

After `pp.runpp(net)`, results are in `res_*` DataFrames:

| Table | Key Columns | Description |
|-------|-------------|-------------|
| `net.res_bus` | `vm_pu`, `va_degree` | Bus voltages and angles |
| `net.res_line` | `loading_percent`, `p_from_mw`, `pl_mw` | Line flows and losses |
| `net.res_trafo` | `loading_percent`, `p_hv_mw`, `pl_mw` | Transformer flows and losses |
| `net.res_gen` | `p_mw`, `q_mvar` | Generator output |
| `net.res_load` | `p_mw`, `q_mvar` | Load consumption |

---

## Provided Scripts

This skill includes ready-to-use analysis scripts:

1. **`scripts/quick_check.py`** - Fast network health check
   ```bash
   python scripts/quick_check.py network.json
   python scripts/quick_check.py network.json --v-min 0.90 --v-max 1.10
   ```

2. **`scripts/contingency_analysis.py`** - Comprehensive N-1 analysis
   ```bash
   python scripts/contingency_analysis.py network.json
   ```

3. **`scripts/network_analysis.py`** - Reusable analysis functions
   ```python
   from scripts.network_analysis import run_comprehensive_check
   results = run_comprehensive_check(net)
   ```

---

## Additional Resources

- **[API Reference](references/API_REFERENCE.md)** - Complete pandapower API documentation
- **[Examples](references/EXAMPLES.md)** - 10+ practical examples with full code
- **[Pandapower Docs](https://pandapower.readthedocs.io/)** - Official documentation

---

## Common Workflows

**Workflow 1: Quick Analysis**
1. Load network: `net = pp.from_json("network.json")`
2. Run: `python scripts/quick_check.py network.json`

**Workflow 2: N-1 Study**
1. Load network
2. Run: `python scripts/contingency_analysis.py network.json`
3. Review: `contingency_report.txt`

**Workflow 3: Custom Analysis**
1. Load network
2. Import: `from scripts.network_analysis import *`
3. Use: `run_comprehensive_check(net, verbose=True)`
