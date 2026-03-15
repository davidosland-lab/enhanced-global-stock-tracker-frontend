"""
LSTM Training Hot-Patch - v1.3.15.87
=====================================

Fixes Flask routes to support symbols with dots (BHP.AX, HSBA.L, etc.)

This patch can be applied while the Flask server is running.
Flask's auto-reload will detect the change and restart automatically.

Usage:
    python PATCH_LSTM_TRAINING.py
"""

import os
import sys
import re
from datetime import datetime
import shutil

def main():
    print("=" * 80)
    print("  LSTM TRAINING HOT-PATCH v1.3.15.87")
    print("=" * 80)
    print()
    print("This patch fixes Flask routes to support symbols with dots")
    print("(e.g., BHP.AX, CBA.AX, HSBA.L, BP.L)")
    print()
    
    # Find the target file
    target_file = os.path.join('finbert_v4.4.4', 'app_finbert_v4_dev.py')
    
    if not os.path.exists(target_file):
        print(f"[ERROR] Cannot find {target_file}")
        print()
        print("Please run this patch from the unified_trading_dashboard_v1.3.15.87_ULTIMATE directory")
        print()
        print(f"Current directory: {os.getcwd()}")
        print()
        input("Press Enter to exit...")
        return 1
    
    print(f"[OK] Found target file: {target_file}")
    print()
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{target_file}.backup_{timestamp}"
    
    print("Creating backup...")
    try:
        shutil.copy2(target_file, backup_file)
        print(f"[OK] Backup created: {backup_file}")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to create backup: {e}")
        input("Press Enter to exit...")
        return 1
    
    # Read the file
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        input("Press Enter to exit...")
        return 1
    
    # Apply patches
    print("Applying patches...")
    print()
    
    original_content = content
    changes = 0
    
    # Define the patches
    patches = [
        (r"@app\.route\('/api/train/<symbol>'", 
         "@app.route('/api/train/<path:symbol>'",
         "/api/train/<symbol>"),
        
        (r"@app\.route\('/api/stock/<symbol>'\)",
         "@app.route('/api/stock/<path:symbol>')",
         "/api/stock/<symbol>"),
        
        (r"@app\.route\('/api/sentiment/<symbol>'\)",
         "@app.route('/api/sentiment/<path:symbol>')",
         "/api/sentiment/<symbol>"),
        
        (r"@app\.route\('/api/predictions/<symbol>'\)(?!\S)",
         "@app.route('/api/predictions/<path:symbol>')",
         "/api/predictions/<symbol>"),
        
        (r"@app\.route\('/api/predictions/<symbol>/history'\)",
         "@app.route('/api/predictions/<path:symbol>/history')",
         "/api/predictions/<symbol>/history"),
        
        (r"@app\.route\('/api/predictions/<symbol>/accuracy'\)",
         "@app.route('/api/predictions/<path:symbol>/accuracy')",
         "/api/predictions/<symbol>/accuracy"),
        
        (r"@app\.route\('/api/trading/positions/<symbol>/close'",
         "@app.route('/api/trading/positions/<path:symbol>/close'",
         "/api/trading/positions/<symbol>/close"),
    ]
    
    for i, (pattern, replacement, route_name) in enumerate(patches, 1):
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            print(f"  [{i}/7] Fixed {route_name} route")
            changes += 1
        else:
            print(f"  [{i}/7] Already patched or not found: {route_name}")
    
    print()
    
    if changes == 0:
        print("[INFO] No patches applied (already patched or routes not found)")
        print()
        input("Press Enter to exit...")
        return 0
    
    # Write the patched file
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Applied {changes} patches successfully")
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")
        print("Restoring from backup...")
        try:
            shutil.copy2(backup_file, target_file)
            print("[OK] Restored from backup")
        except Exception as e2:
            print(f"[ERROR] Failed to restore backup: {e2}")
        input("Press Enter to exit...")
        return 1
    
    print()
    print("=" * 80)
    print("  PATCH APPLIED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Changes made:")
    print("  - All Flask routes now accept symbols with dots")
    print("  - Examples: BHP.AX, CBA.AX, HSBA.L, BP.L, SHOP.TO")
    print()
    print("If Flask server is running with auto-reload enabled:")
    print("  - Flask will detect the change and reload automatically")
    print("  - You should see: 'Detected change... Reloading'")
    print("  - Wait 2-3 seconds for reload to complete")
    print()
    print("If Flask server is NOT running or auto-reload is disabled:")
    print("  - Restart the Flask server manually:")
    print("    cd finbert_v4.4.4")
    print("    python app_finbert_v4_dev.py")
    print()
    print("Test the fix:")
    print("  1. Open: http://localhost:5000")
    print("  2. Click: 'Train LSTM Model' button")
    print("  3. Enter symbol: BHP.AX")
    print("  4. Set epochs: 50")
    print("  5. Click: 'Start Training'")
    print()
    print("Expected result: SUCCESS (no more 'BAD REQUEST' error)")
    print()
    print(f"Backup saved to: {backup_file}")
    print()
    print("=" * 80)
    print()
    input("Press Enter to exit...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
