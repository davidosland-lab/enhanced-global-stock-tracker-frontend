#!/usr/bin/env python3
"""
Show exactly what needs to be changed for PyTorch fix
"""
import os

print("="*80)
print("  PYTORCH FIX CHECKER")
print("="*80)
print()

file_path = os.path.join('finbert_v4.4.4', 'models', 'finbert_sentiment.py')

if not os.path.exists(file_path):
    print(f"❌ ERROR: File not found: {file_path}")
    print("   Make sure you're in the correct directory")
    input("\nPress Enter to exit...")
    exit(1)

print(f"✓ Found file: {file_path}")
print()

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check if fix is applied
fix_applied = False
line_number = 0

for i, line in enumerate(lines, 1):
    if 'predictions[0]' in line and 'numpy()' in line:
        line_number = i
        if '.detach()' in line:
            fix_applied = True
            print(f"✓ FIX IS APPLIED on line {i}")
            print(f"   {line.strip()}")
        else:
            print(f"✗ FIX NOT APPLIED on line {i}")
            print(f"   Current: {line.strip()}")
            print()
            print(f"   Should be: {line.strip().replace('.cpu().numpy()', '.detach().cpu().numpy()')}")
        break

print()

if fix_applied:
    print("="*80)
    print("  STATUS: FIX IS APPLIED ✓")
    print("="*80)
    print()
    print("The PyTorch fix is already applied.")
    print("If you're still getting the error:")
    print("  1. Make sure you RESTARTED Flask after making the change")
    print("  2. Check if there are multiple installations")
    print("  3. Verify you're editing the correct file")
else:
    print("="*80)
    print("  STATUS: FIX NOT APPLIED ✗")
    print("="*80)
    print()
    print(f"ACTION REQUIRED:")
    print()
    print(f"1. Open this file in a text editor:")
    print(f"   {os.path.abspath(file_path)}")
    print()
    print(f"2. Go to line {line_number}")
    print()
    print(f"3. Add .detach() before .cpu() in that line")
    print()
    print(f"4. Save the file")
    print()
    print(f"5. Restart Flask")

print()
input("Press Enter to exit...")
