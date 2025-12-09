#!/usr/bin/env python3
"""
Bug Fix Patch v1.1 - Windows Compatible
Fixes for FinBERT v4.4.4 app_finbert_v4_dev.py
NO UNICODE - works on Windows CMD
"""

import os
import sys
import re
import shutil
from datetime import datetime

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def backup_file(file_path):
    """Create timestamped backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"[OK] Backup created: {backup_path}")
    return backup_path

def find_app_file(base_path):
    """Find the app file"""
    app_file = os.path.join(base_path, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
    if os.path.exists(app_file):
        return app_file
    return None

def apply_fix_1_remove_mock_sentiment(content):
    """Remove get_mock_sentiment fallback"""
    print("Applying FIX 1: Remove mock sentiment fallback...")
    
    pattern1 = r"sentiment_result\s*=\s*finbert_analyzer\.get_mock_sentiment\([^)]+\)"
    replacement1 = """sentiment_result = None  # No fake data
                logger.warning(f"Sentiment unavailable for {symbol}")"""
    
    content = re.sub(pattern1, replacement1, content)
    print("  [OK] Mock sentiment fallback removed")
    return content

def apply_fix_2_adx_validation(content):
    """Add ADX calculation validation"""
    print("Applying FIX 2: Add ADX validation...")
    
    pattern = r"(adx\s*=\s*calculate_adx\([^)]+\))"
    
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            """try:
        if len(df) >= 14:
            \\1
        else:
            adx = None
            logger.info(f"Insufficient data for ADX (need 14, have {len(df)})")
    except Exception as e:
        adx = None
        logger.warning(f"ADX calculation error: {e}")""",
            content
        )
        print("  [OK] ADX validation added")
    else:
        print("  [INFO] No ADX calculation found")
    
    return content

def apply_fix_3_sentiment_none_handling(content):
    """Add proper None handling for sentiment results"""
    print("Applying FIX 3: Add sentiment None handling...")
    
    pattern1 = r"sentiment_result\[(['\"])([^'\"]+)\1\]"
    
    def safe_access(match):
        key = match.group(2)
        return f"(sentiment_result.get('{key}') if sentiment_result else None)"
    
    new_content = re.sub(pattern1, safe_access, content)
    if new_content != content:
        print("  [OK] Sentiment None checks added")
        content = new_content
    else:
        print("  [INFO] Sentiment already properly handled")
    
    return content

def add_patch_marker(content):
    """Add marker to show patch was applied"""
    marker = """
# ========================================
# BUG FIX PATCH v1.1 APPLIED
# Date: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
# NO FAKE/MOCK/SYNTHETIC DATA
# ========================================

"""
    
    import_end = content.find('\n\n', content.find('import'))
    if import_end > 0:
        content = content[:import_end] + '\n' + marker + content[import_end:]
    
    return content

def main():
    print("=" * 60)
    print("Bug Fix Patch v1.1 - Automatic Fixer")
    print("NO MOCK/FAKE/SYNTHETIC DATA")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter FinBERT path: ").strip()
    
    app_file = find_app_file(base_path)
    if not app_file:
        print(f"[ERROR] Could not find app_finbert_v4_dev.py in {base_path}")
        return 1
    
    print(f"[OK] Found app file: {app_file}")
    print()
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    backup_path = backup_file(app_file)
    print()
    
    print("Applying fixes...")
    print("-" * 60)
    
    content = apply_fix_1_remove_mock_sentiment(content)
    content = apply_fix_2_adx_validation(content)
    content = apply_fix_3_sentiment_none_handling(content)
    content = add_patch_marker(content)
    
    print("-" * 60)
    print()
    
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] Fixes applied successfully")
    print()
    print("=" * 60)
    print("Patch Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart FinBERT server")
    print(f"2. Backup at: {backup_path}")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[CANCELLED]")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
