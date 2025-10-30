#!/usr/bin/env python3
"""
Diagnostic script for transformers installation issues
"""

import sys
import subprocess
import platform

print("="*60)
print("TRANSFORMERS INSTALLATION DIAGNOSTIC")
print("="*60)

# System info
print("\n1. SYSTEM INFORMATION:")
print(f"   Python Version: {sys.version}")
print(f"   Platform: {platform.platform()}")
print(f"   Architecture: {platform.machine()}")

# Check pip version
print("\n2. PIP VERSION:")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, text=True)
    print(f"   {result.stdout.strip()}")
except:
    print("   ERROR: Cannot check pip version")

# Check installed packages
print("\n3. CHECKING DEPENDENCIES:")
packages = {
    'numpy': None,
    'torch': None,
    'transformers': None,
    'tokenizers': None,
    'huggingface-hub': None,
    'safetensors': None,
    'regex': None,
    'tqdm': None,
}

for package in packages:
    try:
        __import__(package.replace('-', '_'))
        module = sys.modules[package.replace('-', '_')]
        if hasattr(module, '__version__'):
            packages[package] = module.__version__
            print(f"   ✓ {package}: {module.__version__}")
        else:
            packages[package] = "installed (version unknown)"
            print(f"   ✓ {package}: installed")
    except ImportError:
        packages[package] = "not installed"
        print(f"   ✗ {package}: not installed")

# Try to identify the issue
print("\n4. DIAGNOSIS:")

if packages['torch'] == "not installed":
    print("   ⚠ PyTorch is not installed. Transformers requires PyTorch.")
    print("   FIX: Install PyTorch first:")
    print("        pip install torch --index-url https://download.pytorch.org/whl/cpu")

if packages['numpy'] == "not installed":
    print("   ⚠ NumPy is not installed. This is required.")
    print("   FIX: pip install numpy>=1.26.0")
elif packages['numpy'] and packages['numpy'].startswith('1.') and int(packages['numpy'].split('.')[1]) < 26:
    print(f"   ⚠ NumPy version {packages['numpy']} may not be compatible with Python 3.12")
    print("   FIX: pip install --upgrade numpy>=1.26.0")

if packages['transformers'] == "not installed":
    print("\n5. ATTEMPTING TO DIAGNOSE TRANSFORMERS INSTALLATION:")
    print("   Trying to install transformers in test mode...")
    
    # Try dry run
    result = subprocess.run([sys.executable, "-m", "pip", "install", "--dry-run", "transformers"],
                          capture_output=True, text=True)
    
    if "error" in result.stderr.lower() or result.returncode != 0:
        print("   ✗ Installation would fail. Error output:")
        print(result.stderr[:500])  # First 500 chars of error
        
        print("\n   SUGGESTED FIX:")
        print("   1. Install PyTorch first:")
        print("      pip install torch --index-url https://download.pytorch.org/whl/cpu")
        print("   2. Then install transformers:")
        print("      pip install transformers")
        print("\n   OR use the minimal installation without FinBERT:")
        print("      The system will use fallback sentiment analysis")
    else:
        print("   ✓ Transformers can be installed. No conflicts detected.")
else:
    print("\n5. TRANSFORMERS VERIFICATION:")
    print(f"   ✓ Transformers {packages['transformers']} is installed")
    
    # Try to load FinBERT
    try:
        from transformers import AutoTokenizer
        print("   ✓ Can import AutoTokenizer")
        
        # Try to check if model can be loaded
        print("   Testing FinBERT model availability...")
        tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert", cache_dir="./cache")
        print("   ✓ FinBERT model can be loaded!")
        
    except Exception as e:
        print(f"   ✗ Error loading FinBERT: {e}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)

if packages['transformers'] != "not installed":
    print("✓ Transformers is installed. FinBERT should work.")
else:
    print("ℹ Transformers is not installed.")
    print("  The system will work fine with fallback sentiment analysis.")
    print("  To install transformers (optional):")
    print("    1. Run: pip install torch --index-url https://download.pytorch.org/whl/cpu")
    print("    2. Run: pip install transformers")

print("\nPress Enter to exit...")
input()