"""
Complete Diagnostic Script for Keras 3 Fix
Shows exactly what's wrong and how to fix it
"""

import sys
from pathlib import Path

print("\n" + "="*70)
print("COMPLETE DIAGNOSTIC - KERAS 3 FIX")
print("="*70)

# Check 1: Files exist?
print("\n[CHECK 1] Do the files exist?")
print("-" * 70)

lstm_file = Path("finbert_v4.4.4/models/lstm_predictor.py")
train_file = Path("finbert_v4.4.4/models/train_lstm.py")

if lstm_file.exists():
    print(f"✓ lstm_predictor.py exists ({lstm_file.stat().st_size:,} bytes)")
else:
    print("✗ lstm_predictor.py NOT FOUND!")
    print("\nYou need to download this file from GenSpark or GitHub")
    sys.exit(1)

if train_file.exists():
    print(f"✓ train_lstm.py exists ({train_file.stat().st_size:,} bytes)")
else:
    print("✗ train_lstm.py NOT FOUND!")
    sys.exit(1)

# Check 2: What version?
print("\n[CHECK 2] Which version do you have?")
print("-" * 70)

try:
    lstm_content = lstm_file.read_text(encoding='utf-8', errors='ignore')
except:
    lstm_content = lstm_file.read_text(encoding='latin-1', errors='ignore')

try:
    train_content = train_file.read_text(encoding='utf-8', errors='ignore')
except:
    train_content = train_file.read_text(encoding='latin-1', errors='ignore')

# Check lstm_predictor.py
print("\nA) lstm_predictor.py:")

has_symbol_param = "symbol: str = None" in lstm_content
if has_symbol_param:
    print("   ✓ Has 'symbol' parameter in __init__")
else:
    print("   ✗ MISSING 'symbol' parameter")
    print("   → OLD VERSION! Need to download new file")

has_symbol_path = "f'models/{symbol}_lstm_model.keras'" in lstm_content
if has_symbol_path:
    print("   ✓ Uses symbol-specific path")
else:
    print("   ✗ Uses generic path")
    print("   → OLD VERSION! Need to download new file")

has_clean_save = ("self.model.save(self.model_path)" in lstm_content and 
                  "save_format=" not in lstm_content.split("def save_model")[1].split("def load_model")[0])
if has_clean_save:
    print("   ✓ Uses clean save (no save_format)")
else:
    print("   ✗ Still uses save_format parameter")

# Check train_lstm.py
print("\nB) train_lstm.py:")

passes_symbol = "symbol=symbol" in train_content and "StockLSTMPredictor" in train_content
if passes_symbol:
    print("   ✓ Passes symbol to predictor")
else:
    print("   ✗ Does NOT pass symbol to predictor")
    print("   → OLD VERSION! Need to download new file")

# Check 3: What's in __init__?
print("\n[CHECK 3] Examining __init__ method...")
print("-" * 70)

import re
init_match = re.search(r'def __init__\(self,.*?\):', lstm_content, re.DOTALL)
if init_match:
    init_signature = init_match.group(0)
    print(f"\nCurrent signature:\n{init_signature}")
    
    if "symbol" in init_signature:
        print("\n✓ Signature includes 'symbol' parameter")
    else:
        print("\n✗ Signature MISSING 'symbol' parameter")
        print("\nExpected signature:")
        print("def __init__(self, sequence_length: int = 60, features: List[str] = None, symbol: str = None):")

# Check 4: What's the model_path line?
print("\n[CHECK 4] Examining model_path assignment...")
print("-" * 70)

model_path_lines = [line for line in lstm_content.split('\n') if 'self.model_path' in line and '=' in line]
if model_path_lines:
    print("\nFound model_path assignments:")
    for i, line in enumerate(model_path_lines[:5], 1):
        print(f"  {i}. {line.strip()}")
    
    if any("f'models/{symbol}" in line for line in model_path_lines):
        print("\n✓ Uses f-string with symbol")
    elif any("{symbol}" in line for line in model_path_lines):
        print("\n✓ Uses formatting with symbol")
    else:
        print("\n✗ Uses hardcoded path (no symbol)")
        print("\nExpected:")
        print("  self.model_path = f'models/{symbol}_lstm_model.keras'")

# Summary
print("\n" + "="*70)
print("DIAGNOSTIC SUMMARY")
print("="*70)

issues = []
if not has_symbol_param:
    issues.append("lstm_predictor.py missing 'symbol' parameter")
if not has_symbol_path:
    issues.append("lstm_predictor.py using generic path")
if not passes_symbol:
    issues.append("train_lstm.py not passing symbol")

if issues:
    print("\n✗ ISSUES FOUND:")
    for issue in issues:
        print(f"  • {issue}")
    
    print("\n" + "="*70)
    print("YOU NEED TO DOWNLOAD THE FIXED FILES")
    print("="*70)
    print("\nOPTION 1: Download from GenSpark")
    print("-" * 70)
    print("Navigate to: deployment_dual_market_v1.3.20_CLEAN/finbert_v4.4.4/models/")
    print("Download:")
    print("  • lstm_predictor.py")
    print("  • train_lstm.py")
    print("\nThen copy to: C:\\Users\\david\\AATelS\\finbert_v4.4.4\\models\\")
    
    print("\n\nOPTION 2: Download from GitHub")
    print("-" * 70)
    print("\nlstm_predictor.py:")
    print("https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/raw/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/finbert_v4.4.4/models/lstm_predictor.py")
    print("\ntrain_lstm.py:")
    print("https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/raw/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/finbert_v4.4.4/models/train_lstm.py")
    
    print("\n\nAFTER DOWNLOADING:")
    print("-" * 70)
    print("1. Backup current files:")
    print("   copy finbert_v4.4.4\\models\\lstm_predictor.py finbert_v4.4.4\\models\\lstm_predictor.py.backup")
    print("   copy finbert_v4.4.4\\models\\train_lstm.py finbert_v4.4.4\\models\\train_lstm.py.backup")
    print("\n2. Copy new files:")
    print("   copy Downloads\\lstm_predictor.py finbert_v4.4.4\\models\\")
    print("   copy Downloads\\train_lstm.py finbert_v4.4.4\\models\\")
    print("\n3. Run this diagnostic again:")
    print("   python DIAGNOSE_ISSUE.py")
    
    sys.exit(1)
else:
    print("\n✓ ALL CHECKS PASSED!")
    print("\nYou have the correct version of the files.")
    print("\nTest command:")
    print("  python finbert_v4.4.4\\models\\train_lstm.py --symbol BHP.AX --epochs 5")
    print("\nExpected output:")
    print("  Model saved to models/BHP.AX_lstm_model.keras")
    print("\nVerify:")
    print("  dir models\\BHP.AX_lstm_model.keras")
    
    sys.exit(0)
