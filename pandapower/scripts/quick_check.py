#!/usr/bin/env python3
"""
Quick power system health check script

Usage:
  python quick_check.py <network_file.json>
  python quick_check.py <network_file.json> --v-min 0.90 --v-max 1.10
"""

import pandapower as pp
import sys
import argparse


def quick_check(
    network_file: str,
    v_min: float = 0.95,
    v_max: float = 1.05,
    loading_limit: float = 100.0
):
    """Quick health check of a pandapower network."""
    
    # Load network
    print(f"Loading: {network_file}")
    net = pp.from_json(network_file)
    
    # Run power flow
    print("Running power flow...")
    try:
        pp.runpp(net)
    except Exception as e:
        print(f"❌ Power flow FAILED: {e}")
        return False
    
    if not net.converged:
        print("❌ Power flow did NOT converge")
        return False
    
    print("✓ Power flow converged\n")
    
    # Check violations
    violations_found = False
    
    # Voltage violations
    undervoltage = net.res_bus[net.res_bus.vm_pu < v_min]
    overvoltage = net.res_bus[net.res_bus.vm_pu > v_max]
    
    if len(undervoltage) > 0:
        violations_found = True
        print(f"⚠️  Undervoltage (< {v_min} p.u.): {len(undervoltage)} buses")
        for idx in undervoltage.index[:5]:  # Show first 5
            print(f"   Bus {idx}: {undervoltage.at[idx, 'vm_pu']:.4f} p.u.")
        if len(undervoltage) > 5:
            print(f"   ... and {len(undervoltage)-5} more")
        print()
    
    if len(overvoltage) > 0:
        violations_found = True
        print(f"⚠️  Overvoltage (> {v_max} p.u.): {len(overvoltage)} buses")
        for idx in overvoltage.index[:5]:  # Show first 5
            print(f"   Bus {idx}: {overvoltage.at[idx, 'vm_pu']:.4f} p.u.")
        if len(overvoltage) > 5:
            print(f"   ... and {len(overvoltage)-5} more")
        print()
    
    # Line overloads
    overloaded_lines = net.res_line[net.res_line.loading_percent > loading_limit]
    if len(overloaded_lines) > 0:
        violations_found = True
        print(f"⚠️  Overloaded lines (> {loading_limit}%): {len(overloaded_lines)}")
        for idx in overloaded_lines.index[:5]:  # Show first 5
            print(f"   Line {idx}: {overloaded_lines.at[idx, 'loading_percent']:.1f}%")
        if len(overloaded_lines) > 5:
            print(f"   ... and {len(overloaded_lines)-5} more")
        print()
    
    # Transformer overloads
    if len(net.trafo) > 0:
        overloaded_trafos = net.res_trafo[net.res_trafo.loading_percent > loading_limit]
        if len(overloaded_trafos) > 0:
            violations_found = True
            print(f"⚠️  Overloaded transformers (> {loading_limit}%): {len(overloaded_trafos)}")
            for idx in overloaded_trafos.index[:5]:  # Show first 5
                print(f"   Trafo {idx}: {overloaded_trafos.at[idx, 'loading_percent']:.1f}%")
            if len(overloaded_trafos) > 5:
                print(f"   ... and {len(overloaded_trafos)-5} more")
            print()
    
    # Summary
    print("="*50)
    if not violations_found:
        print("✓ System is HEALTHY - No violations detected")
    else:
        print("⚠️  VIOLATIONS DETECTED - See details above")
    
    print(f"\nVoltage range: {net.res_bus.vm_pu.min():.4f} - {net.res_bus.vm_pu.max():.4f} p.u.")
    if len(net.res_line) > 0:
        print(f"Max line loading: {net.res_line.loading_percent.max():.1f}%")
    if len(net.trafo) > 0 and len(net.res_trafo) > 0:
        print(f"Max trafo loading: {net.res_trafo.loading_percent.max():.1f}%")
    
    # Losses
    total_losses = net.res_line.pl_mw.sum()
    if len(net.trafo) > 0:
        total_losses += net.res_trafo.pl_mw.sum()
    print(f"Total losses: {total_losses:.2f} MW")
    print("="*50)
    
    return not violations_found


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Quick pandapower network health check')
    parser.add_argument('network_file', help='Path to network JSON file')
    parser.add_argument('--v-min', type=float, default=0.95, help='Minimum voltage (p.u.)')
    parser.add_argument('--v-max', type=float, default=1.05, help='Maximum voltage (p.u.)')
    parser.add_argument('--loading-limit', type=float, default=100.0, help='Loading limit (%%)')
    
    args = parser.parse_args()
    
    success = quick_check(
        args.network_file,
        v_min=args.v_min,
        v_max=args.v_max,
        loading_limit=args.loading_limit
    )
    
    sys.exit(0 if success else 1)
