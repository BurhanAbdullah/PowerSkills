# PyPSA Analysis Scripts

Agent-friendly scripts for power system optimization and analysis. Each script:
- Returns structured data (dicts/lists) suitable for automated decision-making
- Works as both CLI tool and importable Python module
- Uses consistent function naming and return formats

---

## Core Functions for Agents

### `network_analysis.py`

**Main function**: `analyze_network(network)`

Returns comprehensive network inspection combining component counts, capacity mix, load, and extendable components.

```python
from network_analysis import analyze_network

results = analyze_network(network)
# Returns: {'summary': {...}, 'capacity': {...}, 'load': {...}, 'extendable': {...}}

print(f"Total load: {results['load']['total_mwh']} MWh")
print(f"Wind capacity: {results['capacity']['generators']['wind']} MW")
```

**Individual functions**:
- `summarize_network(network)` → dict with component counts and snapshots
- `get_capacity_by_carrier(network)` → dict with capacity grouped by technology
- `get_total_load(network)` → dict with load statistics
- `check_extendable_components(network)` → dict with lists of extendable components
- `print_network_report(results)` → formatted output

---

### `optimization_analysis.py`

**Main function**: `analyze_optimization(network)`

Returns optimization results including generation mix, curtailment, storage operation, and transmission loading.

```python
from optimization_analysis import analyze_optimization

network.optimize()
results = analyze_optimization(network)
# Returns: {'status': {...}, 'generation': {...}, 'curtailment': {...}, 'storage': {...}, 'transmission': {...}}

if results['status']['converged']:
    print(f"Total cost: €{results['status']['objective']}")
    print(f"Wind generation: {results['generation']['by_carrier']['wind']} MWh")
    print(f"Curtailment rate: {results['curtailment']['total_curtailment_rate']*100:.1f}%")
```

**Individual functions**:
- `check_optimization_status(network)` → dict with convergence status and objective
- `get_generation_mix(network)` → dict with generation by carrier/generator
- `get_curtailment(network)` → dict with curtailment statistics
- `get_storage_operation(network)` → dict with storage charge/discharge
- `get_line_loading(network)` → dict with transmission loading
- `print_optimization_report(results)` → formatted output

---

### `expansion_analysis.py`

**Main function**: `analyze_expansion(network)`

Returns capacity expansion results including new capacity, investment costs, and before/after comparison.

```python
from expansion_analysis import analyze_expansion

network.optimize()  # with extendable components
results = analyze_expansion(network)
# Returns: {'new_capacity': {...}, 'investment': {...}, 'capacity_before': {...}, 'capacity_after': {...}}

print(f"Total investment: €{results['investment']['total']}")
print(f"New solar capacity: {results['new_capacity']['generators']['solar']['p_nom_new']} MW")
```

**Individual functions**:
- `get_new_capacity(network)` → dict with capacity additions by component
- `calculate_investment_costs(network)` → dict with investment costs by type/carrier
- `get_capacity_by_carrier(network, use_optimal=True)` → dict with total capacity
- `print_expansion_report(results)` → formatted output

---

### `contingency_analysis.py`

**Main function**: `analyze_n1(network, elements=['line', 'link'], method='optimize')`

Returns N-1 contingency results testing each line/link outage.

```python
from contingency_analysis import analyze_n1, get_critical_contingencies

network.optimize()  # Get baseline
results = analyze_n1(network)
# Returns: [{'element_type': 'line', 'element_name': 'line0', 'converged': True, 'critical': False, ...}, ...]

critical = get_critical_contingencies(results)
if critical:
    print(f"Found {len(critical)} critical contingencies")
    for c in critical:
        print(f"  {c['element_type']} '{c['element_name']}': +€{c.get('objective_increase', 0):,.0f}")
```

**Individual functions**:
- `analyze_single_contingency(network, element_type, element_name)` → dict with contingency result
- `get_critical_contingencies(results)` → list of critical contingencies only
- `get_most_expensive_contingencies(results, top_n=10)` → list of most costly contingencies
- `summarize_n1_results(results)` → dict with counts and cost statistics
- `print_n1_report(results)` → formatted output

---

## Command Line Usage

All scripts work from the command line:

```bash
# Network inspection
python network_analysis.py network.nc

# Optimization analysis (runs optimize() automatically)
python optimization_analysis.py network.nc

# Expansion analysis (runs optimize() automatically)
python expansion_analysis.py network.nc

# N-1 contingency analysis (runs optimize() automatically)
python contingency_analysis.py network.nc
python contingency_analysis.py network.nc --method lpf  # Use linear power flow
```

---

## Return Value Structures

### `analyze_network()` returns:
```python
{
    'summary': {
        'name': str,
        'snapshots': {'count': int, 'start': str, 'end': str, 'freq': str},
        'components': {'buses': int, 'generators': int, ...}
    },
    'capacity': {
        'generators': {carrier: float (MW), ...},
        'storage_units': {carrier: float (MW), ...},
        'stores': {carrier: float (MWh), ...}
    },
    'load': {
        'total_mwh': float,
        'average_mw': float,
        'peak_mw': float,
        'by_bus': {bus_name: float (MWh), ...}
    },
    'extendable': {
        'generators': [name, ...],
        'storage_units': [name, ...],
        'stores': [name, ...],
        'lines': [name, ...],
        'links': [name, ...]
    }
}
```

