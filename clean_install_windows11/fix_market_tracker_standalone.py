#!/usr/bin/env python3
"""
Standalone fix for market tracker time display issues
Works regardless of directory structure
"""

import os
import sys
from pathlib import Path

def find_tracker_files():
    """Find all market tracker files"""
    current_dir = Path.cwd()
    possible_files = []
    
    # Search patterns
    patterns = [
        "**/market_tracker*.html",
        "**/indices_tracker*.html",
        "**/global_market*.html"
    ]
    
    for pattern in patterns:
        possible_files.extend(current_dir.glob(pattern))
    
    return possible_files

def fix_tracker_file(filepath):
    """Apply time zone fixes to a tracker file"""
    print(f"\nProcessing: {filepath}")
    
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Apply fixes
        replacements = [
            ('AEST', 'ADST', 'Time zone label'),
            ('Trading: 18:00 - 02:30 ADST', 'Trading: 19:00 - 03:30 ADST', 'FTSE hours'),
            ('Trading: 00:30 - 07:00 ADST', 'Trading: 01:30 - 08:00 ADST', 'SP500 hours'),
            ('hours >= 18 || hours < 2.5', 'hours >= 19 || hours < 3.5', 'FTSE logic'),
            ('hours >= 0.5 && hours < 7', 'hours >= 1.5 && hours < 8', 'SP500 logic')
        ]
        
        for old_text, new_text, description in replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                changes.append(f"  ✓ Fixed {description}")
        
        # Check if we need to add ADST function
        if 'ADST' in content and 'getADSTTime' not in content:
            # Add ADST conversion function
            adst_function = """
        // Get current time in ADST (UTC+11)
        function getADSTTime(date = new Date()) {
            const utcTime = date.getTime() + (date.getTimezoneOffset() * 60000);
            return new Date(utcTime + (11 * 3600000));
        }
        """
            # Find insertion point
            if 'let chart = null;' in content:
                content = content.replace('let chart = null;', 
                                        adst_function + '\n        let chart = null;')
                changes.append("  ✓ Added ADST time function")
        
        # Fix timezone conversions
        old_conversions = [
            'new Date(now.toLocaleString("en-US", {timeZone: "Australia/Sydney"}))',
            'new Date(aestTime.toLocaleString("en-US", {timeZone: "Australia/Sydney"}))'
        ]
        
        for old_conv in old_conversions:
            if old_conv in content:
                if 'getADSTTime' in content:
                    # If we have the function, use it
                    content = content.replace(old_conv, 'getADSTTime(now)')
                    changes.append("  ✓ Fixed timezone conversion")
                else:
                    # Otherwise use direct UTC+11 calculation
                    new_conv = '(function(d) { var u = d.getTime() + (d.getTimezoneOffset() * 60000); return new Date(u + (11 * 3600000)); })(now)'
                    content = content.replace(old_conv, new_conv)
                    changes.append("  ✓ Fixed timezone conversion (inline)")
        
        # Write if changed
        if content != original_content:
            # Backup
            backup_path = str(filepath) + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed version
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  File updated successfully!")
            for change in changes:
                print(change)
            print(f"  Backup saved as: {backup_path}")
            return True
        else:
            print("  No changes needed (already fixed or different version)")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("MARKET TRACKER TIME ZONE FIX")
    print("=" * 60)
    print()
    print("This script will fix time display issues in market tracker")
    print("Changes AEST to ADST and updates market hours")
    print()
    
    # Find tracker files
    print("Searching for market tracker files...")
    files = find_tracker_files()
    
    if not files:
        print("\nNo market tracker files found!")
        print("Please run this script from your StockTracker directory")
        sys.exit(1)
    
    print(f"\nFound {len(files)} tracker file(s):")
    for f in files:
        print(f"  - {f}")
    
    # Fix each file
    fixed_count = 0
    for filepath in files:
        if fix_tracker_file(filepath):
            fixed_count += 1
    
    print()
    print("=" * 60)
    print(f"COMPLETE: Fixed {fixed_count} file(s)")
    print("=" * 60)
    print()
    print("Expected market hours after fix:")
    print("  ASX:   10:00 - 16:00 ADST")
    print("  FTSE:  19:00 - 03:30 ADST")
    print("  SP500: 01:30 - 08:00 ADST")
    print()
    print("Please refresh your browser to see the changes")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")