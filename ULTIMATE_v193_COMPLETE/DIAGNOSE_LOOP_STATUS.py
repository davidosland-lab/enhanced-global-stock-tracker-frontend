#!/usr/bin/env python3
"""
Diagnose why the trading loop stopped running
"""
import os
import sys
import json
import threading
from datetime import datetime

print("=" * 80)
print("TRADING LOOP DIAGNOSTIC")
print("=" * 80)

# Check if the old system has a state file with positions
old_system_state = "/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/state/paper_trading_state.json"

if os.path.exists(old_system_state):
    with open(old_system_state, 'r') as f:
        state = json.load(f)
    
    print(f"\n📊 STATE FILE: {old_system_state}")
    print(f"   Last Update: {state.get('last_update', 'N/A')}")
    print(f"   Version: {state.get('version', 'N/A')}")
    print(f"   Total Capital: ${state.get('capital', {}).get('total', 0):,.2f}")
    print(f"   Cash: ${state.get('capital', {}).get('cash', 0):,.2f}")
    print(f"   Invested: ${state.get('capital', {}).get('invested', 0):,.2f}")
    print(f"   Open Positions: {state.get('positions', {}).get('count', 0)}")
    
    positions = state.get('positions', {}).get('open', [])
    if positions:
        print(f"\n📍 OPEN POSITIONS:")
        for pos in positions:
            print(f"   • {pos.get('symbol', 'N/A')}: {pos.get('quantity', 0)} shares @ ${pos.get('entry_price', 0):.2f}")
            print(f"     Entry: {pos.get('entry_time', 'N/A')}")
    else:
        print(f"\n⚠️  NO POSITIONS IN STATE FILE")
else:
    print(f"\n❌ State file not found: {old_system_state}")

# Check running Python processes
print(f"\n🔍 CHECKING RUNNING PROCESSES:")
os.system("ps aux | grep -E 'unified_trading|paper_trading' | grep -v grep")

# Check if there's a trading loop thread
print(f"\n🧵 CHECKING FOR TRADING THREADS:")
print(f"   Active threads: {threading.active_count()}")
for thread in threading.enumerate():
    print(f"   • {thread.name} (daemon: {thread.daemon}, alive: {thread.is_alive()})")

# Check log file timestamps
print(f"\n📝 LOG FILE STATUS:")
log_dir = "/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/logs"
if os.path.exists(log_dir):
    for log_file in os.listdir(log_dir):
        if log_file.endswith('.log'):
            filepath = os.path.join(log_dir, log_file)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"   • {log_file}: {size:,} bytes, modified {mtime}")

# Look for any recent errors in the log
print(f"\n🚨 CHECKING FOR RECENT ERRORS IN UNIFIED_TRADING.LOG:")
unified_log = "/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/logs/unified_trading.log"
if os.path.exists(unified_log):
    os.system(f"tail -50 {unified_log} | grep -i -E 'error|exception|traceback|failed|stopped' || echo '   No errors found in last 50 lines'")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
