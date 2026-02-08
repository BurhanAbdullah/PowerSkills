#!/usr/bin/env python3
"""
Quick test to validate all pandapower scripts work correctly
"""

import sys
import os
import pandapower as pp

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from network_analysis import (
    check_voltage_violations,
    check_loading_violations,
    calculate_system_losses,
    run_comprehensive_check,
    print_network_summary
)
from contingency_analysis import run_n1_analysis, generate_contingency_report


def test_network_analysis():
    """Test network_analysis.py functions"""
    print("="*60)
    print("Testing network_analysis.py")
    print("="*60)
    
    # Create test network
    net = pp.networks.case14()
    pp.runpp(net)
    
    # Test voltage violations
    undervoltage, overvoltage = check_voltage_violations(net)
    print(f"✓ check_voltage_violations: {len(undervoltage)} under, {len(overvoltage)} over")
    
    # Test loading violations
    overloaded_lines, overloaded_trafos = check_loading_violations(net)
    print(f"✓ check_loading_violations: {len(overloaded_lines)} lines, {len(overloaded_trafos)} trafos")
    
    # Test losses
    losses = calculate_system_losses(net)
    print(f"✓ calculate_system_losses: {losses['total_losses_mw']:.2f} MW")
    
    # Test comprehensive check
    results = run_comprehensive_check(net, verbose=False)
    print(f"✓ run_comprehensive_check: Converged={results['converged']}, Violations={results['has_violations']}")
    
    # Test summary
    print("\n✓ print_network_summary:")
    print_network_summary(net, include_results=True)
    
    print("\n✓ All network_analysis.py tests passed!\n")
    return True


def test_contingency_analysis():
    """Test contingency_analysis.py functions"""
    print("="*60)
    print("Testing contingency_analysis.py")
    print("="*60)
    
    # Use smaller network for faster testing
    net = pp.networks.case9()
    pp.runpp(net)
    
    print(f"Network: {len(net.bus)} buses, {len(net.line)} lines")
    
    # Run N-1 analysis
    results = run_n1_analysis(net, elements=['line'], verbose=False)
    print(f"✓ run_n1_analysis: Analyzed {len(results)} contingencies")
    
    # Generate report
    report = generate_contingency_report(results, output_file=None)
    print(f"✓ generate_contingency_report: Generated {len(report)} characters")
    
    # Check results structure
    assert 'contingency' in results.columns
    assert 'converged' in results.columns
    assert 'status' in results.columns
    print("✓ Results DataFrame has expected columns")
    
    print("\n✓ All contingency_analysis.py tests passed!\n")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PANDAPOWER SCRIPTS VALIDATION TEST")
    print("="*60 + "\n")
    
    try:
        # Test network_analysis
        test_network_analysis()
        
        # Test contingency_analysis
        test_contingency_analysis()
        
        print("="*60)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*60)
        print("\nAll scripts are working correctly!")
        print("You can now use:")
        print("  - python scripts/quick_check.py <network.json>")
        print("  - python scripts/contingency_analysis.py <network.json>")
        print("  - from scripts.network_analysis import *")
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
