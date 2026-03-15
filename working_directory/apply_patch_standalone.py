"""
Market Chart Patch Applier v1.3.15.75
This script applies the market chart fix by replacing the old function
"""
import re
import sys
import os

def apply_patch():
    print('[1/4] Reading fix file...')
    
    # Check if fix file exists
    if not os.path.exists('FIX_MARKET_CHART_v1.3.15.68.py'):
        print('[ERROR] FIX_MARKET_CHART_v1.3.15.68.py not found!')
        print('Please make sure both files are in the same folder.')
        return False
    
    # Check if dashboard exists
    if not os.path.exists('unified_trading_dashboard.py'):
        print('[ERROR] unified_trading_dashboard.py not found!')
        print('Please run this script from the correct folder.')
        return False
    
    try:
        # Read the fix file
        with open('FIX_MARKET_CHART_v1.3.15.68.py', 'r', encoding='utf-8') as f:
            fix_content = f.read()
        
        print('[OK] Fix file loaded')
        
        print('[2/4] Extracting fixed function...')
        
        # Rename the function from _fixed to regular
        fix_content = fix_content.replace('create_market_performance_chart_fixed', 
                                          'create_market_performance_chart')
        
        # Extract the function (from def to before if __name__)
        pattern_extract = r'def create_market_performance_chart\(state\):.*?(?=\n\n\nif __name__|$)'
        match = re.search(pattern_extract, fix_content, re.DOTALL)
        
        if not match:
            print('[ERROR] Could not extract fixed function from fix file')
            return False
        
        fixed_function = match.group(0)
        print(f'[OK] Extracted function ({len(fixed_function)} chars)')
        
        print('[3/4] Applying patch to dashboard...')
        
        # Read dashboard
        with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # Find and replace the old function
        # Pattern matches from "def create_market_performance_chart(state):" 
        # to before the next function/class/callback
        pattern_replace = r'def create_market_performance_chart\(state\):.*?(?=\ndef [a-zA-Z_]|\nclass [a-zA-Z_]|\n@app\.callback|\Z)'
        
        # Check if we found the old function
        old_match = re.search(pattern_replace, dashboard_content, re.DOTALL)
        if not old_match:
            print('[ERROR] Could not find old function in dashboard')
            return False
        
        print(f'[OK] Found old function ({len(old_match.group(0))} chars)')
        
        # Replace
        new_dashboard = re.sub(pattern_replace, fixed_function + '\n\n', 
                              dashboard_content, flags=re.DOTALL)
        
        # Verify replacement happened
        if new_dashboard == dashboard_content:
            print('[ERROR] Replacement did not occur')
            return False
        
        print('[4/4] Writing patched dashboard...')
        
        # Write back
        with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
            f.write(new_dashboard)
        
        print('[OK] Dashboard patched successfully!')
        return True
        
    except Exception as e:
        print(f'[ERROR] {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('=' * 80)
    print('  MARKET CHART PATCH APPLIER v1.3.15.75')
    print('=' * 80)
    print()
    
    success = apply_patch()
    
    print()
    print('=' * 80)
    if success:
        print('  PATCH APPLIED SUCCESSFULLY!')
        print('=' * 80)
        print()
        print('Next step: Restart the dashboard')
        print('  1) Press Ctrl+C in the dashboard window (if running)')
        print('  2) Run START.bat')
        print('  3) Open http://localhost:8050')
        print()
        print('The chart should now show CURRENT data with real-time updates!')
    else:
        print('  PATCH FAILED!')
        print('=' * 80)
        print()
        print('Please check the error messages above.')
        print('Make sure both files are in the same folder:')
        print('  - apply_patch_standalone.py')
        print('  - FIX_MARKET_CHART_v1.3.15.68.py')
        print('  - unified_trading_dashboard.py')
    print()
    
    input('Press Enter to exit...')
