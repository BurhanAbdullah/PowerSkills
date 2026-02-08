# Pandapower Examples

## Example 1: Load and Analyze IEEE Test Case

```python
import pandapower as pp
import pandapower.networks as pn

net = pn.case14()

pp.runpp(net)

print(f"Power flow converged: {net.converged}")
print(f"\nNumber of buses: {len(net.bus)}")
print(f"Number of lines: {len(net.line)}")
print(f"Number of generators: {len(net.gen)}")
print(f"Number of loads: {len(net.load)}")

print("\n=== Bus Voltages ===")
print(net.res_bus[['vm_pu', 'va_degree']])

print("\n=== Line Loading ===")
print(net.res_line[['loading_percent', 'p_from_mw', 'pl_mw']])
```

## Example 2: Create Simple 3-Bus Network

```python
import pandapower as pp

net = pp.create_empty_network(name="Simple 3-Bus System", f_hz=60.0)

bus1 = pp.create_bus(net, vn_kv=110, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=110, name="Gen Bus")
bus3 = pp.create_bus(net, vn_kv=110, name="Load Bus")

pp.create_ext_grid(net, bus=bus1, vm_pu=1.02, va_degree=0, name="Grid Connection")

pp.create_gen(net, bus=bus2, p_mw=40, vm_pu=1.01, name="Generator 1")

pp.create_load(net, bus=bus3, p_mw=50, q_mvar=20, name="Load 1")

pp.create_line_from_parameters(net, from_bus=bus1, to_bus=bus2, length_km=50,
                                r_ohm_per_km=0.1, x_ohm_per_km=0.4, 
                                c_nf_per_km=10, max_i_ka=0.5, name="Line 1-2")

pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus3, length_km=30,
                                r_ohm_per_km=0.1, x_ohm_per_km=0.4,
                                c_nf_per_km=10, max_i_ka=0.5, name="Line 2-3")

pp.create_line_from_parameters(net, from_bus=bus1, to_bus=bus3, length_km=40,
                                r_ohm_per_km=0.1, x_ohm_per_km=0.4,
                                c_nf_per_km=10, max_i_ka=0.5, name="Line 1-3")

pp.runpp(net)

print(f"Converged: {net.converged}")
print("\nBus Results:")
print(net.res_bus)
print("\nLine Results:")
print(net.res_line[['p_from_mw', 'loading_percent', 'pl_mw']])
```

## Example 3: Identify Voltage Violations

```python
import pandapower as pp
import pandapower.networks as pn

net = pn.case_ieee30()
pp.runpp(net)

V_MIN = 0.95
V_MAX = 1.05

undervoltage = net.res_bus[net.res_bus.vm_pu < V_MIN]
overvoltage = net.res_bus[net.res_bus.vm_pu > V_MAX]

print("=== Undervoltage Buses (V < 0.95 p.u.) ===")
if len(undervoltage) > 0:
    for idx in undervoltage.index:
        bus_name = net.bus.at[idx, 'name']
        voltage = undervoltage.at[idx, 'vm_pu']
        print(f"  Bus {idx} ({bus_name}): {voltage:.4f} p.u.")
else:
    print("  No undervoltage violations")

print("\n=== Overvoltage Buses (V > 1.05 p.u.) ===")
if len(overvoltage) > 0:
    for idx in overvoltage.index:
        bus_name = net.bus.at[idx, 'name']
        voltage = overvoltage.at[idx, 'vm_pu']
        print(f"  Bus {idx} ({bus_name}): {voltage:.4f} p.u.")
else:
    print("  No overvoltage violations")

print(f"\nVoltage Range: {net.res_bus.vm_pu.min():.4f} - {net.res_bus.vm_pu.max():.4f} p.u.")
```

## Example 4: Identify Overloaded Elements

```python
import pandapower as pp
import pandapower.networks as pn

net = pn.case39()
pp.runpp(net)

LOADING_LIMIT = 80.0

overloaded_lines = net.res_line[net.res_line.loading_percent > LOADING_LIMIT]
overloaded_trafos = net.res_trafo[net.res_trafo.loading_percent > LOADING_LIMIT]

print(f"=== Overloaded Lines (>{LOADING_LIMIT}%) ===")
if len(overloaded_lines) > 0:
    for idx in overloaded_lines.index:
        line_name = net.line.at[idx, 'name']
        loading = overloaded_lines.at[idx, 'loading_percent']
        from_bus = net.line.at[idx, 'from_bus']
        to_bus = net.line.at[idx, 'to_bus']
        print(f"  Line {idx} ({from_bus}->{to_bus}): {loading:.1f}%")
else:
    print("  No overloaded lines")

print(f"\n=== Overloaded Transformers (>{LOADING_LIMIT}%) ===")
if len(overloaded_trafos) > 0:
    for idx in overloaded_trafos.index:
        loading = overloaded_trafos.at[idx, 'loading_percent']
        hv_bus = net.trafo.at[idx, 'hv_bus']
        lv_bus = net.trafo.at[idx, 'lv_bus']
        print(f"  Trafo {idx} ({hv_bus}->{lv_bus}): {loading:.1f}%")
else:
    print("  No overloaded transformers")
```

