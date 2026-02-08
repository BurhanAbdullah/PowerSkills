#!/usr/bin/env python3
"""
N-1 Contingency Analysis for pandapower networks

This script performs comprehensive N-1 contingency analysis on power systems,
checking for voltage violations and equipment overloading.
"""

import pandapower as pp
import pandas as pd
from typing import Dict, List, Any


def analyze_single_contingency(
    net_copy: pp.pandapowerNet,
    element_type: str,
    element_idx: int,
    v_min: float = 0.95,
    v_max: float = 1.05,
    loading_limit: float = 100.0
) -> Dict[str, Any]:
    """
    Analyze a single contingency scenario.
    
    Args:
        net_copy: Copy of the pandapower network
        element_type: Type of element ('line', 'trafo', 'trafo3w')
        element_idx: Index of the element to disconnect
        v_min: Minimum voltage limit in p.u.
        v_max: Maximum voltage limit in p.u.
        loading_limit: Maximum loading percentage
        
    Returns:
        Dictionary with contingency results
    """
    # Disconnect the element
    net_copy[element_type].at[element_idx, 'in_service'] = False
    
    try:
        pp.runpp(net_copy)
        
        if not net_copy.converged:
            return {
                'status': 'diverged',
                'converged': False
            }
        
        # Check voltage violations
        voltage_violations = net_copy.res_bus[
            (net_copy.res_bus.vm_pu < v_min) | 
            (net_copy.res_bus.vm_pu > v_max)
        ].index.tolist()
        
        # Check line overloads
        line_violations = []
        if len(net_copy.res_line) > 0:
            line_violations = net_copy.res_line[
                net_copy.res_line.loading_percent > loading_limit
            ].index.tolist()
        
        # Check transformer overloads
        trafo_violations = []
        if len(net_copy.res_trafo) > 0:
            trafo_violations = net_copy.res_trafo[
                net_copy.res_trafo.loading_percent > loading_limit
            ].index.tolist()
        
        # Calculate severity metrics
        min_voltage = net_copy.res_bus.vm_pu.min()
        max_voltage = net_copy.res_bus.vm_pu.max()
        
        max_line_loading = net_copy.res_line.loading_percent.max() if len(net_copy.res_line) > 0 else 0
        max_trafo_loading = net_copy.res_trafo.loading_percent.max() if len(net_copy.res_trafo) > 0 else 0
        max_loading = max(max_line_loading, max_trafo_loading)
        
        return {
            'status': 'converged',
            'converged': True,
            'voltage_violations': voltage_violations,
            'line_overloads': line_violations,
            'trafo_overloads': trafo_violations,
            'min_voltage': min_voltage,
            'max_voltage': max_voltage,
            'max_loading': max_loading,
            'has_violations': bool(voltage_violations or line_violations or trafo_violations)
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'converged': False,
            'error': str(e)
        }


