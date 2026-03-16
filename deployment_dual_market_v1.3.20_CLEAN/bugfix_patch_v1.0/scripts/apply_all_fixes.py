#!/usr/bin/env python3
"""
Bug Fix Patch v1.0 - Master Installer
Applies all fixes automatically

Fixes Applied:
1. Remove mock sentiment fallback (NO FAKE DATA)
2. Add ADX validation
3. Add sentiment None handling
4. Disable broken LSTM
5. Improve error logging
"""

import os
import sys
import subprocess

def run_fix_script(script_path, base_path):
    """Run a fix script"""
    try:
        result = subprocess.run(
            [sys.executable, script_path, base_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error running {script_path}: {e}")
        return False

def main():
    print("=" * 70)
    print("Bug Fix Patch v1.0 - Master Installer")
    print("Fixes app errors WITHOUT adding fake/mock data")
    print("=" * 70)
    print()
    
    # Get base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter FinBERT installation path (e.g., C:\\Users\\david\\AATelS): ").strip()
    
    print(f"Installation path: {base_path}")
    print()
    
    # Verify path
    if not os.path.exists(base_path):
        print(f"✗ ERROR: Path not found: {base_path}")
        return 1
    
    if not os.path.exists(os.path.join(base_path, 'finbert_v4.4.4')):
        print(f"✗ ERROR: FinBERT v4.4.4 not found in {base_path}")
        return 1
    
    print("✓ FinBERT installation found")
    print()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fixes_dir = os.path.join(os.path.dirname(script_dir), 'fixes')
    
    fixes = [
        ('fix_app_errors.py', 'App error fixes (remove mock data, add validation)'),
        ('fix_config.py', 'Config updates (disable broken LSTM)'),
    ]
    
    print("Applying fixes...")
    print("-" * 70)
    
    success_count = 0
    for script_name, description in fixes:
        print(f"\n[{success_count + 1}/{len(fixes)}] {description}")
        print("-" * 70)
        
        script_path = os.path.join(fixes_dir, script_name)
        if not os.path.exists(script_path):
            print(f"⚠ WARNING: Script not found: {script_path}")
            continue
        
        if run_fix_script(script_path, base_path):
            success_count += 1
            print(f"✓ {script_name} completed")
        else:
            print(f"✗ {script_name} failed (check errors above)")
    
    print()
    print("=" * 70)
    print(f"Patch Installation Complete: {success_count}/{len(fixes)} fixes applied")
    print("=" * 70)
    print()
    
    if success_count == len(fixes):
        print("✓ All fixes applied successfully!")
        print()
        print("Next steps:")
        print("1. Restart FinBERT server:")
        print(f"   cd {base_path}")
        print("   python finbert_v4.4.4\\app_finbert_v4_dev.py")
        print()
        print("2. Test stock analysis:")
        print("   - Should work without crashes")
        print("   - No mock/fake data used")
        print("   - Real sentiment when available")
        print("   - LSTM disabled (no fake predictions)")
        print()
        print("3. Swing trading backtest still works:")
        print("   curl -X POST http://localhost:5001/api/backtest/swing ...")
        print()
        return 0
    else:
        print(f"⚠ WARNING: Only {success_count}/{len(fixes)} fixes applied")
        print("Review errors above and try manual installation if needed")
        print()
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n✗ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
