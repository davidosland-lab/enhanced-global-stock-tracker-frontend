"""
Simple Direct Fix for TelegramNotifier
======================================
"""

from pathlib import Path
import shutil
from datetime import datetime

pipeline_file = Path("models/screening/overnight_pipeline.py")
print(f"\nFixing {pipeline_file}...\n")

# Backup
backup = pipeline_file.parent / f"{pipeline_file.name}.backup_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(pipeline_file, backup)
print(f"Backup: {backup.name}")

try:
    # Try UTF-8 first
    content = pipeline_file.read_text(encoding='utf-8')
    encoding_used = 'utf-8'
except:
    # Fall back to latin-1 which can read any byte
    content = pipeline_file.read_text(encoding='latin-1')
    encoding_used = 'latin-1'

print(f"Read file using: {encoding_used}")

# Simple approach: add the line at the very beginning after the docstring
lines = content.split('\n')

# Find the end of the module docstring
docstring_end = 0
in_docstring = False
for i, line in enumerate(lines):
    if '"""' in line or "'''" in line:
        if not in_docstring:
            in_docstring = True
        else:
            docstring_end = i + 1
            break

print(f"Docstring ends at line {docstring_end}")

# Add our fix right after docstring
insert_line = docstring_end if docstring_end > 0 else 0

new_lines = [
    '',
    '# ============================================================================',
    '# CRITICAL FIX: Initialize TelegramNotifier to prevent NameError',
    '# This must be defined before any code tries to reference it',
    '# ============================================================================',
    'TelegramNotifier = None',
    ''
]

# Insert at the right position
for idx, new_line in enumerate(new_lines):
    lines.insert(insert_line + idx, new_line)

print(f"Added fix at line {insert_line}")

# Write back
content = '\n'.join(lines)

try:
    pipeline_file.write_text(content, encoding=encoding_used)
    print(f"✓ File written using: {encoding_used}")
except:
    # Try with UTF-8 if latin-1 write fails
    pipeline_file.write_text(content, encoding='utf-8', errors='ignore')
    print("✓ File written using: utf-8 (with error ignore)")

print("\n" + "="*60)
print("FIX APPLIED!")
print("="*60)
print("\nNow test with:")
print("  python models\\screening\\overnight_pipeline.py")
print("\nOr run debug test:")
print("  python DEBUG_PIPELINE_IMPORT.py")
print("="*60)

input("\nPress Enter...")