def run_n1_analysis(
    net: pp.pandapowerNet,
    elements: List[str] = ['line', 'trafo'],
    v_min: float = 0.95,
    v_max: float = 1.05,
    loading_limit: float = 100.0,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Run comprehensive N-1 contingency analysis.
    
    Args:
        net: pandapower network
        elements: List of element types to analyze ('line', 'trafo', 'trafo3w')
        v_min: Minimum voltage limit in p.u.
        v_max: Maximum voltage limit in p.u.
        loading_limit: Maximum loading percentage
        verbose: Print progress messages
        
    Returns:
        DataFrame with contingency analysis results
    """
    results = []
    
    # Analyze line contingencies
    if 'line' in elements:
        for line_idx in net.line.index:
            if verbose:
                print(f"Analyzing line {line_idx} outage...")
            
            net_copy = net.deepcopy()
            result = analyze_single_contingency(
                net_copy, 'line', line_idx, v_min, v_max, loading_limit
            )
            result['contingency'] = f'Line {line_idx}'
            result['element_type'] = 'line'
            result['element_idx'] = line_idx
            
            # Add element details
            result['from_bus'] = net.line.at[line_idx, 'from_bus']
            result['to_bus'] = net.line.at[line_idx, 'to_bus']
            result['element_name'] = net.line.at[line_idx, 'name'] if 'name' in net.line.columns else ''
            
            results.append(result)
    
    # Analyze transformer contingencies
    if 'trafo' in elements and len(net.trafo) > 0:
        for trafo_idx in net.trafo.index:
            if verbose:
                print(f"Analyzing trafo {trafo_idx} outage...")
            
            net_copy = net.deepcopy()
            result = analyze_single_contingency(
                net_copy, 'trafo', trafo_idx, v_min, v_max, loading_limit
            )
            result['contingency'] = f'Trafo {trafo_idx}'
            result['element_type'] = 'trafo'
            result['element_idx'] = trafo_idx
            
            # Add element details
            result['from_bus'] = net.trafo.at[trafo_idx, 'hv_bus']
            result['to_bus'] = net.trafo.at[trafo_idx, 'lv_bus']
            result['element_name'] = net.trafo.at[trafo_idx, 'name'] if 'name' in net.trafo.columns else ''
            
            results.append(result)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"N-1 Contingency Analysis Complete")
        print(f"{'='*60}")
        print(f"Total contingencies analyzed: {len(results)}")
        print(f"Failed to converge: {len(df[df['status'] == 'diverged'])}")
        print(f"With violations: {len(df[df.get('has_violations', False)])}")
        print(f"{'='*60}\n")
    
    return df


def generate_contingency_report(results_df: pd.DataFrame, output_file: str = None) -> str:
    """
    Generate a detailed contingency analysis report.
    
    Args:
        results_df: DataFrame from run_n1_analysis()
        output_file: Optional file path to save report
        
    Returns:
        Report as a string
    """
    report = []
    report.append("="*80)
    report.append("N-1 CONTINGENCY ANALYSIS REPORT")
    report.append("="*80)
    report.append("")
    
    # Summary statistics
    total = len(results_df)
    diverged = len(results_df[results_df['status'] == 'diverged'])
    failed = len(results_df[results_df['status'] == 'failed'])
    with_violations = len(results_df[results_df.get('has_violations', False)])
    
    report.append(f"Total Contingencies:    {total}")
    report.append(f"Converged:              {total - diverged - failed}")
    report.append(f"Diverged:               {diverged}")
    report.append(f"Failed:                 {failed}")
    report.append(f"With Violations:        {with_violations}")
    report.append("")
    
    # Critical contingencies
    critical = results_df[
        (results_df['status'] == 'diverged') | 
        (results_df.get('has_violations', False))
    ]
    
    if len(critical) > 0:
        report.append("="*80)
        report.append("CRITICAL CONTINGENCIES")
        report.append("="*80)
        report.append("")
        
        for idx, row in critical.iterrows():
            report.append(f"Contingency: {row['contingency']}")
            
            if row['status'] == 'diverged':
                report.append("  Status: POWER FLOW DID NOT CONVERGE")
            elif row['status'] == 'failed':
                report.append(f"  Status: FAILED - {row.get('error', 'Unknown error')}")
            else:
                if row.get('voltage_violations'):
                    report.append(f"  Voltage violations at buses: {row['voltage_violations']}")
                    report.append(f"  Min voltage: {row['min_voltage']:.4f} p.u.")
                    report.append(f"  Max voltage: {row['max_voltage']:.4f} p.u.")
                
                if row.get('line_overloads'):
                    report.append(f"  Overloaded lines: {row['line_overloads']}")
                
                if row.get('trafo_overloads'):
                    report.append(f"  Overloaded transformers: {row['trafo_overloads']}")
                
                if row.get('max_loading'):
                    report.append(f"  Max loading: {row['max_loading']:.1f}%")
            
            report.append("")
    else:
        report.append("="*80)
        report.append("NO CRITICAL CONTINGENCIES FOUND")
        report.append("System is N-1 secure for all analyzed contingencies.")
        report.append("="*80)
    
    report_text = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"Report saved to: {output_file}")
    
    return report_text


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python contingency_analysis.py <network_file.json>")
        sys.exit(1)
    
    network_file = sys.argv[1]
    
    # Load network
    print(f"Loading network from {network_file}...")
    net = pp.from_json(network_file)
    
    # Run baseline power flow
    print("Running baseline power flow...")
    pp.runpp(net)
    
    if not net.converged:
        print("ERROR: Baseline power flow did not converge!")
        sys.exit(1)
    
    print(f"Baseline converged: {net.converged}")
    print(f"Network has {len(net.bus)} buses, {len(net.line)} lines, {len(net.trafo)} transformers")
    print()
    
    # Run N-1 analysis
    results = run_n1_analysis(net, elements=['line', 'trafo'], verbose=True)
    
    # Generate report
    report = generate_contingency_report(results, output_file='contingency_report.txt')
    print(report)
