#!/usr/bin/env python3
"""
Diagnose .env file issues
"""

import os
import sys

print("="*60)
print("ENVIRONMENT FILE DIAGNOSTIC")
print("="*60)

# Check for .env files
env_files = ['.env', '.flaskenv', '.env.local', '.env.production']

for env_file in env_files:
    if os.path.exists(env_file):
        print(f"\n⚠️ Found: {env_file}")
        try:
            # Try to read the file
            with open(env_file, 'rb') as f:
                content = f.read(100)  # Read first 100 bytes
                
                # Check for BOM or other issues
                if content.startswith(b'\xff\xfe'):
                    print(f"  ❌ File has UTF-16 LE BOM - This causes the error!")
                elif content.startswith(b'\xfe\xff'):
                    print(f"  ❌ File has UTF-16 BE BOM - This causes the error!")
                elif content.startswith(b'\xff'):
                    print(f"  ❌ File starts with 0xFF byte - This causes the error!")
                elif content.startswith(b'\xef\xbb\xbf'):
                    print(f"  ⚠️ File has UTF-8 BOM")
                else:
                    print(f"  ✅ File encoding looks OK")
                    
                print(f"  First bytes: {content[:20].hex()}")
                
            # Try to read as text
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"  ✅ Can read as UTF-8 ({len(lines)} lines)")
            except UnicodeDecodeError as e:
                print(f"  ❌ Cannot read as UTF-8: {e}")
                
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    else:
        print(f"✅ Not found: {env_file}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)

if any(os.path.exists(f) for f in env_files):
    print("⚠️ Found .env files that may be causing issues.")
    print("Run these commands to fix:")
    print("  1. del .env")
    print("  2. del .flaskenv")
    print("  3. set FLASK_SKIP_DOTENV=1")
    print("  4. python simple_server.py")
else:
    print("✅ No .env files found.")
    print("The issue might be in your Python installation.")
    print("Try running: python simple_server.py")

print("="*60)