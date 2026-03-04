#!/usr/bin/env python3
"""
COMPREHENSIVE FIX VERIFICATION SCRIPT
v1.3.15.87 - Verify all fixes are applied correctly
"""

import os
import sys

def check_file_content(filepath, search_text, should_contain=True, description=""):
    """Check if a file contains specific text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            contains = search_text in content
            
            if should_contain and contains:
                print(f"[OK] {description}")
                return True
            elif not should_contain and not contains:
                print(f"[OK] {description}")
                return True
            else:
                print(f"✗ {description}")
                print(f"  File: {filepath}")
                if should_contain:
                    print(f"  Missing: {search_text}")
                else:
                    print(f"  Found (should not exist): {search_text}")
                return False
    except Exception as e:
        print(f"✗ {description}")
        print(f"  Error: {e}")
        return False

def main():
    print("="*80)
    print("COMPREHENSIVE FIX VERIFICATION")
    print("v1.3.15.87 - Unified Trading Dashboard")
    print("="*80)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    finbert_dir = os.path.join(base_dir, 'finbert_v4.4.4')
    models_dir = os.path.join(finbert_dir, 'models')
    
    all_passed = True
    
    # Test 1: Pandas 2.x fix
    print("1. PANDAS 2.X FIX")
    train_lstm_path = os.path.join(models_dir, 'train_lstm.py')
    all_passed &= check_file_content(
        train_lstm_path,
        '.ffill().fillna(0)',
        True,
        "Pandas 2.x compatible ffill() method"
    )
    all_passed &= check_file_content(
        train_lstm_path,
        "fillna(method='ffill')",
        False,
        "Old fillna(method=) removed"
    )
    print()
    
    # Test 2: PyTorch tensor fix
    print("2. PYTORCH TENSOR FIX")
    finbert_sent_path = os.path.join(models_dir, 'finbert_sentiment.py')
    all_passed &= check_file_content(
        finbert_sent_path,
        '.detach().cpu().numpy()',
        True,
        "PyTorch tensor detach() before numpy()"
    )
    all_passed &= check_file_content(
        finbert_sent_path,
        'predictions[0].cpu().numpy()',  # Without detach
        False,
        "Old .cpu().numpy() removed"
    )
    print()
    
    # Test 3: FinBERT disabled during training
    print("3. FINBERT IMPORT DISABLED DURING TRAINING")
    lstm_pred_path = os.path.join(models_dir, 'lstm_predictor.py')
    all_passed &= check_file_content(
        lstm_pred_path,
        '# from finbert_sentiment import',
        True,
        "FinBERT import commented out"
    )
    all_passed &= check_file_content(
        lstm_pred_path,
        'FINBERT_AVAILABLE = False',
        True,
        "FINBERT_AVAILABLE set to False"
    )
    print()
    
    # Test 4: Enhanced error logging
    print("4. ENHANCED ERROR LOGGING")
    all_passed &= check_file_content(
        train_lstm_path,
        'import traceback',
        True,
        "Traceback module imported"
    )
    all_passed &= check_file_content(
        train_lstm_path,
        'traceback.format_exc()',
        True,
        "Full traceback logging enabled"
    )
    print()
    
    # Test 5: Check for any remaining PyTorch imports
    print("5. NO PYTORCH IMPORTS IN TRAINING PATH")
    for filename in ['train_lstm.py', 'lstm_predictor.py']:
        filepath = os.path.join(models_dir, filename)
        all_passed &= check_file_content(
            filepath,
            'import torch',
            False,
            f"No 'import torch' in {filename}"
        )
        all_passed &= check_file_content(
            filepath,
            'from torch',
            False,
            f"No 'from torch' in {filename}"
        )
    print()
    
    # Summary
    print("="*80)
    if all_passed:
        print("[OK] ALL FIXES VERIFIED - PACKAGE IS CORRECT")
        print()
        print("NEXT STEPS:")
        print("1. Extract this package to a CLEAN directory")
        print("2. Delete any old installations")
        print("3. Run INSTALL.bat")
        print("4. Start Flask with: set FLASK_SKIP_DOTENV=1 && python app_finbert_v4_dev.py")
        print("5. Test training: curl -X POST http://localhost:5001/api/train/AAPL ...")
        sys.exit(0)
    else:
        print("✗ SOME FIXES MISSING - PACKAGE NEEDS UPDATE")
        print()
        print("This package may not be the latest version.")
        print("Please download the updated package again.")
        sys.exit(1)

if __name__ == '__main__':
    main()
