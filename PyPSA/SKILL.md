---
name: pypsa-analysis
description: Power system optimization and simulation using PyPSA including optimal power flow, capacity expansion planning, unit commitment, sector coupling, and network analysis. Use when the user asks about power system optimization, capacity expansion, investment planning, renewable integration, sector coupling, or PyPSA networks.
compatibility: Requires Python 3.10+ and PyPSA library
metadata:
  author: PowerSkills
  version: "1.0"
---

# PyPSA Power System Optimization

> **How to use this guide**: Start with Quick Start, then follow sections in order.
> For production analysis tools, see [scripts/README.md](scripts/README.md).

---

## 1. Quick Start

```python
import pypsa

# Load a network (from file, test case, or built-in example)
network = pypsa.Network("case39.nc")               # test case (IEEE 39-bus, single-file)
# network.import_from_csv_folder("network_folder/")  # or from CSV folder
# network = pypsa.examples.ac_dc_meshed()             # or built-in example

# Run optimal power flow
network.optimize()

# Check results
print(f"Objective: {network.objective}")
print(network.generators_t.p)     # generator dispatch
print(network.buses_t.marginal_price)  # nodal prices
```

**For automated analysis**, use the provided scripts (see [scripts/README.md](scripts/README.md)).

---

## 2. Network Inspection

Before optimization, understand the network structure and components.

### Load a Network

```python
import pypsa

# From CSV folder
network = pypsa.Network()
network.import_from_csv_folder("network_folder/")

# From NetCDF file
network = pypsa.Network("network.nc")

# Test case included in this skill (IEEE 39-bus, single-file)
network = pypsa.Network("case39.nc")

# Built-in examples
network = pypsa.examples.ac_dc_meshed()
network = pypsa.examples.storage_hvdc()
network = pypsa.examples.scigrid_de()
```

### Inspect Network Components

A PyPSA network contains multiple component DataFrames.

```python
# Component counts
print(f"Buses:       {len(network.buses)}")
print(f"Generators:  {len(network.generators)}")
print(f"Loads:       {len(network.loads)}")
print(f"Lines:       {len(network.lines)}")
print(f"Links:       {len(network.links)}")
print(f"Stores:      {len(network.storage_units)}")

# View static component data
print(network.buses)           # bus locations, voltage levels
print(network.generators)      # generator capacities, costs
print(network.loads)           # load profiles

# View time series data
print(network.loads_t.p_set)   # load time series
print(network.generators_t.p_max_pu)  # renewable availability
```

### Get Network Summary

```python
# Snapshot information
print(f"Snapshots: {len(network.snapshots)}")
print(f"Period: {network.snapshots[0]} to {network.snapshots[-1]}")

# Installed capacity by carrier
print(network.generators.groupby('carrier')['p_nom'].sum())
```

**For automated summaries**, see `scripts/network_analysis.py`.

---

## 3. Power Flow Simulation

Power flow computes nodal voltages and branch flows for given dispatch.

### Linear Power Flow

```python
# Linear (DC) power flow
network.lpf()

# Check results
print(network.buses_t.v_ang)      # voltage angles
print(network.lines_t.p0)         # line power flows
```

### Nonlinear Power Flow

```python
# AC power flow (Newton-Raphson)
network.pf()

# Check results
print(network.buses_t.v_mag_pu)   # voltage magnitudes
print(network.buses_t.v_ang)      # voltage angles
print(network.lines_t.p0)         # active power flows
print(network.lines_t.q0)         # reactive power flows
```

---

## 4. Optimization

Linear Optimal Power Flow (LOPF) optimizes generator dispatch to minimize costs.

### Basic Optimization

```python
# Optimize for single snapshot
network.optimize(snapshots=network.snapshots[0])

# Optimize for all snapshots
network.optimize()

# Check objective and results
print(f"Total cost: {network.objective}")
print(network.generators_t.p)           # optimal dispatch
print(network.buses_t.marginal_price)   # locational marginal prices
```

### Optimization with Solver Options

```python
network.optimize(
    solver_name='gurobi',  # or 'glpk', 'highs', 'cplex'
    solver_options={'LogToConsole': 0}
)
```

### Check Constraints

```python
# Check if optimization converged
if network.status['status'] == 'ok':
    print("Optimization succeeded")
else:
    print(f"Optimization failed: {network.status}")

# Examine shadow prices
print(network.lines_t.mu_lower)  # line congestion prices
```

**For comprehensive optimization analysis**, see `scripts/optimization_analysis.py`.

---

## 5. Network Creation

Build networks from scratch for custom studies.

### Create Empty Network

```python
import pypsa
import pandas as pd

network = pypsa.Network()

# Set time snapshots
network.set_snapshots(pd.date_range('2023-01-01', periods=8760, freq='h'))
```

### Add Components

