#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set custom stop-loss percentage in backtest_engine.py"""

import os
import shutil
from datetime import datetime

print("\n" + "="*70)
print("  SET CUSTOM STOP-LOSS PERCENTAGE")
print("="*70)

# Get stop-loss from user
print("\n" + "="*70)
print("  STOP-LOSS GUIDELINES:")
print("="*70)
print("\n  Day Trading:      0.5% - 1.0%  (minutes to hours)")
print("  Swing Trading:    1.0% - 3.0%  (days to weeks)")
print("  Position Trading: 2.0% - 5.0%  (weeks to months)")
print("  Recommended:      2.0%         (industry standard)")
print("\n" + "="*70)

while True:
    try:
        stop_loss_input = input("\nEnter stop-loss percentage (e.g., 0.1, 1.0, 2.0): ")
        stop_loss = float(stop_loss_input)
        
        if stop_loss <= 0:
            print("ERROR: Stop-loss must be greater than 0")
            continue
        
        if stop_loss > 20:
            print("ERROR: Stop-loss greater than 20% seems unreasonable")
            confirm = input("Continue anyway? (yes/no): ").lower()
            if confirm != 'yes':
                continue
        
        break
    except ValueError:
        print("ERROR: Please enter a valid number")

# Warning for very tight stops
if stop_loss < 0.5:
    print("\n" + "!"*70)
    print("  EXTREME WARNING: Stop-loss under 0.5% is VERY TIGHT!")
    print("!"*70)
    print("\n  Risk: You will be stopped out on normal market noise")
    print("  Result: Likely to lose MORE money, not less")
    print("  Example: At 0.1%, any $0.10 move stops you out")
    print("\n  Bid-ask spread alone can be 0.05-0.15%")
    print("  You may be stopped out within SECONDS of entry")
    print("\n" + "!"*70)
    
    confirm = input("\nAre you SURE you want to proceed? (type 'YES' to confirm): ")
    if confirm != 'YES':
        print("\nCancelled. Wise choice!")
        input("\nPress Enter to exit...")
        exit(0)

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

# Change stop-loss
import re
pattern = r"stop_loss_percent: float = \d+\.?\d*"
match = re.search(pattern, content)

if match:
    old_line = match.group(0)
    old_value = old_line.split('=')[1].strip()
    new_line = f"stop_loss_percent: float = {stop_loss}"
    
    content = re.sub(pattern, new_line, content)
    
    print(f"\nChanged: stop_loss_percent from {old_value} to {stop_loss}")
    
    # Write back
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\nSUCCESS!")
    print("\n" + "="*70)
    print("  IMPORTANT NEXT STEPS:")
    print("="*70)
    print("\n1. Restart FinBERT v4.4.4 completely")
    print("2. Run a fresh backtest")
    print("3. Compare results to previous backtest")
    
    if stop_loss < 0.5:
        print("\n" + "!"*70)
        print("  EXPECT: Very high number of stopped out trades")
        print("  EXPECT: Win rate may DROP significantly")
        print("  EXPECT: May lose MORE total money")
        print("!"*70)
        print("\n  If results are worse, restore from backup:")
        print(f"  copy {backup_path} finbert_v4.4.4\\models\\backtesting\\backtest_engine.py")
    elif stop_loss < 1.0:
        print("\nNOTE: Stop-loss under 1% may cause excessive whipsaw")
        print("      Monitor win rate - if it drops below 35%, increase stop-loss")
    
else:
    print("\nERROR: Could not find stop_loss_percent in file")
    print("File might not have Phase 2 features")

print("\n" + "="*70)
input("\nPress Enter to exit...")
