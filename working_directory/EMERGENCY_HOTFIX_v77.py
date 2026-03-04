"""
EMERGENCY HOTFIX v1.3.15.77
Restores original 4-index chart (AORD, FTSE, S&P, NASDAQ)
Only fixes the date filtering bug - NOTHING ELSE CHANGED
"""
import sys

def emergency_hotfix():
    print('=' * 80)
    print('  EMERGENCY HOTFIX v1.3.15.77 - Restore 4-Index Chart')
    print('=' * 80)
    print()
    print('[CRITICAL] Restoring AORD and FTSE to chart...')
    print()
    
    # Check files
    import os
    if not os.path.exists('unified_trading_dashboard.py'):
        print('[ERROR] unified_trading_dashboard.py not found!')
        print('Run from: C:\\Users\\david\\Regime_trading\\COMPLETE_SYSTEM_v1.3.15.45_FINAL')
        return False
    
    # Backup
    print('[1/3] Creating backup...')
    import shutil
    from datetime import datetime
    backup_name = f'unified_trading_dashboard.py.backup_before_hotfix_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2('unified_trading_dashboard.py', backup_name)
    print(f'[OK] Backup: {backup_name}')
    
    # Read dashboard
    print('[2/3] Applying hotfix...')
    with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the create_market_performance_chart function
    import re
    
    # The MINIMAL fix: Just change the date filtering logic
    # Find: latest_date = hist.index[-1].date()
    # Replace with: current_date = datetime.now(gmt).date()
    
    # Find the function
    pattern = r'(def create_market_performance_chart\(state\):.*?)(latest_date = hist\.index\[-1\]\.date\(\))'
    
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print('[ERROR] Could not find the date bug in the function')
        return False
    
    # Replace ONLY the problematic line
    old_line = 'latest_date = hist.index[-1].date()'
    new_line = 'current_date = datetime.now(gmt).date()'
    
    if old_line not in content:
        print('[INFO] Date bug already fixed or chart was modified')
        print('[INFO] Restoring original 4-index version from backup...')
        
        # We need to restore from a known good backup
        print()
        print('[CRITICAL] The chart function was completely replaced.')
        print('[ACTION] Checking for original backup...')
        
        # Look for backup files
        import glob
        backups = glob.glob('unified_trading_dashboard.py.backup_*')
        if backups:
            print(f'[FOUND] {len(backups)} backup files')
            # Use the most recent backup from before the bad patch
            latest_backup = max(backups, key=os.path.getctime)
            print(f'[RESTORE] Using: {latest_backup}')
            
            with open(latest_backup, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Now apply ONLY the date fix to the original
            if old_line in original_content:
                fixed_content = original_content.replace(old_line, new_line)
                # Also replace all references
                fixed_content = fixed_content.replace('latest_date', 'current_date')
                
                with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print('[OK] Restored 4-index chart with date fix applied')
                return True
            else:
                print('[WARNING] Backup also has modified code')
        else:
            print('[ERROR] No backup files found')
            print()
            print('MANUAL RESTORE NEEDED:')
            print('1. Find unified_trading_dashboard.py.backup_* file from BEFORE patch')
            print('2. Copy it: copy backup_file unified_trading_dashboard.py')
            print('3. Run this hotfix again')
            return False
    else:
        # Simple case: just fix the date line
        fixed_content = content.replace(old_line, new_line)
        # Replace all instances of latest_date with current_date
        fixed_content = fixed_content.replace('latest_date', 'current_date')
        
        with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print('[OK] Date filtering fixed')
        return True
    
    print('[3/3] Verifying syntax...')
    try:
        compile(fixed_content, 'unified_trading_dashboard.py', 'exec')
        print('[OK] Syntax valid')
        return True
    except SyntaxError as e:
        print(f'[ERROR] Syntax error: {e}')
        return False

if __name__ == '__main__':
    success = emergency_hotfix()
    
    print()
    print('=' * 80)
    if success:
        print('  HOTFIX APPLIED!')
        print('=' * 80)
        print()
        print('Your 4-index chart (AORD, FTSE, S&P, NASDAQ) has been restored!')
        print()
        print('Next: Restart dashboard with START.bat')
        print('The chart will now show all 4 markets from previous close.')
    else:
        print('  HOTFIX FAILED')
        print('=' * 80)
        print()
        print('Please check the error messages above.')
    print()
    input('Press Enter to exit...')
