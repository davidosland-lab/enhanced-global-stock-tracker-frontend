"""
Windows Encoding Fix - Replace Unicode emojis with ASCII
========================================================

Fixes UnicodeEncodeError on Windows console (cp1252 encoding)
by replacing Unicode emojis with ASCII equivalents.

Usage:
    python fix_windows_encoding.py
"""

import os
import glob
from pathlib import Path

# Emoji replacements
REPLACEMENTS = {
    '[OK]': '[OK]',
    '[X]': '[X]',
    '[!]': '[!]',
    '[X]': '[X]',
    '[=>]': '[=>]',
    '[#]': '[#]',
    '[i]': '[i]',
    '[*]': '[*]',
    '[*]': '[*]',
    '🔧': '[+]',
    '📁': '[F]',
    '🎮': '[>]',
    '🐍': '[PY]',
    '[GLOBE]': '[W]',
    '[UP]': '[^]',
    '🔍': '[?]',
    '[~]': '[R]',
    '🎉': '[!]',
    '[!]': '[!]',
    '🏆': '[#]',
    '🚫': '[X]',
    '💾': '[D]',
    '🇦🇺': '[AU]',
    '🇺🇸': '[US]',
    '🇬🇧': '[UK]',
}

def fix_file(filepath):
    """Fix Unicode emojis in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all emojis
        for emoji, replacement in REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Main function"""
    print()
    print("="*80)
    print("  WINDOWS ENCODING FIX")
    print("  Replacing Unicode emojis with ASCII characters")
    print("="*80)
    print()
    
    base_path = Path(__file__).parent
    
    # Find all Python files
    python_files = []
    python_files.extend(glob.glob(str(base_path / "*.py")))
    python_files.extend(glob.glob(str(base_path / "models" / "**" / "*.py"), recursive=True))
    
    print(f"Found {len(python_files)} Python files")
    print()
    
    fixed_count = 0
    
    for filepath in python_files:
        if fix_file(filepath):
            print(f"[OK] Fixed: {Path(filepath).name}")
            fixed_count += 1
    
    print()
    print("="*80)
    print(f"Encoding fix complete! Fixed {fixed_count}/{len(python_files)} files")
    print("="*80)
    print()
    print("Emoji replacements:")
    for emoji, replacement in REPLACEMENTS.items():
        print(f"  {emoji} -> {replacement}")
    print()

if __name__ == "__main__":
    main()
