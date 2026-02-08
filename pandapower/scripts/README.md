# Pandapower Analysis Scripts

Reusable Python scripts for power system analysis with pandapower.

## Scripts Overview

### 1. `quick_check.py` - Fast Network Health Check

Quick verification of network status with violation detection.

**Command Line Usage:**
```bash
# Basic check
python quick_check.py network.json

# Custom limits
python quick_check.py network.json --v-min 0.90 --v-max 1.10 --loading-limit 80
```

**Output:**
- Power flow convergence status
- Voltage violations (undervoltage/overvoltage)
- Equipment overloading (lines/transformers)
- System summary (voltage range, max loading, losses)

---

### 2. `contingency_analysis.py` - N-1 Contingency Analysis

Comprehensive N-1 contingency analysis for lines and transformers.

**Command Line Usage:**
```bash
python contingency_analysis.py network.json
```

**Python Usage:**
```python
from contingency_analysis import run_n1_analysis, generate_contingency_report

# Run N-1 analysis
results_df = run_n1_analysis(
    net, 
    elements=['line', 'trafo'],
    v_min=0.95,
    v_max=1.05,
    loading_limit=100.0,
    verbose=True
)

# Generate report
report = generate_contingency_report(results_df, output_file='report.txt')
```

**Features:**
- Tests each line and transformer outage
- Detects convergence failures
- Identifies voltage violations
- Flags equipment overloading
- Generates detailed reports

**Output:**
- DataFrame with all contingency results
- Text report with critical contingencies
- Summary statistics

---

### 3. `network_analysis.py` - Analysis Function Library

Reusable functions for common power system analysis tasks.

**Available Functions:**

#### `check_voltage_violations(net, v_min=0.95, v_max=1.05)`
Returns DataFrames of undervoltage and overvoltage buses.

```python
from network_analysis import check_voltage_violations

pp.runpp(net)
undervoltage, overvoltage = check_voltage_violations(net)
print(f"Undervoltage buses: {len(undervoltage)}")
```

#### `check_loading_violations(net, loading_limit=100.0)`
Returns DataFrames of overloaded lines and transformers.

```python
from network_analysis import check_loading_violations

overloaded_lines, overloaded_trafos = check_loading_violations(net)
print(f"Overloaded lines: {len(overloaded_lines)}")
```

#### `calculate_system_losses(net)`
Calculates total system losses (lines + transformers).

```python
from network_analysis import calculate_system_losses

losses = calculate_system_losses(net)
print(f"Total: {losses['total_losses_mw']:.2f} MW ({losses['loss_percentage']:.2f}%)")
print(f"Lines: {losses['line_losses_mw']:.2f} MW")
print(f"Trafos: {losses['trafo_losses_mw']:.2f} MW")
```

#### `print_network_summary(net, include_results=True)`
Prints comprehensive network summary.

```python
from network_analysis import print_network_summary

pp.runpp(net)
print_network_summary(net)
```

#### `run_comprehensive_check(net, v_min=0.95, v_max=1.05, loading_limit=100.0, verbose=True)`
Runs all checks and returns structured results.

```python
from network_analysis import run_comprehensive_check

results = run_comprehensive_check(net, verbose=True)

if results['has_violations']:
    print("Violations found:")
    print(f"  Undervoltage: {results['voltage']['undervoltage_count']}")
    print(f"  Overloaded lines: {results['loading']['overloaded_lines_count']}")
```

**Returns:**
```python
{
    'converged': True,
    'voltage': {
        'min': 0.9876,
        'max': 1.0234,
        'undervoltage_count': 2,
        'overvoltage_count': 0,
        'undervoltage_buses': [5, 7],
        'overvoltage_buses': []
    },
    'loading': {
        'max_line_loading': 87.5,
        'max_trafo_loading': 95.2,
        'overloaded_lines_count': 0,
        'overloaded_trafos_count': 0
    },
    'losses': {
        'total_losses_mw': 5.67,
        'loss_percentage': 2.34
    },
    'has_violations': True
}
```

---

## Installation

Ensure pandapower is installed:

```bash
pip install pandapower
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

---

## Examples

### Example 1: Quick Daily Check

```bash
#!/bin/bash
# daily_check.sh

for network in networks/*.json; do
    echo "Checking $network..."
    python scripts/quick_check.py "$network"
    echo ""
done
```

### Example 2: Automated N-1 Analysis

```python
#!/usr/bin/env python3
# automated_n1.py

import pandapower as pp
from scripts.contingency_analysis import run_n1_analysis, generate_contingency_report

# Load network
net = pp.from_json("network.json")

# Run baseline
pp.runpp(net)
print(f"Baseline: {net.converged}")

# Run N-1 analysis
results = run_n1_analysis(net, verbose=False)

# Generate report
report = generate_contingency_report(results, output_file="daily_n1_report.txt")

# Email critical contingencies
critical = results[results['has_violations']]
if len(critical) > 0:
    print(f"ALERT: {len(critical)} critical contingencies found!")
    # Send email notification...
```

### Example 3: Custom Analysis Pipeline

```python
import pandapower as pp
from scripts.network_analysis import (
    run_comprehensive_check,
    calculate_system_losses,
    print_network_summary
)

# Load network
net = pp.from_json("network.json")
pp.runpp(net)

# Print summary
print_network_summary(net)

# Run checks
results = run_comprehensive_check(net, v_min=0.93, v_max=1.07)

# Calculate losses
losses = calculate_system_losses(net)

# Custom analysis
if losses['loss_percentage'] > 3.0:
    print(f"WARNING: High losses detected: {losses['loss_percentage']:.2f}%")
```

---

## Script Parameters

### Voltage Limits
- **Default**: 0.95 - 1.05 p.u. (typical North American/European standards)
- **Relaxed**: 0.90 - 1.10 p.u.
- **Strict**: 0.97 - 1.03 p.u.

### Loading Limits
- **Default**: 100% (emergency rating)
- **Normal**: 80% (normal operating limit)
- **Conservative**: 70%

---

## Output Files

Scripts may generate the following files:

- `contingency_report.txt` - N-1 analysis report
- Network JSON/pickle files
- Custom analysis results

---

## Troubleshooting

**Power flow doesn't converge:**
- Check for isolated buses/islands
- Verify slack bus exists
- Check for unrealistic parameters

**Script import errors:**
- Ensure you're running from the skill directory
- Or add to Python path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"`

**Memory issues with large networks:**
- Process contingencies in batches
- Use `verbose=False` to reduce output
- Consider parallel processing for very large systems
