#!/usr/bin/env python3
"""
Fix backend.py to restore default values for missing data
This fixes the issue where removing default values broke frontend modules
"""

import re

def fix_backend():
    """Restore default values in backend.py"""
    
    with open('backend.py', 'r') as f:
        content = f.read()
    
    # Restore default values for info.get() calls that were changed
    replacements = [
        # Restore defaults for price data
        ("info.get('currentPrice') or info.get('regularMarketPrice')",
         "info.get('currentPrice') or info.get('regularMarketPrice', 0)"),
        
        ("info.get('previousClose') or info.get('regularMarketPreviousClose')",
         "info.get('previousClose', 0) or info.get('regularMarketPreviousClose', 0)"),
        
        # Restore defaults for all market data fields
        ("\"volume\": info.get('volume'),",
         "\"volume\": info.get('volume', 0),"),
        
        ("\"marketCap\": info.get('marketCap'),",
         "\"marketCap\": info.get('marketCap', 0),"),
        
        ("\"dayHigh\": info.get('dayHigh'),",
         "\"dayHigh\": info.get('dayHigh', 0),"),
        
        ("\"dayLow\": info.get('dayLow'),",
         "\"dayLow\": info.get('dayLow', 0),"),
        
        ("\"yearHigh\": info.get('fiftyTwoWeekHigh'),",
         "\"yearHigh\": info.get('fiftyTwoWeekHigh', 0),"),
        
        ("\"yearLow\": info.get('fiftyTwoWeekLow'),",
         "\"yearLow\": info.get('fiftyTwoWeekLow', 0),"),
        
        ("\"pe_ratio\": info.get('forwardPE'),",
         "\"pe_ratio\": info.get('forwardPE', 0),"),
        
        ("\"dividend_yield\": info.get('dividendYield'),",
         "\"dividend_yield\": info.get('dividendYield', 0),"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Restored default value for: {old[:30]}...")
    
    # Write the fixed content
    with open('backend.py', 'w') as f:
        f.write(content)
    
    print("\n✅ Backend defaults restored successfully!")
    print("\nThis fixes the issue where removing default values caused frontend modules to fail.")
    
    return True

if __name__ == "__main__":
    fix_backend()