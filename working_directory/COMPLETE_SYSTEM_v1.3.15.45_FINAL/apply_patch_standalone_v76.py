"""
Market Chart Patch Applier v1.3.15.76
This script applies the market chart fix by replacing the old function
FIXED: Proper line-based extraction to avoid regex issues
"""
import re
import sys
import os

def apply_patch():
    print('[1/5] Reading fix file...')
    
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
        # Read the fix file - get lines 7-251 (the function)
        with open('FIX_MARKET_CHART_v1.3.15.68.py', 'r', encoding='utf-8') as f:
            fix_lines = f.readlines()
        
        # Extract function (lines 7-251, which is indices 6-250)
        function_lines = fix_lines[6:251]
        
        # Join and rename function
        fixed_function = ''.join(function_lines)
        fixed_function = fixed_function.replace('create_market_performance_chart_fixed', 
                                               'create_market_performance_chart')
        
        print(f'[OK] Fix file loaded ({len(fixed_function)} chars)')
        
        print('[2/5] Reading dashboard...')
        
        # Read dashboard
        with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        print('[OK] Dashboard loaded')
        
        print('[3/5] Finding old function...')
        
        # Find the old function using a more reliable pattern
        # Match from "def create_market_performance_chart(state):" to the next "def " or "@app.callback"
        pattern = r'(def create_market_performance_chart\(state\):.*?)(\ndef [a-zA-Z_]|\n@app\.callback)'
        
        match = re.search(pattern, dashboard_content, re.DOTALL)
        if not match:
            print('[ERROR] Could not find old function in dashboard')
            return False
        
        old_function = match.group(1)
        next_part = match.group(2)
        
        print(f'[OK] Found old function ({len(old_function)} chars)')
        
        print('[4/5] Replacing function...')
        
        # Replace: old function + separator => new function + separator
        new_dashboard = dashboard_content.replace(
            old_function + next_part,
            fixed_function + next_part
        )
        
        # Verify replacement happened
        if new_dashboard == dashboard_content:
            print('[ERROR] Replacement did not occur')
            return False
        
        print('[OK] Function replaced')
        
        print('[5/5] Writing patched dashboard...')
        
        # Write back
        with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
            f.write(new_dashboard)
        
        print('[OK] Dashboard patched successfully!')
        
        # Verify syntax
        print('[VERIFY] Checking Python syntax...')
        try:
            compile(new_dashboard, 'unified_trading_dashboard.py', 'exec')
            print('[OK] Syntax is valid!')
        except SyntaxError as e:
            print(f'[ERROR] Syntax error after patch: {e}')
            print('Rolling back...')
            with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
                f.write(dashboard_content)
            return False
        
        return True
        
    except Exception as e:
        print(f'[ERROR] {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('=' * 80)
    print('  MARKET CHART PATCH APPLIER v1.3.15.76')
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
        print('If you see a syntax error, the patch was automatically rolled back.')
    print()
    
    input('Press Enter to exit...')
