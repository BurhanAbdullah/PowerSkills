#!/usr/bin/env python3
"""
Common power system analysis functions for pandapower networks
"""

import pandapower as pp
import pandas as pd
from typing import Dict, List, Tuple


def check_voltage_violations(
    net: pp.pandapowerNet,
    v_min: float = 0.95,
    v_max: float = 1.05
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Check for voltage violations in the network.
    
    Args:
        net: pandapower network (must have results from runpp)
        v_min: Minimum voltage limit in p.u.
        v_max: Maximum voltage limit in p.u.
        
    Returns:
        Tuple of (undervoltage_df, overvoltage_df)
    """
    undervoltage = net.res_bus[net.res_bus.vm_pu < v_min].copy()
    overvoltage = net.res_bus[net.res_bus.vm_pu > v_max].copy()
    
    # Add bus names if available
    if 'name' in net.bus.columns:
        undervoltage['bus_name'] = undervoltage.index.map(lambda x: net.bus.at[x, 'name'])
        overvoltage['bus_name'] = overvoltage.index.map(lambda x: net.bus.at[x, 'name'])
    
    return undervoltage, overvoltage


def check_loading_violations(
    net: pp.pandapowerNet,
    loading_limit: float = 100.0
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Check for equipment overloading in the network.
    
    Args:
        net: pandapower network (must have results from runpp)
        loading_limit: Maximum loading percentage
        
    Returns:
        Tuple of (overloaded_lines_df, overloaded_trafos_df)
    """
    overloaded_lines = net.res_line[
        net.res_line.loading_percent > loading_limit
    ].copy()
    
    overloaded_trafos = pd.DataFrame()
    if len(net.trafo) > 0:
        overloaded_trafos = net.res_trafo[
            net.res_trafo.loading_percent > loading_limit
        ].copy()
    
    # Add element names if available
    if 'name' in net.line.columns:
        overloaded_lines['line_name'] = overloaded_lines.index.map(
            lambda x: net.line.at[x, 'name']
        )
    
    if len(overloaded_trafos) > 0 and 'name' in net.trafo.columns:
        overloaded_trafos['trafo_name'] = overloaded_trafos.index.map(
            lambda x: net.trafo.at[x, 'name']
        )
    
    return overloaded_lines, overloaded_trafos


def calculate_system_losses(net: pp.pandapowerNet) -> Dict[str, float]:
    """
    Calculate total system losses.
    
    Args:
        net: pandapower network (must have results from runpp)
        
    Returns:
        Dictionary with loss information
    """
    # Line losses
    line_losses_mw = net.res_line.pl_mw.sum()
    line_losses_mvar = net.res_line.ql_mvar.sum()
    
    # Transformer losses
    trafo_losses_mw = 0
    trafo_losses_mvar = 0
    if len(net.trafo) > 0:
        trafo_losses_mw = net.res_trafo.pl_mw.sum()
        trafo_losses_mvar = net.res_trafo.ql_mvar.sum()
    
    # Total losses
    total_losses_mw = line_losses_mw + trafo_losses_mw
    total_losses_mvar = line_losses_mvar + trafo_losses_mvar
    
    # Total generation and load
    total_generation_mw = 0
    if len(net.res_gen) > 0:
        total_generation_mw += net.res_gen.p_mw.sum()
    if len(net.res_ext_grid) > 0:
        total_generation_mw += net.res_ext_grid.p_mw.sum()
    
    total_load_mw = net.res_load.p_mw.sum() if len(net.res_load) > 0 else 0
    
    # Loss percentage
    loss_percentage = (total_losses_mw / total_generation_mw * 100) if total_generation_mw > 0 else 0
    
    return {
        'line_losses_mw': line_losses_mw,
        'line_losses_mvar': line_losses_mvar,
        'trafo_losses_mw': trafo_losses_mw,
        'trafo_losses_mvar': trafo_losses_mvar,
        'total_losses_mw': total_losses_mw,
        'total_losses_mvar': total_losses_mvar,
        'total_generation_mw': total_generation_mw,
        'total_load_mw': total_load_mw,
        'loss_percentage': loss_percentage
    }


def print_network_summary(net: pp.pandapowerNet, include_results: bool = True):
    """
    Print a comprehensive network summary.
    
    Args:
        net: pandapower network
        include_results: Whether to include power flow results
    """
    print("="*60)
    print(f"Network: {net.name if hasattr(net, 'name') else 'Unnamed'}")
    print("="*60)
    
    # Network elements
    print("\nNetwork Elements:")
    print(f"  Buses:            {len(net.bus)}")
    print(f"  Lines:            {len(net.line)}")
    print(f"  Transformers:     {len(net.trafo)}")
    print(f"  Loads:            {len(net.load)}")
    print(f"  Generators:       {len(net.gen)}")
    print(f"  External Grids:   {len(net.ext_grid)}")
    
    if include_results and hasattr(net, 'converged'):
        print(f"\nPower Flow Status: {'CONVERGED' if net.converged else 'NOT CONVERGED'}")
        
        if net.converged:
            # Voltage summary
            print(f"\nVoltage Summary:")
            print(f"  Min: {net.res_bus.vm_pu.min():.4f} p.u.")
            print(f"  Max: {net.res_bus.vm_pu.max():.4f} p.u.")
            print(f"  Avg: {net.res_bus.vm_pu.mean():.4f} p.u.")
            
            # Loading summary
            if len(net.res_line) > 0:
                print(f"\nLine Loading:")
                print(f"  Max: {net.res_line.loading_percent.max():.1f}%")
                print(f"  Avg: {net.res_line.loading_percent.mean():.1f}%")
            
            if len(net.trafo) > 0 and len(net.res_trafo) > 0:
                print(f"\nTransformer Loading:")
                print(f"  Max: {net.res_trafo.loading_percent.max():.1f}%")
                print(f"  Avg: {net.res_trafo.loading_percent.mean():.1f}%")
            
            # Losses
            losses = calculate_system_losses(net)
            print(f"\nSystem Losses:")
            print(f"  Total: {losses['total_losses_mw']:.2f} MW ({losses['loss_percentage']:.2f}%)")
            print(f"  Lines: {losses['line_losses_mw']:.2f} MW")
            print(f"  Trafos: {losses['trafo_losses_mw']:.2f} MW")
    
    print("="*60)


def run_comprehensive_check(
    net: pp.pandapowerNet,
    v_min: float = 0.95,
    v_max: float = 1.05,
    loading_limit: float = 100.0,
    verbose: bool = True
) -> Dict[str, any]:
    """
    Run comprehensive network checks and return results.
    
    Args:
        net: pandapower network
        v_min: Minimum voltage limit in p.u.
        v_max: Maximum voltage limit in p.u.
        loading_limit: Maximum loading percentage
        verbose: Print detailed output
        
    Returns:
        Dictionary with check results
    """
    # Run power flow if not already done
    if not hasattr(net, 'converged') or not net.converged:
        pp.runpp(net)
    
    if not net.converged:
        return {
            'converged': False,
            'error': 'Power flow did not converge'
        }
    
    # Check violations
    undervoltage, overvoltage = check_voltage_violations(net, v_min, v_max)
    overloaded_lines, overloaded_trafos = check_loading_violations(net, loading_limit)
    losses = calculate_system_losses(net)
    
    results = {
        'converged': True,
        'voltage': {
            'min': net.res_bus.vm_pu.min(),
            'max': net.res_bus.vm_pu.max(),
            'mean': net.res_bus.vm_pu.mean(),
            'undervoltage_count': len(undervoltage),
            'overvoltage_count': len(overvoltage),
            'undervoltage_buses': undervoltage.index.tolist(),
            'overvoltage_buses': overvoltage.index.tolist()
        },
        'loading': {
            'max_line_loading': net.res_line.loading_percent.max() if len(net.res_line) > 0 else 0,
            'max_trafo_loading': net.res_trafo.loading_percent.max() if len(net.trafo) > 0 else 0,
            'overloaded_lines_count': len(overloaded_lines),
            'overloaded_trafos_count': len(overloaded_trafos),
            'overloaded_lines': overloaded_lines.index.tolist(),
            'overloaded_trafos': overloaded_trafos.index.tolist()
        },
        'losses': losses,
        'has_violations': (
            len(undervoltage) > 0 or 
            len(overvoltage) > 0 or 
            len(overloaded_lines) > 0 or 
            len(overloaded_trafos) > 0
        )
    }
    
    if verbose:
        print("\n" + "="*60)
        print("COMPREHENSIVE NETWORK CHECK")
        print("="*60)
        print(f"\nPower Flow: {'CONVERGED' if results['converged'] else 'FAILED'}")
        
        print(f"\nVoltage Analysis:")
        print(f"  Range: {results['voltage']['min']:.4f} - {results['voltage']['max']:.4f} p.u.")
        print(f"  Undervoltage buses (< {v_min}): {results['voltage']['undervoltage_count']}")
        print(f"  Overvoltage buses (> {v_max}): {results['voltage']['overvoltage_count']}")
        
        print(f"\nLoading Analysis:")
        print(f"  Max line loading: {results['loading']['max_line_loading']:.1f}%")
        print(f"  Max trafo loading: {results['loading']['max_trafo_loading']:.1f}%")
        print(f"  Overloaded lines (> {loading_limit}%): {results['loading']['overloaded_lines_count']}")
        print(f"  Overloaded trafos (> {loading_limit}%): {results['loading']['overloaded_trafos_count']}")
        
        print(f"\nSystem Losses:")
        print(f"  Total: {results['losses']['total_losses_mw']:.2f} MW ({results['losses']['loss_percentage']:.2f}%)")
        
        print(f"\nOverall Status: {'⚠️  VIOLATIONS DETECTED' if results['has_violations'] else '✓ SYSTEM HEALTHY'}")
        print("="*60 + "\n")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python network_analysis.py <network_file.json>")
        sys.exit(1)
    
    network_file = sys.argv[1]
    
    # Load and analyze network
    print(f"Loading network from {network_file}...")
    net = pp.from_json(network_file)
    
    print("\nRunning power flow...")
    pp.runpp(net)
    
    # Print summary
    print_network_summary(net)
    
    # Run comprehensive check
    print("\n")
    results = run_comprehensive_check(net, verbose=True)
