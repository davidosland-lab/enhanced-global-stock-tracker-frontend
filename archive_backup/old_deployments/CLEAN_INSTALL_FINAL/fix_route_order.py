#!/usr/bin/env python3
"""Fix route order in backend.py so specific routes come before wildcard routes"""

import re

# Read the backend file
with open('backend.py', 'r') as f:
    content = f.read()

# Find the historical/{symbol} endpoint and all its code
historical_symbol_pattern = r'(@app\.get\("/api/historical/\{symbol\}"\).*?)(?=@app\.|# =============|if __name__)'
match = re.search(historical_symbol_pattern, content, re.DOTALL)

if match:
    historical_symbol_code = match.group(1)
    
    # Remove it from its current location
    content = content.replace(historical_symbol_code, '')
    
    # Find where to insert it (after the clear-cache endpoint)
    clear_cache_pattern = r'(@app\.get\("/api/historical/clear-cache"\).*?)(?=@app\.|# =============|if __name__)'
    clear_cache_match = re.search(clear_cache_pattern, content, re.DOTALL)
    
    if clear_cache_match:
        # Insert after clear-cache endpoint
        insert_pos = clear_cache_match.end()
        content = content[:insert_pos] + '\n\n' + historical_symbol_code + content[insert_pos:]
        
        print("✅ Fixed route order - moved /api/historical/{symbol} to end")
        print("   This prevents it from catching /api/historical/statistics")
    else:
        # If we can't find clear-cache, insert before "if __name__"
        insert_pos = content.find('if __name__')
        if insert_pos > 0:
            content = content[:insert_pos] + historical_symbol_code + '\n\n' + content[insert_pos:]
            print("✅ Fixed route order - moved /api/historical/{symbol} to end")
        else:
            print("❌ Could not find insertion point")
else:
    print("❌ Could not find /api/historical/{symbol} endpoint")

# Write the fixed backend
with open('backend.py', 'w') as f:
    f.write(content)

print("\nRoute order is now:")
print("  1. /api/historical/batch-download (POST)")
print("  2. /api/historical/download (POST)")
print("  3. /api/historical/statistics (GET)")
print("  4. /api/historical/best-models/{symbol} (GET)")
print("  5. /api/historical/clear-cache (GET)")
print("  6. /api/historical/{symbol} (GET) - now at end to avoid conflicts")
print("\nRestart the backend to apply changes!")