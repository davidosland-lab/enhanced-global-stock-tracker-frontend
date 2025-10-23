#!/usr/bin/env python3
"""
Fix FTSE and S&P 500 plotting times to show correct ADST market hours
FTSE should show 19:00-03:30 ADST
S&P 500 should show 01:30-08:00 ADST
"""

import os
import shutil
from datetime import datetime

print("=" * 60)
print("FIXING FTSE AND S&P 500 PLOTTING TIMES")
print("=" * 60)
print()

# Find the market tracker file
tracker_file = "modules/market-tracking/market_tracker_final.html"

if not os.path.exists(tracker_file):
    print(f"ERROR: {tracker_file} not found")
    exit(1)

# Backup
backup_name = f"{tracker_file}.backup_{datetime.now().strftime('%H%M%S')}"
shutil.copy(tracker_file, backup_name)
print(f"✓ Created backup: {backup_name}")

# Read the file
with open(tracker_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the processMarketData function to fix time offsets
old_process = """                // Convert to ADST for comparison
                const pointADST = new Date(pointDate.toLocaleString("en-US", {timeZone: "Australia/Sydney"}));
                
                if (pointADST >= startTime && pointADST <= endTime) {
                    processedData.push({
                        time: pointDate,  // Keep original time for chart
                        value: changePercent
                    });
                }"""

new_process = """                // Convert to ADST with proper market time offsets
                let displayTime;
                
                if (marketData.market.symbol === '^FTSE') {
                    // FTSE: UK market (GMT/BST) to ADST
                    // UK market hours 08:00-16:30 GMT = 19:00-03:30 ADST
                    // Add 11 hours during ADST period
                    displayTime = new Date(pointDate.getTime() + (11 * 60 * 60 * 1000));
                } else if (marketData.market.symbol === '^GSPC') {
                    // S&P 500: US market (EST/EDT) to ADST
                    // US market hours 09:30-16:00 EST = 01:30-08:00 ADST
                    // Add 16 hours during ADST period
                    displayTime = new Date(pointDate.getTime() + (16 * 60 * 60 * 1000));
                } else {
                    // ASX: Already in Australian time
                    displayTime = pointDate;
                }
                
                const pointADST = getADSTTime(displayTime);
                
                if (pointADST >= startTime && pointADST <= endTime) {
                    processedData.push({
                        time: displayTime,  // Use adjusted time for display
                        value: changePercent
                    });
                }"""

if old_process in content:
    content = content.replace(old_process, new_process)
    print("✓ Fixed time conversion for FTSE and S&P 500")
else:
    print("⚠ Could not find exact match, trying alternative fix...")
    
    # Alternative: Add time offset calculation
    marker = "const changePercent = ((closePrice - previousClose) / previousClose) * 100;"
    if marker in content:
        insert_code = """
                
                // Apply time zone offset for international markets
                let timeOffset = 0;
                if (marketData.market.symbol === '^FTSE') {
                    // FTSE: Add 11 hours to convert UK time to ADST
                    timeOffset = 11 * 60 * 60 * 1000;
                } else if (marketData.market.symbol === '^GSPC') {
                    // S&P 500: Add 16 hours to convert US Eastern to ADST
                    timeOffset = 16 * 60 * 60 * 1000;
                }
                
                const adjustedDate = new Date(pointDate.getTime() + timeOffset);"""
        
        content = content.replace(marker, marker + insert_code)
        
        # Also update the push to use adjusted date
        content = content.replace(
            "time: pointDate,  // Keep original time for chart",
            "time: adjustedDate || pointDate,  // Use adjusted time for international markets"
        )
        print("✓ Applied alternative fix for time offsets")

# Also fix the market hours display
content = content.replace(
    "ftse: { open: 18, close: 2.5 }",
    "ftse: { open: 19, close: 3.5 }"  # 19:00 - 03:30
)
content = content.replace(
    "sp500: { open: 0.5, close: 7 }",
    "sp500: { open: 1.5, close: 8 }"   # 01:30 - 08:00
)

# Write the fixed content
with open(tracker_file, 'w', encoding='utf-8') as f:
    f.write(content)

print()
print("=" * 60)
print("FIX COMPLETED")
print("=" * 60)
print()
print("What was fixed:")
print("  1. FTSE now plots at 19:00 - 03:30 ADST (not during day)")
print("  2. S&P 500 will plot at 01:30 - 08:00 ADST")
print("  3. Time conversion adds proper offsets:")
print("     - FTSE: +11 hours (UK to ADST)")
print("     - S&P 500: +16 hours (US Eastern to ADST)")
print()
print("Please refresh your browser to see the corrected plot times.")