## Example 5: N-1 Contingency Analysis

```python
import pandapower as pp
import pandapower.networks as pn
import pandas as pd

net = pn.case14()
pp.runpp(net)

def analyze_contingency(net_copy, element_type, element_idx):
    net_copy[element_type].at[element_idx, 'in_service'] = False
    
    try:
        pp.runpp(net_copy)
        
        if not net_copy.converged:
            return {'status': 'diverged'}
        
        voltage_violations = net_copy.res_bus[
            (net_copy.res_bus.vm_pu < 0.95) | (net_copy.res_bus.vm_pu > 1.05)
        ].index.tolist()
        
        line_violations = net_copy.res_line[
            net_copy.res_line.loading_percent > 100
        ].index.tolist()
        
        trafo_violations = net_copy.res_trafo[
            net_copy.res_trafo.loading_percent > 100
        ].index.tolist()
        
        return {
            'status': 'converged',
            'voltage_violations': voltage_violations,
            'line_overloads': line_violations,
            'trafo_overloads': trafo_violations,
            'min_voltage': net_copy.res_bus.vm_pu.min(),
            'max_loading': max(
                net_copy.res_line.loading_percent.max() if len(net_copy.res_line) > 0 else 0,
                net_copy.res_trafo.loading_percent.max() if len(net_copy.res_trafo) > 0 else 0
            )
        }
    except:
        return {'status': 'failed'}

results = []

for line_idx in net.line.index:
    net_copy = net.deepcopy()
    result = analyze_contingency(net_copy, 'line', line_idx)
    result['contingency'] = f'Line {line_idx}'
    result['element'] = 'line'
    result['element_idx'] = line_idx
    results.append(result)

for trafo_idx in net.trafo.index:
    net_copy = net.deepcopy()
    result = analyze_contingency(net_copy, 'trafo', trafo_idx)
    result['contingency'] = f'Trafo {trafo_idx}'
    result['element'] = 'trafo'
    result['element_idx'] = trafo_idx
    results.append(result)

print("=== N-1 Contingency Analysis Results ===\n")

critical = [r for r in results if r['status'] == 'diverged' or 
            (r['status'] == 'converged' and 
             (r['voltage_violations'] or r['line_overloads'] or r['trafo_overloads']))]

if critical:
    print("Critical Contingencies:")
    for r in critical:
        print(f"\n  {r['contingency']}:")
        if r['status'] == 'diverged':
            print("    Power flow did not converge!")
        else:
            if r['voltage_violations']:
                print(f"    Voltage violations at buses: {r['voltage_violations']}")
            if r['line_overloads']:
                print(f"    Overloaded lines: {r['line_overloads']}")
            if r['trafo_overloads']:
                print(f"    Overloaded transformers: {r['trafo_overloads']}")
else:
    print("No critical contingencies found. System is N-1 secure.")

print(f"\nTotal contingencies analyzed: {len(results)}")
print(f"Critical contingencies: {len(critical)}")
```

## Example 6: Calculate System Losses

```python
import pandapower as pp
import pandapower.networks as pn

net = pn.case_ieee30()
pp.runpp(net)

line_losses_mw = net.res_line.pl_mw.sum()
line_losses_mvar = net.res_line.ql_mvar.sum()

trafo_losses_mw = net.res_trafo.pl_mw.sum() if len(net.res_trafo) > 0 else 0
trafo_losses_mvar = net.res_trafo.ql_mvar.sum() if len(net.res_trafo) > 0 else 0

total_losses_mw = line_losses_mw + trafo_losses_mw
total_losses_mvar = line_losses_mvar + trafo_losses_mvar

total_load_mw = net.res_load.p_mw.sum()
total_generation_mw = net.res_gen.p_mw.sum() + net.res_ext_grid.p_mw.sum()

loss_percentage = (total_losses_mw / total_generation_mw) * 100

print("=== System Loss Analysis ===")
print(f"\nLine Losses:        {line_losses_mw:.2f} MW, {line_losses_mvar:.2f} Mvar")
print(f"Transformer Losses: {trafo_losses_mw:.2f} MW, {trafo_losses_mvar:.2f} Mvar")
print(f"Total Losses:       {total_losses_mw:.2f} MW, {total_losses_mvar:.2f} Mvar")
print(f"\nTotal Generation:   {total_generation_mw:.2f} MW")
print(f"Total Load:         {total_load_mw:.2f} MW")
print(f"Loss Percentage:    {loss_percentage:.2f}%")
```

