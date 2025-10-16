#!/usr/bin/env python3
"""
Fix ML Backend Port - Changes port from 8004 to 8003
"""

import os

def fix_ml_backend_port():
    """Fix the ML backend to run on port 8003 instead of 8004"""
    
    ml_backend_file = "backend_ml_enhanced.py"
    
    if not os.path.exists(ml_backend_file):
        print(f"ERROR: {ml_backend_file} not found!")
        return False
    
    # Read the file
    with open(ml_backend_file, 'r') as f:
        content = f.read()
    
    # Replace port 8004 with 8003
    content = content.replace('port=8004', 'port=8003')
    content = content.replace('port 8004', 'port 8003')
    
    # Write back
    with open(ml_backend_file, 'w') as f:
        f.write(content)
    
    print(f"✓ Fixed ML Backend to run on port 8003")
    return True

if __name__ == "__main__":
    fix_ml_backend_port()