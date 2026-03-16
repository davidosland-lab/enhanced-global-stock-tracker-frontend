#!/usr/bin/env python3
"""Verification script for Keras 3 Model Save Fix"""
import sys
from pathlib import Path

def main():
    print("="*80)
    print("KERAS 3 MODEL SAVE FIX - VERIFICATION")
    print("="*80)
    print()
    
    lstm_predictor = Path("finbert_v4.4.4/models/lstm_predictor.py")
    train_lstm = Path("finbert_v4.4.4/models/train_lstm.py")
    
    if not lstm_predictor.exists() or not train_lstm.exists():
        print("✗ Files not found! Run from C:\\Users\\david\\AATelS")
        return 1
    
    checks = 0
    # Check 1: Symbol parameter
    if "symbol: str = None" in lstm_predictor.read_text():
        print("✓ lstm_predictor.py has symbol parameter")
        checks += 1
    # Check 2: Symbol-specific paths
    if "symbol}_lstm_model.keras" in lstm_predictor.read_text():
        print("✓ lstm_predictor.py uses symbol-specific paths")
        checks += 1
    # Check 3: .keras format
    if ".keras" in lstm_predictor.read_text():
        print("✓ lstm_predictor.py uses .keras format")
        checks += 1
    # Check 4: train_lstm passes symbol
    if "symbol=symbol" in train_lstm.read_text():
        print("✓ train_lstm.py passes symbol parameter")
        checks += 1
    
    print()
    if checks == 4:
        print("✓ ALL CHECKS PASSED!")
        return 0
    else:
        print(f"✗ CHECKS FAILED: {checks}/4 passed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
