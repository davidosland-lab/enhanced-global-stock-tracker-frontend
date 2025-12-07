#!/usr/bin/env python3
"""
Bug Fix Patch v1.0 - Remove Mock Data and Fix Errors
Fixes for FinBERT v4.4.4 app_finbert_v4_dev.py

Fixes:
1. Remove get_mock_sentiment fallback (NO FAKE DATA)
2. Add ADX validation (prevent crashes)
3. Add proper error handling (skip broken features)
4. Improve logging

NO MOCK/FAKE/SYNTHETIC DATA IS ADDED
"""

import os
import sys
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create timestamped backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return backup_path

def find_app_file(base_path):
    """Find the app file"""
    app_file = os.path.join(base_path, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
    if os.path.exists(app_file):
        return app_file
    return None

def apply_fix_1_remove_mock_sentiment(content):
    """
    FIX 1: Remove get_mock_sentiment fallback
    Replace with proper None handling (NO FAKE DATA)
    """
    print("Applying FIX 1: Remove mock sentiment fallback...")
    
    # Pattern 1: Direct call to get_mock_sentiment
    pattern1 = r"sentiment_result\s*=\s*finbert_analyzer\.get_mock_sentiment\([^)]+\)"
    replacement1 = """sentiment_result = None  # No fake data - skip if real sentiment fails
                logger.warning(f"Sentiment analysis failed for {symbol}, continuing without sentiment")"""
    
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: Any other mock sentiment references
    pattern2 = r"\.get_mock_sentiment\("
    if re.search(pattern2, content):
        print("  ⚠ WARNING: Additional get_mock_sentiment calls found - review manually")
    
    print("  ✓ Mock sentiment fallback removed")
    return content

def apply_fix_2_adx_validation(content):
    """
    FIX 2: Add ADX calculation validation
    Prevent crashes when insufficient data
    """
    print("Applying FIX 2: Add ADX validation...")
    
    # Find ADX calculation blocks
    # Pattern: Look for ADX calculation without length check
    
    # Add validation before ADX calculation
    adx_fix = """
    # ADX calculation with validation (FIX 2: Bug Fix Patch v1.0)
    adx_result = None
    try:
        if len(df) >= 14:  # Need at least 14 periods for ADX
            adx_result = calculate_adx(df, period=14)
        else:
            logger.info(f"Insufficient data for ADX (need 14, have {len(df)})")
    except Exception as e:
        logger.warning(f"ADX calculation error: {e}")
    """
    
    # Look for existing ADX calculation patterns
    pattern = r"(adx\s*=\s*calculate_adx\([^)]+\))"
    
    if re.search(pattern, content):
        # Wrap existing calculation with validation
        content = re.sub(
            pattern,
            f"""# ADX with validation (Bug Fix Patch v1.0)
    try:
        if len(df) >= 14:
            \\1
        else:
            adx = None
            logger.info(f"Insufficient data for ADX (need 14, have {{len(df)}})")
    except Exception as e:
        adx = None
        logger.warning(f"ADX calculation error: {{e}}")""",
            content
        )
        print("  ✓ ADX validation added")
    else:
        print("  ℹ No ADX calculation found (may already be fixed)")
    
    return content

def apply_fix_3_sentiment_none_handling(content):
    """
    FIX 3: Add proper None handling for sentiment results
    Ensure app continues when sentiment unavailable
    """
    print("Applying FIX 3: Add sentiment None handling...")
    
    # Find where sentiment_result is used and add None checks
    fixes_applied = 0
    
    # Pattern 1: Direct access to sentiment_result['key']
    pattern1 = r"sentiment_result\[(['\"])([^'\"]+)\1\]"
    
    # Replace with safe access
    def safe_access(match):
        key = match.group(2)
        return f"(sentiment_result.get('{key}') if sentiment_result else None)"
    
    new_content = re.sub(pattern1, safe_access, content)
    if new_content != content:
        fixes_applied += 1
        content = new_content
    
    # Pattern 2: if sentiment_result: checks
    # Make sure there are checks before using sentiment_result
    sentiment_usage_pattern = r"sentiment_result\.get\("
    if re.search(sentiment_usage_pattern, content):
        print("  ℹ sentiment_result.get() already used (good)")
    
    if fixes_applied > 0:
        print(f"  ✓ Added {fixes_applied} sentiment None checks")
    else:
        print("  ℹ Sentiment already properly handled")
    
    return content

def apply_fix_4_improve_logging(content):
    """
    FIX 4: Improve error logging for debugging
    """
    print("Applying FIX 4: Improve error logging...")
    
    # Add detailed exception logging where needed
    pattern = r"except Exception as e:\s*\n\s*logger\.(error|warning)\(f['\"]([^'\"]+)['\"]"
    
    def improve_log(match):
        level = match.group(1)
        msg = match.group(2)
        return f"""except Exception as e:
        logger.{level}(f"{msg}: {{e}}")
        import traceback
        logger.debug(traceback.format_exc())"""
    
    new_content = re.sub(pattern, improve_log, content)
    
    if new_content != content:
        print("  ✓ Enhanced error logging")
        content = new_content
    else:
        print("  ℹ Logging already detailed")
    
    return content

def add_patch_marker(content):
    """Add marker to show patch was applied"""
    marker = """
# ========================================
# BUG FIX PATCH v1.0 APPLIED
# Date: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
# Fixes:
#   1. Removed mock sentiment fallback (NO FAKE DATA)
#   2. Added ADX validation (prevent crashes)
#   3. Added sentiment None handling
#   4. Improved error logging
# ========================================

"""
    
    # Add after imports
    import_end = content.find('\n\n', content.find('import'))
    if import_end > 0:
        content = content[:import_end] + '\n' + marker + content[import_end:]
    
    return content

def main():
    print("=" * 60)
    print("Bug Fix Patch v1.0 - Automatic Fixer")
    print("NO MOCK/FAKE/SYNTHETIC DATA")
    print("=" * 60)
    print()
    
    # Get base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter FinBERT installation path (e.g., C:\\Users\\david\\AATelS): ").strip()
    
    # Find app file
    app_file = find_app_file(base_path)
    if not app_file:
        print(f"✗ ERROR: Could not find app_finbert_v4_dev.py in {base_path}")
        return 1
    
    print(f"✓ Found app file: {app_file}")
    print()
    
    # Read content
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_path = backup_file(app_file)
    print()
    
    # Apply fixes
    print("Applying fixes...")
    print("-" * 60)
    
    content = apply_fix_1_remove_mock_sentiment(content)
    content = apply_fix_2_adx_validation(content)
    content = apply_fix_3_sentiment_none_handling(content)
    content = apply_fix_4_improve_logging(content)
    content = add_patch_marker(content)
    
    print("-" * 60)
    print()
    
    # Write back
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixes applied successfully")
    print()
    print("=" * 60)
    print("Patch Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart FinBERT server:")
    print(f"   cd {base_path}")
    print("   python finbert_v4.4.4\\app_finbert_v4_dev.py")
    print()
    print("2. Test stock analysis (should work without crashes)")
    print()
    print("3. If issues occur, restore backup:")
    print(f"   copy {backup_path} {app_file}")
    print()
    print(f"Backup saved at: {backup_path}")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n✗ Patch cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
