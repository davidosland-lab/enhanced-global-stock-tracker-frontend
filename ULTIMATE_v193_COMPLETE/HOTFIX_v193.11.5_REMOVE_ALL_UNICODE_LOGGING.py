#!/usr/bin/env python3
"""
HOTFIX v193.11.5 - Remove ALL Unicode Characters from Logging
==============================================================

This script systematically replaces all Unicode special characters in logger calls
with ASCII equivalents to prevent UnicodeEncodeError on Windows (cp1252).

Replacements:
  ✓ → [OK]
  ✗ → [X]
  → → ->
  ⚠ → [!]
  🚨 → [ALERT]
  ❌ → [ERROR]
  🔒 → [LOCKED]
  📦 → [CACHE]

Author: Claude (AI Assistant)
Date: 2026-03-07
Version: 193.11.5
"""

import os
import re
from pathlib import Path

# Unicode to ASCII mapping
REPLACEMENTS = {
    '✓': '[OK]',
    '✗': '[X]',
    '→': '->',
    '⚠': '[!]',
    '🚨': '[ALERT]',
    '❌': '[ERROR]',
    '🔒': '[LOCKED]',
    '📦': '[CACHE]',
    '⚙': '[*]',       # Gear symbol
    '🇺🇸': '[US]',     # US flag
    '🇦🇺': '[AU]',     # AU flag
    '🇬🇧': '[UK]',     # UK flag
    '📊': '[CHART]',   # Chart symbol
    '💰': '[$]',       # Money bag
    '📈': '[UP]',      # Chart increasing
    '📉': '[DOWN]',    # Chart decreasing
    '🛑': '[STOP]',    # Stop sign
    '🎯': '[TARGET]',  # Target
    '🚀': '[BOOST]',   # Rocket
    '📋': '[LIST]',    # Clipboard
    '🔧': '[TOOL]',    # Wrench
    '✅': '[OK]',      # Check mark button
    '️': '',          # Variation selector (invisible)
    '≥': '>=',        # Greater than or equal
    '≤': '<=',        # Less than or equal
    '×': 'x',         # Multiplication
    '£': 'GBP',       # Pound sterling
    '🧠': '[AI]',     # Brain
    '📄': '[DOC]',    # Document
    '🎉': '[PASS]',   # Party popper
    '⚠️': '[!]',      # Warning with variation selector
}

def fix_file(file_path: Path) -> tuple[int, list[str]]:
    """
    Fix a single file by replacing Unicode characters in logger calls.
    
    Returns:
        (replacements_made, changes_list)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Replace each Unicode character
        for unicode_char, ascii_replacement in REPLACEMENTS.items():
            if unicode_char in content:
                # Count occurrences in logger calls
                pattern = rf'logger\.(info|warning|error|debug)\([^)]*{re.escape(unicode_char)}[^)]*\)'
                matches = re.findall(pattern, content)
                if matches:
                    content = content.replace(unicode_char, ascii_replacement)
                    changes.append(f"  {unicode_char} -> {ascii_replacement} ({len(matches)} logger calls)")
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return (len(changes), changes)
        else:
            return (0, [])
            
    except Exception as e:
        print(f"[ERROR] Failed to process {file_path}: {e}")
        return (0, [])

def main():
    """Main execution"""
    base_path = Path(__file__).parent
    
    print("=" * 80)
    print("HOTFIX v193.11.5 - Remove ALL Unicode from Logging")
    print("=" * 80)
    print()
    
    # Files with known Unicode issues
    target_files = [
        'core/paper_trading_coordinator.py',
        'finbert_v4.4.4/app_finbert_v4_dev.py',
        'finbert_v4.4.4/models/finbert_sentiment.py',
        'finbert_v4.4.4/models/lstm_predictor.py',
        'finbert_v4.4.4/models/market_timezones.py',
        'finbert_v4.4.4/models/prediction_manager.py',
        'finbert_v4.4.4/models/prediction_scheduler.py',
        'finbert_v4.4.4/models/screening/stock_scanner.py',
        'finbert_v4.4.4/models/trading/order_manager.py',
        'finbert_v4.4.4/models/trading/position_manager.py',
        'finbert_v4.4.4/train_lstm_batch.py',
        'finbert_v4.4.4/train_lstm_custom.py',
        'ml_pipeline/market_monitoring.py',
        'models/cross_market_features.py',
        'models/market_data_fetcher.py',
        'models/regime_aware_opportunity_scorer.py',
        'patches/opportunity_monitor_integration.py',
        'pipelines/models/screening/lstm_trainer.py',
        'pipelines/models/screening/overnight_pipeline.py',
        'pipelines/models/screening/spi_monitor.py',
        'pipelines/models/screening/uk_overnight_pipeline.py',
        'pipelines/models/screening/us_overnight_pipeline.py',
        'scripts/run_au_pipeline_v1.3.13.py',
        'scripts/run_uk_full_pipeline.py',
        'scripts/test_pipeline_to_dashboard_flow.py',
        'test_parquet_duckdb.py',
    ]
    
    total_files_fixed = 0
    total_replacements = 0
    
    for file_rel in target_files:
        file_path = base_path / file_rel
        if not file_path.exists():
            print(f"[SKIP] {file_rel} (not found)")
            continue
        
        count, changes = fix_file(file_path)
        if count > 0:
            print(f"[OK] {file_rel}")
            for change in changes:
                print(change)
            total_files_fixed += 1
            total_replacements += count
        else:
            print(f"[SKIP] {file_rel} (no changes needed)")
    
    print()
    print("=" * 80)
    print(f"SUMMARY: Fixed {total_files_fixed} files, {total_replacements} replacements")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review the changes with: git diff")
    print("2. Test the pipelines to ensure no Unicode errors")
    print("3. Commit the changes")
    print("4. Create deployment package v193.11.5")

if __name__ == '__main__':
    main()