## Example 7: Load Scaling Study

```python
import pandapower as pp
import pandapower.networks as pn
import matplotlib.pyplot as plt

net = pn.case9()

scaling_factors = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
results = []

original_loads = net.load.p_mw.copy()
original_q_loads = net.load.q_mvar.copy()

for scale in scaling_factors:
    net.load.p_mw = original_loads * scale
    net.load.q_mvar = original_q_loads * scale
    
    pp.runpp(net)
    
    results.append({
        'scale': scale,
        'converged': net.converged,
        'min_voltage': net.res_bus.vm_pu.min() if net.converged else None,
        'max_loading': net.res_line.loading_percent.max() if net.converged else None,
        'total_losses': net.res_line.pl_mw.sum() if net.converged else None
    })

print("=== Load Scaling Study Results ===\n")
print(f"{'Scale':<10} {'Converged':<12} {'Min V (p.u.)':<15} {'Max Loading (%)':<18} {'Losses (MW)':<12}")
print("-" * 70)

for r in results:
    if r['converged']:
        print(f"{r['scale']:<10.2f} {'Yes':<12} {r['min_voltage']:<15.4f} {r['max_loading']:<18.1f} {r['total_losses']:<12.2f}")
    else:
        print(f"{r['scale']:<10.2f} {'No':<12} {'N/A':<15} {'N/A':<18} {'N/A':<12}")

net.load.p_mw = original_loads
net.load.q_mvar = original_q_loads
```

## Example 8: Save and Load Network

```python
import pandapower as pp
import pandapower.networks as pn
import os

net = pn.case14()

pp.create_load(net, bus=5, p_mw=10, q_mvar=5, name="New Load")

pp.runpp(net)

pp.to_json(net, "modified_case14.json")
print("Network saved to modified_case14.json")

loaded_net = pp.from_json("modified_case14.json")

print(f"\nLoaded network has {len(loaded_net.bus)} buses")
print(f"Power flow already run: {loaded_net.converged}")
print(f"Loads: {len(loaded_net.load)}")

os.remove("modified_case14.json")
```

## Example 9: Network Topology Analysis

```python
import pandapower as pp
import pandapower.networks as pn
import pandapower.topology as top

net = pn.case14()

connected = top.connected_components(net)
print(f"Number of connected components: {len(connected)}")

unsupplied = top.unsupplied_buses(net)
print(f"Unsupplied buses: {unsupplied}")

net.line.at[0, 'in_service'] = False
net.line.at[1, 'in_service'] = False

connected_after = top.connected_components(net)
print(f"\nAfter outages:")
print(f"Number of connected components: {len(connected_after)}")

unsupplied_after = top.unsupplied_buses(net)
print(f"Unsupplied buses: {unsupplied_after}")
```

## Example 10: Transformer Tap Adjustment

```python
import pandapower as pp
import pandapower.networks as pn

net = pn.case_ieee30()

target_bus = 12
target_trafo = 0

original_tap = net.trafo.at[target_trafo, 'tap_pos']
tap_min = net.trafo.at[target_trafo, 'tap_min']
tap_max = net.trafo.at[target_trafo, 'tap_max']

print(f"Transformer {target_trafo} tap range: {tap_min} to {tap_max}")
print(f"Original tap position: {original_tap}")

results = []
for tap in range(tap_min, tap_max + 1):
    net.trafo.at[target_trafo, 'tap_pos'] = tap
    pp.runpp(net)
    
    if net.converged:
        voltage = net.res_bus.at[target_bus, 'vm_pu']
        results.append({'tap': tap, 'voltage': voltage})

print(f"\n{'Tap Position':<15} {'Bus {target_bus} Voltage (p.u.)':<25}")
print("-" * 40)
for r in results:
    print(f"{r['tap']:<15} {r['voltage']:<25.4f}")

target_voltage = 1.0
best_tap = min(results, key=lambda x: abs(x['voltage'] - target_voltage))
print(f"\nBest tap position for V={target_voltage} p.u.: {best_tap['tap']} (V={best_tap['voltage']:.4f} p.u.)")
```
