#!/usr/bin/env python3
"""
FIX: PyTorch/TensorFlow Conflict During LSTM Training

PROBLEM:
    RuntimeError: Can't call numpy() on Tensor that requires grad

ROOT CAUSE:
    - app_finbert_v4_dev.py imports finbert_sentiment at startup (line 41)
    - This loads PyTorch into memory
    - When TensorFlow LSTM training starts, PyTorch interferes
    - Result: Tensor conversion fails during training

SOLUTION:
    Lazy-load FinBERT only when needed for sentiment analysis,
    not at Flask startup
"""

import os
import sys

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
        lines = f.readlines()
    
    # Create backup
    backup_file = f"{app_file}.backup_pytorch_fix"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"[OK] Backup created: {backup_file}")
    
    # Find and replace the import section
    new_lines = []
    in_import_section = False
    replaced = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Detect start of FinBERT import section
        if "# Import FinBERT sentiment analyzer" in line:
            in_import_section = True
            # Replace the entire import section
            new_lines.append(line)
            new_lines.append("\n")
            new_lines.append("# LAZY-LOAD FinBERT to avoid PyTorch/TensorFlow conflicts during LSTM training\n")
            new_lines.append("FINBERT_AVAILABLE = False\n")
            new_lines.append("finbert_analyzer = None\n")
            new_lines.append("real_sentiment_module = None\n")
            new_lines.append("_finbert_loaded = False\n")
            new_lines.append("\n")
            new_lines.append("def _load_finbert_if_needed():\n")
            new_lines.append("    \"\"\"\n")
            new_lines.append("    Lazy-load FinBERT only when needed for sentiment analysis.\n")
            new_lines.append("    This prevents PyTorch from interfering with TensorFlow LSTM training.\n")
            new_lines.append("    \"\"\"\n")
            new_lines.append("    global FINBERT_AVAILABLE, finbert_analyzer, real_sentiment_module, _finbert_loaded\n")
            new_lines.append("    \n")
            new_lines.append("    if _finbert_loaded:\n")
            new_lines.append("        return\n")
            new_lines.append("    \n")
            new_lines.append("    try:\n")
            new_lines.append("        from models.finbert_sentiment import finbert_analyzer as fa, get_sentiment_analysis, get_batch_sentiment\n")
            new_lines.append("        from models.news_sentiment_real import get_sentiment_sync, get_real_sentiment_for_symbol\n")
            new_lines.append("        finbert_analyzer = fa\n")
            new_lines.append("        FINBERT_AVAILABLE = True\n")
            new_lines.append("        real_sentiment_module = True\n")
            new_lines.append("        _finbert_loaded = True\n")
            new_lines.append("        logger.info(\"[OK] FinBERT lazy-loaded for sentiment analysis\")\n")
            new_lines.append("    except (ImportError, ValueError, Exception) as e:\n")
            new_lines.append("        logger.warning(f\"FinBERT not available: {e}\")\n")
            new_lines.append("        FINBERT_AVAILABLE = False\n")
            new_lines.append("        _finbert_loaded = True  # Mark as attempted\n")
            new_lines.append("\n")
            replaced = True
            continue
        
        # Skip old import lines
        if in_import_section:
            if line.strip().startswith("from models.finbert_sentiment") or \
               line.strip().startswith("from models.news_sentiment_real") or \
               line.strip().startswith("FINBERT_AVAILABLE =") or \
               line.strip().startswith("finbert_analyzer =") or \
               line.strip().startswith("real_sentiment_module =") or \
               ("FinBERT" in line and "try:" in lines[i-1] if i > 0 else False) or \
               ("except" in line and in_import_section and i < len(lines) - 1):
                continue
            elif line.strip() == "" and i + 1 < len(lines) and "Suppress warnings" in lines[i+1]:
                in_import_section = False
        
        new_lines.append(line)
    
    if not replaced:
        print("❌ ERROR: Could not find FinBERT import section to replace")
        return False
    
    # Write the fixed file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"[OK] Fixed: Converted to lazy-loading")
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
    print("NEXT STEPS:")
    print("  1. Now you need to add _load_finbert_if_needed() calls")
    print("  2. Add it to sentiment endpoints before using finbert_analyzer")
    print()
    print("  Example locations to add:")
    print("    • /api/sentiment/<symbol> route")
    print("    • /api/stock/<symbol> route (if it uses sentiment)")
    print("    • Any route that calls finbert_analyzer methods")
    print()
    print("  Add this line at the start of each sentiment route:")
    print("    _load_finbert_if_needed()")
    print()
    
    return True

def add_lazy_load_calls():
    """
    Add _load_finbert_if_needed() calls to sentiment routes
    """
    
    app_file = "finbert_v4.4.4/app_finbert_v4_dev.py"
    
    print("🔧 Adding lazy-load calls to sentiment routes...")
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find sentiment route and add lazy load call
    replacements = [
        # Sentiment route
        (
            "@app.route('/api/sentiment/<path:symbol>', methods=['GET'])\ndef get_sentiment(symbol):",
            "@app.route('/api/sentiment/<path:symbol>', methods=['GET'])\ndef get_sentiment(symbol):\n    _load_finbert_if_needed()  # Lazy-load FinBERT when needed"
        ),
        # Stock route (if it exists)
        (
            "@app.route('/api/stock/<path:symbol>', methods=['GET'])\ndef get_stock_data(symbol):",
            "@app.route('/api/stock/<path:symbol>', methods=['GET'])\ndef get_stock_data(symbol):\n    _load_finbert_if_needed()  # Lazy-load FinBERT when needed"
        ),
    ]
    
    modified = False
    for old, new in replacements:
        if old in content and "_load_finbert_if_needed()" not in content[content.find(old):content.find(old)+200]:
            content = content.replace(old, new)
            modified = True
            print(f"  [OK] Added lazy-load to route: {old.split('def ')[1].split('(')[0]}")
    
    if modified:
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] Lazy-load calls added")
    else:
        print("  → No changes needed (already added or routes not found)")
    
    return True

if __name__ == "__main__":
    print()
    print("="*70)
    print("  PYTORCH/TENSORFLOW CONFLICT FIX")
    print("="*70)
    print()
    print("This will fix the RuntimeError during LSTM training by:")
    print("  1. Converting FinBERT import to lazy-loading")
    print("  2. Adding lazy-load calls to sentiment routes")
    print()
    
    input("Press ENTER to continue or CTRL+C to cancel...")
    print()
    
    # Apply main fix
    if not fix_pytorch_tensorflow_conflict():
        sys.exit(1)
    
    # Add lazy load calls
    add_lazy_load_calls()
    
    print()
    print("="*70)
    print("[OK] ALL FIXES APPLIED!")
    print("="*70)
    print()
    print("RESTART FLASK SERVER:")
    print("  1. Stop Flask (CTRL+C)")
    print("  2. cd finbert_v4.4.4")
    print("  3. set FLASK_SKIP_DOTENV=1")
    print("  4. python app_finbert_v4_dev.py")
    print()
    print("TEST LSTM TRAINING:")
    print('  curl -X POST http://localhost:5001/api/train/AAPL \\')
    print('       -H "Content-Type: application/json" \\')
    print('       -d "{\\"epochs\\": 20}"')
    print()
    print("EXPECTED: Training succeeds without RuntimeError!")
    print()
