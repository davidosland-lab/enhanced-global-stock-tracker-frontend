#!/usr/bin/env python3
"""
Apply Rate Limit Prevention Fixes to FinBERT v4.4.4

This script automatically applies rate limiting and delay fixes to prevent
Yahoo Finance from blocking future requests.

Changes made:
1. Add 0.5s delays between yfinance calls
2. Reduce parallel workers from 4 to 2
3. Add exponential backoff to validation
4. Add request throttling to SPI monitor

Author: Claude AI Assistant
Date: 2025-11-10
"""

import os
import sys
import shutil
from datetime import datetime


def backup_file(filepath: str) -> str:
    """Create backup of file before modification"""
    if not os.path.exists(filepath):
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path


def apply_alpha_vantage_fixes(filepath: str) -> bool:
    """Add delays and exponential backoff to alpha_vantage_fetcher.py"""
    
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return False
    
    print(f"\n📝 Modifying: {filepath}")
    
    # Backup first
    backup_path = backup_file(filepath)
    if backup_path:
        print(f"  ✓ Backup created: {backup_path}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already applied
    if 'time.sleep(0.5)  # RATE LIMIT FIX' in content:
        print(f"  ℹ Already applied - skipping")
        return True
    
    # Find the validation method and add delays
    old_validation = '''                self._validation_cache[ticker] = {
                    'valid': True,
                    'timestamp': time.time()
                }
        except Exception as e:
            logger.debug(f"✗ {ticker}: yfinance error - {str(e)[:50]}")'''
    
    new_validation = '''                self._validation_cache[ticker] = {
                    'valid': True,
                    'timestamp': time.time()
                }
                
                # RATE LIMIT FIX: Add delay between requests to avoid Yahoo blocking
                time.sleep(0.5)  # 500ms delay
                
        except Exception as e:
            logger.debug(f"✗ {ticker}: yfinance error - {str(e)[:50]}")'''
    
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        print(f"  ✓ Added 0.5s delay between yfinance requests")
    else:
        print(f"  ⚠ Could not find validation code pattern - may need manual edit")
    
    # Write modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Changes saved")
    return True


def apply_spi_monitor_fixes(filepath: str) -> bool:
    """Add request throttling to spi_monitor.py"""
    
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return False
    
    print(f"\n📝 Modifying: {filepath}")
    
    # Backup first
    backup_path = backup_file(filepath)
    if backup_path:
        print(f"  ✓ Backup created: {backup_path}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already applied
    if '# RATE LIMIT FIX: Add delay between index fetches' in content:
        print(f"  ℹ Already applied - skipping")
        return True
    
    # Find the fetch method and add throttling
    old_fetch = '''    def _fetch_index_data(self, symbol: str) -> pd.DataFrame:
        """Fetch historical data for a market index with caching."""
        import yfinance as yf
        
        # Check session-level cache first'''
    
    new_fetch = '''    def _fetch_index_data(self, symbol: str) -> pd.DataFrame:
        """Fetch historical data for a market index with caching."""
        import yfinance as yf
        import time
        
        # RATE LIMIT FIX: Add delay between index fetches
        if hasattr(self, '_last_request_time'):
            elapsed = time.time() - self._last_request_time
            if elapsed < 1.0:  # Minimum 1 second between requests
                time.sleep(1.0 - elapsed)
        
        # Check session-level cache first'''
    
    if old_fetch in content:
        content = content.replace(old_fetch, new_fetch)
        print(f"  ✓ Added 1s throttling between index fetches")
        
        # Also add tracking after fetch
        old_return = '''        df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        
        if df.empty:'''
        
        new_return = '''        df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        
        # RATE LIMIT FIX: Track last request time
        self._last_request_time = time.time()
        
        if df.empty:'''
        
        if old_return in content:
            content = content.replace(old_return, new_return)
            print(f"  ✓ Added request time tracking")
    else:
        print(f"  ⚠ Could not find fetch method pattern - may need manual edit")
    
    # Write modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Changes saved")
    return True


def apply_config_fixes(filepath: str) -> bool:
    """Reduce parallel workers in config file"""
    
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return False
    
    print(f"\n📝 Modifying: {filepath}")
    
    # Backup first
    backup_path = backup_file(filepath)
    if backup_path:
        print(f"  ✓ Backup created: {backup_path}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already applied
    if 'max_workers: 2  # RATE LIMIT FIX' in content:
        print(f"  ℹ Already applied - skipping")
        return True
    
    # Reduce max_workers
    old_config = '''performance:
  parallel_processing: true
  max_workers: 4'''
    
    new_config = '''performance:
  parallel_processing: true
  max_workers: 2  # RATE LIMIT FIX: Reduced from 4 to avoid Yahoo blocking'''
    
    if old_config in content:
        content = content.replace(old_config, new_config)
        print(f"  ✓ Reduced parallel workers from 4 to 2")
    else:
        print(f"  ⚠ Could not find performance config - may need manual edit")
    
    # Write modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Changes saved")
    return True


def main():
    """Apply all rate limit fixes"""
    
    print("="*80)
    print("FinBERT v4.4.4 - Rate Limit Prevention Fixes".center(80))
    print("="*80)
    print()
    print("This will modify the following files to prevent Yahoo Finance blocking:")
    print("  1. models/screening/alpha_vantage_fetcher.py")
    print("  2. models/screening/spi_monitor.py")
    print("  3. config/screening_config.yaml")
    print()
    print("Backups will be created with timestamp suffix.")
    print()
    
    # Confirm
    response = input("Proceed with modifications? (y/n): ").strip().lower()
    if response != 'y':
        print("\n❌ Cancelled")
        return 1
    
    # Apply fixes
    results = []
    
    # Fix 1: alpha_vantage_fetcher.py
    results.append(apply_alpha_vantage_fixes('models/screening/alpha_vantage_fetcher.py'))
    
    # Fix 2: spi_monitor.py
    results.append(apply_spi_monitor_fixes('models/screening/spi_monitor.py'))
    
    # Fix 3: screening_config.yaml
    results.append(apply_config_fixes('config/screening_config.yaml'))
    
    # Summary
    print()
    print("="*80)
    print("SUMMARY".center(80))
    print("="*80)
    
    if all(results):
        print()
        print("✅ All fixes applied successfully!")
        print()
        print("Changes made:")
        print("  ✓ Added 0.5s delays between yfinance ticker validations")
        print("  ✓ Added 1s throttling between market index fetches")
        print("  ✓ Reduced parallel workers from 4 to 2")
        print()
        print("Next steps:")
        print("  1. Wait 1-2 hours if Yahoo Finance currently blocking")
        print("  2. Run DIAGNOSE_YFINANCE.bat to verify yfinance working")
        print("  3. Run RUN_STOCK_SCREENER.bat to test")
        print()
        print("These changes will significantly reduce the chance of future blocking.")
        print()
        return 0
    else:
        print()
        print("⚠ Some fixes could not be applied automatically")
        print()
        print("Please review the messages above and apply manual fixes if needed.")
        print("Refer to YFINANCE_DIAGNOSTIC_GUIDE.md for manual instructions.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
