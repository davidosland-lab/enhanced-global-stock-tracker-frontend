#!/usr/bin/env python3
"""
Comprehensive Unicode Removal Script
Removes ALL non-ASCII characters from Python files
"""

import os
import re
from pathlib import Path

# Comprehensive replacement map
REPLACEMENTS = {
    # Arrows
    '->': '->',
    '<-': '<-',
    '^': '^',
    'v': 'v',
    '=>': '=>',
    
    # Checkmarks and crosses
    '[OK]': '[OK]',
    '[OK]': '[OK]',
    '[OK]': '[OK]',
    '[X]': '[X]',
    '[X]': '[X]',
    '[ERROR]': '[ERROR]',
    '[X]': '[X]',
    
    # Warnings
    '[!]': '[!]',
    '[!][U+FE0F]': '[!]',  # With emoji variant selector
    '[ALERT]': '[ALERT]',
    
    # Symbols
    '[LOCKED]': '[LOCKED]',
    '[CACHE]': '[CACHE]',
    '[ALERT]': '[ALERT]',
    '[OK]': '[OK]',
    '[WARN]': '[WARN]',
    
    # Mathematical
    'x': 'x',
    '+/-': '+/-',
    ' degrees': ' degrees',
    'u': 'u',
    '/': '/',
    '<=': '<=',
    '>=': '>=',
    '!=': '!=',
    '~=': '~=',
    
    # Box drawing
    '|--': '|--',
    '\--': '\\--',
    '|': '|',
    '-': '-',
    '.--': '.--',
    '--.': '--.',
    '--'': '--\'',
    '-|-': '-|-',
    '-|-': '-|-',
    '-|-': '-|-',
    
    # Bullets
    '*': '*',
    'o': 'o',
    '*': '*',
    '*': '*',
    '*': '*',
    '[]': '[]',
    'o': 'o',
    '*': '*',
    
    # Currency
    'GBP': 'GBP',
    'EUR': 'EUR',
    'JPY': 'JPY',
    'USD': 'USD',
    
    # Emojis - Charts and Trends
    '[CHART]': '[CHART]',
    '[UP]': '[UP]',
    '[DOWN]': '[DOWN]',
    '[NOTE]': '[NOTE]',
    '[DOCS]': '[DOCS]',
    
    # Emojis - Actions
    '[ROCKET]': '[ROCKET]',
    '[TOOL]': '[TOOL]',
    '[SEARCH]': '[SEARCH]',
    '[TIMER]': '[TIMER]',
    '[ALARM]': '[ALARM]',
    '[PLAY]': '[PLAY]',
    '[PAUSE]': '[PAUSE]',
    '[STOP]': '[STOP]',
    
    # Emojis - Status
    '[CELEBRATE]': '[CELEBRATE]',
    '[TARGET]': '[TARGET]',
    '[MONEY]': '[MONEY]',
    '[IDEA]': '[IDEA]',
    '[STAR]': '[STAR]',
    
    # Emojis - Flags
    '[GB]': '[GB]',
    '[US]': '[US]',
    '[AU]': '[AU]',
    
    # Emojis - New/Updated
    '[NEW]': '[NEW]',
    '[UPDATE]': '[UPDATE]',
    '[RECYCLE]': '[RECYCLE]',
    
    # Quotes
    '"': '"',
    '"': '"',
    ''''''''''''''''
    # Dashes
    '--': '--',
    '---': '---',
    '---': '---',
    
    # Ellipsis
    '...': '...',
    
    # Spaces (non-breaking, etc.)
    '\u00a0': ' ',  # Non-breaking space
    '\u2009': ' ',  # Thin space
    '\u200b': '',   # Zero-width space
}

def remove_unicode_from_file(filepath):
    """Remove all non-ASCII characters from a Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply specific replacements first
        for unicode_char, ascii_replacement in REPLACEMENTS.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        # Remove any remaining non-ASCII characters
        # Keep only printable ASCII (0x20-0x7E) plus newlines and tabs
        cleaned = ''
        for char in content:
            code = ord(char)
            if (0x20 <= code <= 0x7E) or char in '\n\r\t':
                cleaned += char
            else:
                # Replace unknown Unicode with placeholder
                if not char.isspace():
                    cleaned += f'[U+{code:04X}]'
        
        if cleaned != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            return True, len(original_content) - len(cleaned)
        
        return False, 0
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False, 0

def main():
    """Process all Python files."""
    root_dir = Path('.')
    files_changed = 0
    total_chars_removed = 0
    
    for py_file in root_dir.rglob('*.py'):
        # Skip __pycache__
        if '__pycache__' in str(py_file):
            continue
        
        changed, chars_removed = remove_unicode_from_file(py_file)
        if changed:
            files_changed += 1
            total_chars_removed += abs(chars_removed)
            print(f"[FIXED] {py_file}")
    
    print(f"\n[SUMMARY]")
    print(f"Files changed: {files_changed}")
    print(f"Characters removed/replaced: {total_chars_removed}")
    print(f"[COMPLETE] All Python files are now ASCII-safe!")

if __name__ == '__main__':
    main()
