#!/usr/bin/env python3
import os, sys, subprocess

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("=" * 60)
print("Bug Fix Patch v1.1 - Master Installer")
print("=" * 60)
print()

base_path = sys.argv[1] if len(sys.argv) > 1 else input("Enter FinBERT path: ").strip()

if not os.path.exists(os.path.join(base_path, 'finbert_v4.4.4')):
    print("[ERROR] FinBERT v4.4.4 not found")
    sys.exit(1)

print(f"[OK] FinBERT found: {base_path}")
print()

script_dir = os.path.dirname(os.path.abspath(__file__))
fixes_dir = os.path.join(os.path.dirname(script_dir), 'fixes')

fixes = [
    ('fix_app_errors.py', 'App fixes'),
    ('fix_config.py', 'Config updates'),
]

success = 0
for script_name, desc in fixes:
    print(f"[{success+1}/{len(fixes)}] {desc}")
    print("-" * 60)
    
    script_path = os.path.join(fixes_dir, script_name)
    try:
        result = subprocess.run([sys.executable, script_path, base_path], 
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.returncode == 0:
            success += 1
            print(f"[OK] {script_name} completed")
        else:
            print(f"[ERROR] {script_name} failed")
            if result.stderr:
                print("Error:", result.stderr)
    except Exception as e:
        print(f"[ERROR] {e}")
    print()

print("=" * 60)
print(f"Complete: {success}/{len(fixes)} fixes applied")
print("=" * 60)

if success == len(fixes):
    print("\n[SUCCESS] All fixes applied!")
    print("\nNext: Restart FinBERT server")
else:
    print(f"\n[WARNING] Only {success}/{len(fixes)} applied")

sys.exit(0 if success == len(fixes) else 1)
