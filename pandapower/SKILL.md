---
name: pandapower-analysis
description: Perform power system analysis using pandapower including power flow calculations, contingency analysis, network creation, and result interpretation. Use when the user asks about power flow, load flow, voltage analysis, line loading, transformer analysis, N-1 contingency, or working with pandapower networks.
compatibility: Requires Python 3.10+ and pandapower library
metadata:
  author: PowerSkills
  version: "1.0"
---

# Pandapower Power System Analysis

## Quick Start

```python
import pandapower as pp

net = pp.from_json("network.json")
pp.runpp(net)

print(f"Converged: {net.converged}")
print(net.res_bus)
```

## Core Operations

### Loading Networks

```python
net = pp.from_json("path/to/network.json")

net = pp.from_pickle("path/to/network.p")

net = pp.networks.case9()
net = pp.networks.case14()
net = pp.networks.case_ieee30()
```

### Creating Empty Network

```python
net = pp.create_empty_network(name="My Network", f_hz=60.0, sn_mva=100)
```

### Running Power Flow

```python
pp.runpp(net)

pp.runpp(net, 
         algorithm='nr',
         calculate_voltage_angles=True,
         max_iteration=10,
         tolerance_mva=1e-8)
```

Algorithm options: `'nr'` (Newton-Raphson), `'bfsw'` (backward/forward sweep for radial networks)

### Checking Results

```python
if net.converged:
    print("Bus voltages:", net.res_bus[['vm_pu', 'va_degree']])
    print("Line loading:", net.res_line[['loading_percent', 'p_from_mw']])
    print("Transformer loading:", net.res_trafo['loading_percent'])
```

## Network Elements

### Adding Buses

```python
bus_idx = pp.create_bus(net, vn_kv=110, name="HV Bus")
```

### Adding Lines

```python
line_idx = pp.create_line(net, 
                          from_bus=0, 
                          to_bus=1, 
                          length_km=10, 
                          std_type="N2XS(FL)2Y 1x300 RM/35 64/110 kV")
```

### Adding Transformers

```python
trafo_idx = pp.create_transformer(net, 
                                   hv_bus=0, 
                                   lv_bus=1, 
                                   std_type="25 MVA 110/20 kV")
```

### Adding Loads

```python
load_idx = pp.create_load(net, bus=1, p_mw=2.0, q_mvar=0.5)
```

### Adding Generators

```python
gen_idx = pp.create_gen(net, bus=0, p_mw=50, vm_pu=1.02)
```

### Adding External Grid (Slack)

```python
ext_grid_idx = pp.create_ext_grid(net, bus=0, vm_pu=1.02, va_degree=0)
```

## Contingency Analysis

### N-1 Analysis Pattern

```python
def run_n1_contingency(net):
    results = []
    original_net = net.deepcopy()
    
    for line_idx in net.line.index:
        test_net = original_net.deepcopy()
        test_net.line.at[line_idx, 'in_service'] = False
        
        try:
            pp.runpp(test_net)
            
            voltage_violations = test_net.res_bus[
                (test_net.res_bus.vm_pu < 0.95) | 
                (test_net.res_bus.vm_pu > 1.05)
            ].index.tolist()
            
            loading_violations = test_net.res_line[
                test_net.res_line.loading_percent > 100
            ].index.tolist()
            
            results.append({
                'contingency': f'line_{line_idx}',
                'converged': test_net.converged,
                'voltage_violations': voltage_violations,
                'loading_violations': loading_violations
            })
        except:
            results.append({
                'contingency': f'line_{line_idx}',
                'converged': False
            })
    
    return results
```

## Result Tables

After running power flow, results are stored in `res_*` DataFrames:

| Table | Key Columns |
|-------|-------------|
| `net.res_bus` | `vm_pu`, `va_degree`, `p_mw`, `q_mvar` |
| `net.res_line` | `p_from_mw`, `q_from_mvar`, `loading_percent`, `i_ka` |
| `net.res_trafo` | `p_hv_mw`, `loading_percent`, `i_hv_ka` |
| `net.res_gen` | `p_mw`, `q_mvar`, `vm_pu` |
| `net.res_load` | `p_mw`, `q_mvar` |
| `net.res_ext_grid` | `p_mw`, `q_mvar` |

## Common Checks

### Voltage Violations

```python
undervoltage = net.res_bus[net.res_bus.vm_pu < 0.95]
overvoltage = net.res_bus[net.res_bus.vm_pu > 1.05]
```

### Line Overloads

```python
overloaded_lines = net.res_line[net.res_line.loading_percent > 100]
```

### Transformer Overloads

```python
overloaded_trafos = net.res_trafo[net.res_trafo.loading_percent > 100]
```

## Saving Networks

```python
pp.to_json(net, "network.json")

pp.to_pickle(net, "network.p")
```

## Additional Resources

- For detailed API reference, see [references/API_REFERENCE.md](references/API_REFERENCE.md)
- For practical examples, see [references/EXAMPLES.md](references/EXAMPLES.md)
- [Pandapower Documentation](https://pandapower.readthedocs.io/)
