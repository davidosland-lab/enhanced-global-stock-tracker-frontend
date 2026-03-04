#!/usr/bin/env python3
"""
FIXED VERSION: PyTorch/TensorFlow Conflict Fix

This version properly handles the try/except block removal.
"""

import os
import sys
import re

def fix_pytorch_tensorflow_conflict():
    """
    Fix the PyTorch/TensorFlow conflict by lazy-loading FinBERT
    """
    
    app_file = "finbert_v4.4.4/app_finbert_v4_dev.py"
    
    if not os.path.exists(app_file):
        print(f"❌ ERROR: {app_file} not found")
        print(f"   Current directory: {os.getcwd()}")
        return False
    
    print(f"🔧 Fixing PyTorch/TensorFlow conflict in {app_file}...")
    
    # Read the file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_file = f"{app_file}.backup_pytorch_fix_v2"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Backup created: {backup_file}")
    
    # Check if already fixed
    if "_load_finbert_if_needed" in content:
        # Check for syntax error (orphaned try block)
        if re.search(r'_finbert_loaded = True.*?\n\ntry:\s*\n\s*logger\.info.*?FinBERT.*?loaded', content, re.DOTALL):
            print("⚠️  Found orphaned try block from previous fix - cleaning up...")
            
            # Remove the orphaned try block
            content = re.sub(
                r'(_finbert_loaded = True.*?\n\n)try:\s*\n\s*logger\.info\("[OK] REAL FinBERT.*?"\).*?\n\s*print\(f"Note: FinBERT.*?"\).*?\n\n',
                r'\1',
                content,
                flags=re.DOTALL
            )
            
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[OK] Cleaned up orphaned try block")
            print()
            print("="*70)
            print("[OK] SYNTAX ERROR FIXED!")
            print("="*70)
            return True
        else:
            print("[OK] Fix already applied and correct")
            return True
    
    # Find the old import section
    pattern = r'# Import FinBERT sentiment analyzer.*?FINBERT_AVAILABLE = False.*?finbert_analyzer = None.*?real_sentiment_module = None.*?try:.*?from models\.finbert_sentiment.*?from models\.news_sentiment_real.*?FINBERT_AVAILABLE = True.*?real_sentiment_module = True.*?logger\.info\("[OK] REAL FinBERT.*?"\).*?except.*?print\(f"Note: FinBERT.*?"\)'
    
    if not re.search(pattern, content, re.DOTALL):
        print("❌ ERROR: Could not find expected import pattern")
        print("   The file may have been modified")
        return False
    
    # Replace with lazy-load version
    new_section = '''# Import FinBERT sentiment analyzer with REAL news scraping (must be after other imports)

# LAZY-LOAD FinBERT to avoid PyTorch/TensorFlow conflicts during LSTM training
FINBERT_AVAILABLE = False
finbert_analyzer = None
real_sentiment_module = None
_finbert_loaded = False

def _load_finbert_if_needed():
    """
    Lazy-load FinBERT only when needed for sentiment analysis.
    This prevents PyTorch from interfering with TensorFlow LSTM training.
    """
    global FINBERT_AVAILABLE, finbert_analyzer, real_sentiment_module, _finbert_loaded
    
    if _finbert_loaded:
        return
    
    try:
        from models.finbert_sentiment import finbert_analyzer as fa, get_sentiment_analysis, get_batch_sentiment
        from models.news_sentiment_real import get_sentiment_sync, get_real_sentiment_for_symbol
        finbert_analyzer = fa
        FINBERT_AVAILABLE = True
        real_sentiment_module = True
        _finbert_loaded = True
        logger.info("[OK] FinBERT lazy-loaded for sentiment analysis")
    except (ImportError, ValueError, Exception) as e:
        logger.warning(f"FinBERT not available: {e}")
        FINBERT_AVAILABLE = False
        _finbert_loaded = True  # Mark as attempted'''
    
    content = re.sub(pattern, new_section, content, flags=re.DOTALL)
    
    # Write the fixed file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] Fixed: Converted to lazy-loading")
    
    # Add lazy-load calls to routes
    add_lazy_load_calls(content, app_file)
    
    print()
    print("="*70)
    print("[OK] FIX APPLIED SUCCESSFULLY!")
    print("="*70)
    print()
    print("WHAT WAS FIXED:")
    print("  • Changed FinBERT import from eager to lazy-loading")
    print("  • PyTorch now loads only when sentiment analysis is needed")
    print("  • LSTM training no longer conflicts with PyTorch")
    print()
    
    return True

def add_lazy_load_calls(content, app_file):
    """
    Add _load_finbert_if_needed() calls to sentiment routes
    """
    
    print("🔧 Adding lazy-load calls to sentiment routes...")
    
    modified = False
    
    # Sentiment route
    if "@app.route('/api/sentiment/<path:symbol>')" in content:
        if "_load_finbert_if_needed()" not in content[content.find("@app.route('/api/sentiment"):content.find("@app.route('/api/sentiment")+300]:
            content = content.replace(
                "@app.route('/api/sentiment/<path:symbol>')\ndef get_sentiment(symbol):\n    \"\"\"Get sentiment analysis for a stock symbol\"\"\"\n    try:",
                "@app.route('/api/sentiment/<path:symbol>')\ndef get_sentiment(symbol):\n    \"\"\"Get sentiment analysis for a stock symbol\"\"\"\n    _load_finbert_if_needed()  # Lazy-load FinBERT when needed\n    try:"
            )
            modified = True
            print("  [OK] Added lazy-load to sentiment route")
    
    # Stock route
    if "@app.route('/api/stock/<path:symbol>')" in content:
        if "_load_finbert_if_needed()" not in content[content.find("@app.route('/api/stock"):content.find("@app.route('/api/stock")+300]:
            content = content.replace(
                "@app.route('/api/stock/<path:symbol>')\ndef get_stock_data(symbol):\n    \"\"\"Get stock data with v4.0 ML predictions\"\"\"\n    try:",
                "@app.route('/api/stock/<path:symbol>')\ndef get_stock_data(symbol):\n    \"\"\"Get stock data with v4.0 ML predictions\"\"\"\n    _load_finbert_if_needed()  # Lazy-load FinBERT when needed\n    try:"
            )
            modified = True
            print("  [OK] Added lazy-load to stock route")
    
    if modified:
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] Lazy-load calls added")
    else:
        print("  → Already added or routes not found")

if __name__ == "__main__":
    print()
    print("="*70)
    print("  PYTORCH/TENSORFLOW CONFLICT FIX - CORRECTED VERSION")
    print("="*70)
    print()
    print("This will fix:")
    print("  1. RuntimeError during LSTM training")
    print("  2. SyntaxError from previous fix attempt")
    print()
    
    input("Press ENTER to continue or CTRL+C to cancel...")
    print()
    
    # Apply main fix
    if not fix_pytorch_tensorflow_conflict():
        sys.exit(1)
    
    print()
    print("="*70)
    print("[OK] ALL FIXES APPLIED!")
    print("="*70)
    print()
    print("RESTART FLASK SERVER:")
    print("  1. Stop Flask (CTRL+C if running)")
    print("  2. cd finbert_v4.4.4")
    print("  3. set FLASK_SKIP_DOTENV=1")
    print("  4. python app_finbert_v4_dev.py")
    print()
    print("TEST LSTM TRAINING:")
    print('  curl -X POST http://localhost:5001/api/train/AAPL \\')
    print('       -H "Content-Type: application/json" \\')
    print('       -d "{\\"epochs\\": 20}"')
    print()
    print("EXPECTED: Training succeeds without errors!")
    print()
