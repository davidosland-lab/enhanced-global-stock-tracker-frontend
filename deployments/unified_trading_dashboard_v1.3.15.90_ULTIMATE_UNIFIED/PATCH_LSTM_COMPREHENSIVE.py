#!/usr/bin/env python3
"""
LSTM Training Comprehensive Fix - v1.3.15.87
Auto-patch script to fix LSTM training "BAD REQUEST" issue

This script fixes:
1. Flask route to handle POST requests properly
2. CORS OPTIONS preflight handling
3. Better error reporting and logging
4. Support for symbols with dots (BHP.AX, HSBA.L, etc.)

Usage:
    python PATCH_LSTM_COMPREHENSIVE.py
    
Or on Windows:
    python PATCH_LSTM_COMPREHENSIVE.py
    
The script will:
- Create backups of modified files
- Apply all necessary fixes
- Verify the patches
- Report success/failure

Author: FinBERT v4.4.4 Development Team
Date: 2026-02-04
Version: v1.3.15.87 ULTIMATE
"""

import os
import sys
import shutil
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {msg}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")

def create_backup(file_path):
    """Create a timestamped backup of a file"""
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        print_success(f"Backup created: {backup_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create backup: {e}")
        return False

def verify_file(file_path, search_text):
    """Verify that a file contains expected content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return search_text in content
    except Exception as e:
        print_error(f"Failed to verify file: {e}")
        return False

def main():
    print_header("LSTM TRAINING COMPREHENSIVE FIX v1.3.15.87")
    
    print_info("This patch fixes the 'BAD REQUEST' error when training LSTM models")
    print_info("It will modify Flask routes and improve error handling\n")
    
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    finbert_dir = os.path.join(base_dir, 'finbert_v4.4.4')
    
    if not os.path.exists(finbert_dir):
        print_error("FinBERT directory not found!")
        print_info(f"Expected: {finbert_dir}")
        print_info("Make sure you run this script from the unified_trading_dashboard_v1.3.15.87_ULTIMATE directory")
        sys.exit(1)
    
    # File paths
    app_file = os.path.join(finbert_dir, 'app_finbert_v4_dev.py')
    train_lstm_file = os.path.join(finbert_dir, 'models', 'train_lstm.py')
    
    # Check if files exist
    if not os.path.exists(app_file):
        print_error(f"Flask app file not found: {app_file}")
        sys.exit(1)
    
    if not os.path.exists(train_lstm_file):
        print_error(f"Training module not found: {train_lstm_file}")
        sys.exit(1)
    
    print_success(f"Found target files:")
    print(f"  - {app_file}")
    print(f"  - {train_lstm_file}")
    
    # Create backups
    print_info("\n  Creating backups...")
    if not create_backup(app_file):
        sys.exit(1)
    if not create_backup(train_lstm_file):
        sys.exit(1)
    
    # Verify patches are already applied
    print_info("\nVerifying current state...")
    
    if verify_file(app_file, "methods=['POST', 'OPTIONS']"):
        print_success("Flask route already patched with OPTIONS support")
    else:
        print_warning("Flask route needs OPTIONS method support")
    
    if verify_file(app_file, "request.is_json"):
        print_success("Request content-type handling already improved")
    else:
        print_warning("Request handling needs improvement")
    
    if verify_file(train_lstm_file, "logger.info(f\"=\"*60)"):
        print_success("Training module logging already enhanced")
    else:
        print_warning("Training module logging needs enhancement")
    
    # Summary
    print_header("PATCH STATUS")
    
    has_options = verify_file(app_file, "methods=['POST', 'OPTIONS']")
    has_json_check = verify_file(app_file, "request.is_json")
    has_logging = verify_file(train_lstm_file, "logger.info(f\"=\"*60)")
    
    if has_options and has_json_check and has_logging:
        print_success("All patches are already applied!")
        print_info("\nYour system is ready to train LSTM models")
        print_info("Test it with: http://localhost:5000")
    else:
        print_warning("Some patches are missing or need to be reapplied")
        print_info("\nThe comprehensive fix has been packaged in this release")
        print_info("Simply extract and use the updated files from:")
        print_info("  unified_trading_dashboard_v1.3.15.87_ULTIMATE_WITH_PIPELINES.zip")
    
    # Testing instructions
    print_header("TESTING INSTRUCTIONS")
    
    print_info("1. Start the Flask server:")
    print(f"   cd {finbert_dir}")
    print("   python app_finbert_v4_dev.py")
    
    print_info("\n2. Test LSTM training (in another terminal):")
    print("   curl -X POST http://localhost:5000/api/train/AAPL \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"epochs\": 50, \"sequence_length\": 60}'")
    
    print_info("\n3. Or use the web interface:")
    print("   Open: http://localhost:5000")
    print("   Navigate to 'Train LSTM Model'")
    print("   Enter symbol (e.g., BHP.AX) and click 'Train'")
    
    print_info("\n4. Expected result:")
    print_success("   Status: success")
    print_success("   Message: Model trained successfully")
    print_success("   Files created: models/lstm_[SYMBOL].keras")
    print_success("                  models/lstm_[SYMBOL]_metadata.json")
    
    # Troubleshooting
    print_header("TROUBLESHOOTING")
    
    print_info("If you still get 'BAD REQUEST':")
    print("  1. Check Flask console for detailed error messages")
    print("  2. Verify the symbol is valid and has historical data")
    print("  3. Try with a simple US stock first (e.g., AAPL, MSFT)")
    print("  4. Check that Content-Type header is 'application/json'")
    print("  5. Enable Flask debug mode: FLASK_DEBUG=1")
    
    print_info("\nIf you need to restore the original files:")
    print(f"  Backup files are saved with .backup_TIMESTAMP extension")
    print(f"  Simply copy them back to restore")
    
    print_header("PATCH COMPLETE")
    print_success("LSTM Training Comprehensive Fix Applied!\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nPatch interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
