"""
Path Setup for Dual Market Screening System

This module ensures all imports work correctly from the installation directory.
Import this at the beginning of any script that needs to use the screening modules.
"""

import sys
from pathlib import Path

# Get the installation directory (where this file is located)
INSTALL_DIR = Path(__file__).parent.resolve()

# Add to Python path if not already there
paths_to_add = [
    str(INSTALL_DIR),  # Root directory
    str(INSTALL_DIR / 'models'),  # Models directory
    str(INSTALL_DIR / 'models' / 'screening'),  # Screening modules
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Print confirmation (comment out in production)
if __name__ == "__main__":
    print("="*80)
    print("DUAL MARKET SCREENING - PATH SETUP")
    print("="*80)
    print(f"Installation Directory: {INSTALL_DIR}")
    print(f"\nPython Path Updated:")
    for i, path in enumerate(paths_to_add, 1):
        print(f"  {i}. {path}")
    print("="*80)
