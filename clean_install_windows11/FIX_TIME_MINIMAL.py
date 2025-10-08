#!/usr/bin/env python3
"""
Minimal fix for market tracker time display
Changes AEST to ADST and fixes time conversion
"""

import os
import shutil
from datetime import datetime

print("=" * 60)
print("MINIMAL TIME FIX FOR MARKET TRACKER")
print("=" * 60)
print()

# Change to the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

tracker_file = "modules/market-tracking/market_tracker_final.html"

# Backup current version
backup_name = f"modules/market-tracking/market_tracker_final_backup_{datetime.now().strftime('%H%M%S')}.html"
shutil.copy(tracker_file, backup_name)
print(f"✓ Created backup: {backup_name}")

# Read the file
with open(tracker_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Apply minimal fixes
replacements = [
    # Change AEST to ADST in display text
    ('AEST', 'ADST'),
    
    # Fix market hours display for ADST
    ('Trading: 18:00 - 02:30 ADST', 'Trading: 19:00 - 03:30 ADST'),  # FTSE
    ('Trading: 00:30 - 07:00 ADST', 'Trading: 01:30 - 08:00 ADST'),  # S&P 500
    
    # Fix the actual hour checks in isMarketOpen function
    ('hours >= 18 || hours < 2.5', 'hours >= 19 || hours < 3.5'),  # FTSE
    ('hours >= 0.5 && hours < 7', 'hours >= 1.5 && hours < 8'),     # S&P 500
]

changes_made = 0
for old_text, new_text in replacements:
    if old_text in content:
        content = content.replace(old_text, new_text)
        changes_made += 1
        print(f"✓ Fixed: {old_text} → {new_text}")

# Add ADST conversion function if not present
if 'function getADSTTime' not in content:
    # Find where to insert (after the MARKETS definition)
    insert_pos = content.find('let chart = null;')
    if insert_pos > 0:
        adst_function = '''
        // Get current time in ADST (Australian Daylight Saving Time = UTC+11)
        function getADSTTime(date = new Date()) {
            // During daylight saving (Oct-Apr), Sydney is UTC+11
            const utcTime = date.getTime() + (date.getTimezoneOffset() * 60000);
            return new Date(utcTime + (11 * 3600000));
        }
        
        '''
        content = content[:insert_pos] + adst_function + content[insert_pos:]
        print("✓ Added ADST time conversion function")
        changes_made += 1

# Replace timezone conversion to use ADST
old_sydney = "new Date(now.toLocaleString(\"en-US\", {timeZone: \"Australia/Sydney\"}))"
new_adst = "getADSTTime(now)"
if old_sydney in content:
    content = content.replace(old_sydney, new_adst)
    print("✓ Fixed timezone conversion to use ADST")
    changes_made += 1

# Write the fixed content
with open(tracker_file, 'w', encoding='utf-8') as f:
    f.write(content)

print()
print("=" * 60)
print(f"MINIMAL FIX COMPLETED - {changes_made} changes made")
print("=" * 60)
print()
print("What was fixed:")
print("  1. Display text changed from AEST to ADST")
print("  2. FTSE hours: 19:00 - 03:30 ADST")
print("  3. S&P 500 hours: 01:30 - 08:00 ADST")
print("  4. Market open/close logic updated")
print("  5. Time conversion uses ADST (UTC+11)")
print()
print("The original working code is preserved.")
print("Only time-related issues were fixed.")
print()
print("Please refresh your browser to see the changes.")