```python
# Add buses
network.add("Bus", "bus0", v_nom=380)
network.add("Bus", "bus1", v_nom=380)

# Add generators
network.add("Generator", "coal", 
            bus="bus0", 
            p_nom=1000,      # MW capacity
            marginal_cost=30) # €/MWh

network.add("Generator", "wind",
            bus="bus1",
            p_nom=800,
            marginal_cost=0,
            p_max_pu=wind_profile)  # time series

# Add loads
network.add("Load", "load1",
            bus="bus1",
            p_set=load_profile)  # time series

# Add transmission line
network.add("Line", "line0-1",
            bus0="bus0",
            bus1="bus1",
            x=0.1,           # reactance
            s_nom=1000)      # MVA rating
```

### Save Networks

```python
# Export to CSV folder
network.export_to_csv_folder("my_network/")

# Save to NetCDF (faster, recommended)
network.export_to_netcdf("my_network.nc")
```

---

## 6. Capacity Expansion

Optimize both dispatch and investment in new capacity.

### Enable Capacity Expansion

```python
# Make generator capacity extendable
network.generators.loc['wind', 'p_nom_extendable'] = True
network.generators.loc['wind', 'capital_cost'] = 1000  # €/MW/year

# Make line capacity extendable
network.lines.loc['line0-1', 's_nom_extendable'] = True
network.lines.loc['line0-1', 'capital_cost'] = 400  # €/MW/year

# Optimize with investments
network.optimize()

# Check optimal capacities
print(network.generators.p_nom_opt)  # optimal installed capacity
print(network.lines.s_nom_opt)       # optimal line capacity
```

### Multi-Period Investment Planning

```python
# Set investment periods
network.set_investment_periods(periods=[2025, 2030, 2035, 2040])

# Different costs per period
network.generators_t.capital_cost  # time-varying costs

# Optimize pathway
network.optimize()
```

**For capacity expansion studies**, see `scripts/expansion_analysis.py`.

---

## 7. Contingency Analysis

N-1 contingency analysis tests whether the optimal solution remains feasible when any single element fails.

### Basic Concept

```python
# Test a single contingency (removes element and re-optimizes)
import copy
test_network = network.deepcopy()
test_network.mremove("Line", "line_name")
test_network.optimize()
```

### For Full N-1 Studies

Use the provided scripts (see [scripts/README.md](scripts/README.md)):

```bash
python scripts/contingency_analysis.py network.nc
```

Or import as a module:

```python
from scripts.contingency_analysis import analyze_n1, get_critical_contingencies

results = analyze_n1(network, elements=['line', 'link'])
critical = get_critical_contingencies(results)
```

**Note**: PyPSA also supports security-constrained optimization where N-1 constraints are built into the optimization itself (see PyPSA documentation).

---

## 8. Advanced Topics

### Unit Commitment

```python
# Add unit commitment constraints
network.generators.loc['coal', 'committable'] = True
network.generators.loc['coal', 'min_up_time'] = 4  # hours
network.generators.loc['coal', 'min_down_time'] = 4
network.generators.loc['coal', 'start_up_cost'] = 1000  # €/start

network.optimize()
```

### Storage Optimization

```python
# Add battery storage
network.add("StorageUnit", "battery",
            bus="bus1",
            p_nom=100,           # MW power capacity
            max_hours=4,         # MWh/MW energy capacity
            efficiency_store=0.95,
            efficiency_dispatch=0.95,
            capital_cost=150)
```

### Sector Coupling

```python
# Add power-to-gas link
network.add("Link", "P2G",
            bus0="elec_bus",
            bus1="gas_bus",
            efficiency=0.6,
            p_nom=100)

# Add heat pump
network.add("Link", "heat_pump",
            bus0="elec_bus",
            bus1="heat_bus",
            efficiency=3.0,    # COP
            p_nom=50)
```

### Sensitivity Analysis

```python
# Parametric cost sweep
costs = [20, 30, 40, 50]
objectives = []

for cost in costs:
    network.generators.loc['coal', 'marginal_cost'] = cost
    network.optimize()
    objectives.append(network.objective)
```

**For advanced studies**, see examples in `references/EXAMPLES.md`.

---

## Reference

### Provided Scripts

| Script | Purpose | Usage |
|---|---|---|
| `scripts/network_analysis.py` | Network inspection and statistics | `from network_analysis import analyze_network` |
| `scripts/optimization_analysis.py` | Optimization results analysis | `from optimization_analysis import analyze_optimization` |
| `scripts/expansion_analysis.py` | Capacity expansion studies | `from expansion_analysis import analyze_expansion` |
| `scripts/contingency_analysis.py` | N-1 contingency analysis | `from contingency_analysis import analyze_n1` |

See [scripts/README.md](scripts/README.md) for complete documentation.

### Typical Workflows

| Goal | Steps |
|---|---|
| Dispatch optimization | Load network → `network.optimize()` → analyze results |
| Capacity expansion | Set extendable components → `network.optimize()` → check `p_nom_opt` |
| N-1 security check | Optimize baseline → `python scripts/contingency_analysis.py network.nc` |
| Sector coupling | Add links between sectors → `network.optimize()` → analyze flows |

### Additional Resources

- **[API Reference](references/API_REFERENCE.md)** -- component types, network methods, data structures
- **[Examples](references/EXAMPLES.md)** -- worked examples from basic to advanced
- **[PyPSA Documentation](https://pypsa.readthedocs.io/)** -- official documentation
