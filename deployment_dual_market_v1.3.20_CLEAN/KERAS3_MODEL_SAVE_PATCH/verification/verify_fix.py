#!/usr/bin/env python3
"""
Verification script for Keras 3 Model Save Fix
Checks if the patch was applied correctly
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath):
    """Check if file exists"""
    if not Path(filepath).exists():
        print(f"✗ File not found: {filepath}")
        return False
    return True

def check_line_in_file(filepath, search_text, description):
    """Check if a line exists in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - NOT FOUND")
                return False
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
        return False

def main():
    print("="*80)
    print("         KERAS 3 MODEL SAVE FIX - VERIFICATION")
    print("="*80)
    print()
    
    # Check current directory
    cwd = Path.cwd()
    print(f"Current directory: {cwd}")
    print()
    
    # Define file paths
    lstm_predictor = Path("finbert_v4.4.4/models/lstm_predictor.py")
    train_lstm = Path("finbert_v4.4.4/models/train_lstm.py")
    
    # Check files exist
    print("Checking files exist...")
    predictor_exists = check_file_exists(lstm_predictor)
    train_exists = check_file_exists(train_lstm)
    print()
    
    if not predictor_exists or not train_exists:
        print("✗ Required files not found!")
        print()
        print("Make sure you are running this from:")
        print("  C:\\Users\\david\\AATelS")
        print()
        print("And that finbert_v4.4.4\\models\\ directory exists.")
        return 1
    
    # Check patches applied
    print("Checking if patches are applied...")
    print()
    
    checks_passed = 0
    checks_total = 4
    
    # Check 1: Symbol parameter exists
    if check_line_in_file(lstm_predictor, "symbol: str = None", 
                          "lstm_predictor.py has symbol parameter"):
        checks_passed += 1
    
    # Check 2: Symbol-specific paths
    if check_line_in_file(lstm_predictor, "symbol}_lstm_model.keras",
                          "lstm_predictor.py uses symbol-specific paths"):
        checks_passed += 1
    
    # Check 3: Uses .keras format
    if check_line_in_file(lstm_predictor, ".keras",
                          "lstm_predictor.py uses .keras format"):
        checks_passed += 1
    
    # Check 4: train_lstm.py passes symbol
    if check_line_in_file(train_lstm, "symbol=symbol",
                          "train_lstm.py passes symbol parameter"):
        checks_passed += 1
    
    print()
    print("="*80)
    
    if checks_passed == checks_total:
        print("✓ ALL CHECKS PASSED!")
        print("="*80)
        print()
        print("The fix has been applied correctly!")
        print()
        print("NEXT STEPS:")
        print("  1. Test with one stock:")
        print("     python finbert_v4.4.4\\models\\train_lstm.py --symbol BHP.AX --epochs 5")
        print()
        print("  2. Check for output:")
        print("     'Model saved to models/BHP.AX_lstm_model.keras'")
        print()
        print("  3. Verify file exists:")
        print("     dir models\\BHP.AX_lstm_model.keras")
        print()
        print("  4. Run full pipeline:")
        print("     RUN_PIPELINE.bat")
        print()
        return 0
    else:
        print(f"✗ CHECKS FAILED: {checks_passed}/{checks_total} passed")
        print("="*80)
        print()
        print("The fix was not applied correctly!")
        print()
        print("TROUBLESHOOTING:")
        print("  1. Make sure you copied the files to the correct location:")
        print("     finbert_v4.4.4\\models\\lstm_predictor.py")
        print("     finbert_v4.4.4\\models\\train_lstm.py")
        print()
        print("  2. Clear Python cache:")
        print("     del /s /q finbert_v4.4.4\\__pycache__")
        print()
        print("  3. Try manual installation:")
        print("     See MANUAL_INSTALL.txt")
        print()
        print("  4. Re-download from GenSpark:")
        print("     deployment_dual_market_v1.3.20_CLEAN/finbert_v4.4.4/models/")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
