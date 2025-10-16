#!/usr/bin/env python3
"""
Verify that all backends are configured for the correct ports
"""

import os
import re

services = {
    'main_backend.py': 8000,
    'ml_backend.py': 8002,
    'finbert_backend.py': 8003,
    'historical_backend.py': 8004,
    'backtesting_backend.py': 8005
}

print("="*60)
print("Verifying Port Configurations")
print("="*60)
print()

all_correct = True

for filename, expected_port in services.items():
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
            
        # Look for port configuration
        port_match = re.search(r'port\s*=\s*(\d+)', content)
        if port_match:
            actual_port = int(port_match.group(1))
            if actual_port == expected_port:
                print(f"✓ {filename:<25} configured for port {expected_port} - CORRECT")
            else:
                print(f"✗ {filename:<25} configured for port {actual_port} - SHOULD BE {expected_port}")
                all_correct = False
        else:
            print(f"? {filename:<25} no port configuration found")
    else:
        print(f"✗ {filename:<25} FILE NOT FOUND")
        all_correct = False

print()
print("="*60)

if all_correct:
    print("✓ All services are configured for the correct ports!")
else:
    print("✗ Some services have incorrect port configurations")
    print("  Run QUICK_FIX.bat to fix the issues")

print("="*60)
print()
print("Correct port mapping:")
print("  Main Backend:    http://localhost:8000")
print("  ML Backend:      http://localhost:8002")  
print("  FinBERT:         http://localhost:8003")
print("  Historical:      http://localhost:8004")
print("  Backtesting:     http://localhost:8005")
print("="*60)