### `analyze_optimization()` returns:
```python
{
    'status': {
        'optimized': bool,
        'converged': bool,
        'status': str,
        'objective': float,
        'solver': str
    },
    'generation': {
        'by_carrier': {carrier: float (MWh), ...},
        'by_generator': {gen_name: float (MWh), ...},
        'total_mwh': float
    },
    'curtailment': {
        'by_generator': {
            gen_name: {'available': float, 'used': float, 'curtailed': float, 'curtailment_rate': float},
            ...
        },
        'total_curtailed_mwh': float,
        'total_curtailment_rate': float
    },
    'storage': {
        'storage_units': {
            name: {'charge_mwh': float, 'discharge_mwh': float, 'cycles': float},
            ...
        },
        'stores': {
            name: {'min_energy_mwh': float, 'max_energy_mwh': float, 'avg_energy_mwh': float},
            ...
        }
    },
    'transmission': {
        'lines': {
            line_name: {'max_loading': float, 'avg_loading': float, 'congested_hours': int},
            ...
        },
        'most_congested': [(line_name, max_loading), ...]
    }
}
```

### `analyze_expansion()` returns:
```python
{
    'new_capacity': {
        'generators': {
            name: {'p_nom_old': float, 'p_nom_opt': float, 'p_nom_new': float, 'carrier': str},
            ...
        },
        'storage_units': {...},
        'stores': {...},
        'lines': {...},
        'links': {...}
    },
    'investment': {
        'by_component_type': {'generators': float, 'storage_units': float, ...},
        'by_carrier': {carrier: float, ...},
        'total': float
    },
    'capacity_before': {carrier: float (MW), ...},
    'capacity_after': {carrier: float (MW), ...}
}
```

### `analyze_n1()` returns:
```python
[
    {
        'element_type': 'line',
        'element_name': 'line0',
        'converged': bool,
        'critical': bool,
        'objective': float (if converged),
        'objective_increase': float (if baseline available),
        'objective_increase_pct': float,
        'voltage_violations': [bus_name, ...],
        'overloaded_lines': [line_name, ...],
        'overloaded_links': [link_name, ...],
        'line_loading': {line_name: max_loading_pct, ...},
        'link_loading': {link_name: max_loading_pct, ...}
    },
    ...
]
```

---

## Design Principles

1. **Structured returns**: All functions return dicts/lists, not just print statements
2. **Composable**: Individual functions can be combined for custom workflows
3. **Consistent naming**: `analyze_*` for main functions, `get_*` for data extraction, `calculate_*` for computations
4. **Agent-friendly**: Return values are designed for programmatic decision-making
5. **CLI + module**: Works from command line and as importable Python module

---

## Example Agent Workflow

```python
import pypsa
from network_analysis import analyze_network
from optimization_analysis import analyze_optimization
from expansion_analysis import analyze_expansion
from contingency_analysis import analyze_n1, get_critical_contingencies

# Load network
network = pypsa.Network("network.nc")

# Inspect network
network_info = analyze_network(network)
print(f"Network has {network_info['summary']['components']['generators']} generators")

# Run optimization
network.optimize()
opt_results = analyze_optimization(network)

if opt_results['status']['converged']:
    print(f"Optimization successful: €{opt_results['status']['objective']:,.0f}")
    
    # Check for renewable curtailment
    if opt_results['curtailment']['total_curtailment_rate'] > 0.10:
        print(f"High curtailment detected: {opt_results['curtailment']['total_curtailment_rate']*100:.1f}%")
    
    # Check for transmission congestion
    congested = [line for line, stats in opt_results['transmission']['lines'].items() 
                 if stats['congested_hours'] > 100]
    if congested:
        print(f"Congested lines: {congested}")
    
    # Run N-1 contingency analysis
    n1_results = analyze_n1(network, elements=['line', 'link'])
    critical = get_critical_contingencies(n1_results)
    
    if critical:
        print(f"System is NOT N-1 secure: {len(critical)} critical contingencies")
        # Show most expensive contingencies
        expensive = sorted([c for c in critical if 'objective_increase' in c],
                          key=lambda x: x['objective_increase'], reverse=True)[:3]
        for c in expensive:
            print(f"  {c['element_type']} '{c['element_name']}': +€{c['objective_increase']:,.0f}")
    else:
        print("System is N-1 secure")
    
    # Analyze capacity expansion (if extendable components)
    if network_info['extendable']['generators']:
        exp_results = analyze_expansion(network)
        print(f"Total investment: €{exp_results['investment']['total']:,.0f}")
else:
    print(f"Optimization failed: {opt_results['status']['status']}")
```
