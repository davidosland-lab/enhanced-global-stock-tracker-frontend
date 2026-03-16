#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set stop-loss to 1% in backtest_engine.py"""

import os
import shutil
from datetime import datetime

print("\n" + "="*70)
print("  SET STOP-LOSS TO 1%")
print("="*70)

engine_path = 'finbert_v4.4.4/models/backtesting/backtest_engine.py'

# Check file exists
if not os.path.exists(engine_path):
    print("\nERROR: backtest_engine.py not found!")
    print(f"Current directory: {os.getcwd()}")
    print("\nRun from: C:\\Users\\david\\AATelS")
    input("\nPress Enter to exit...")
    exit(1)

# Create backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = "backups"
os.makedirs(backup_dir, exist_ok=True)
backup_path = os.path.join(backup_dir, f"backtest_engine_backup_{timestamp}.py")
shutil.copy2(engine_path, backup_path)
print(f"\nBackup created: {backup_path}")

# Read file
with open(engine_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Change stop-loss to 1%
import re
pattern = r"stop_loss_percent: float = \d+\.?\d*"
match = re.search(pattern, content)

if match:
    old_line = match.group(0)
    old_value = old_line.split('=')[1].strip()
    new_line = "stop_loss_percent: float = 1.0"
    
    content = re.sub(pattern, new_line, content)
    
    print(f"\nChanged: stop_loss_percent from {old_value} to 1.0")
    
    # Write back
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\nSUCCESS!")
    print("\nIMPORTANT:")
    print("1. Restart FinBERT v4.4.4 completely")
    print("2. Run a fresh backtest")
    print("\nNOTE: 1% stop-loss is tighter than recommended 2%")
    print("      May cause more whipsaw (stopped out on noise)")
    print("      But smaller losses when stopped out")
    
else:
    print("\nERROR: Could not find stop_loss_percent in file")
    print("File might not have Phase 2 features")

print("\n" + "="*70)
input("\nPress Enter to exit...")
