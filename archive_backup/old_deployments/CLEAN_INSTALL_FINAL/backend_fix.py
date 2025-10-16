"""
Quick Fix Script for backend.py logger issue
Run this to fix the NameError in backend.py
"""

import os

def fix_backend():
    # Read the backend.py file
    with open('backend.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and fix the logger issue
    fixed_lines = []
    logger_defined = False
    historical_block_start = -1
    
    for i, line in enumerate(lines):
        # Check if we found the logger definition
        if 'logging.basicConfig' in line:
            logger_defined = True
        
        # Check if we found the Historical Data Manager import
        if '# Import Historical Data Manager' in line:
            historical_block_start = i
        
        # If we found the historical block but logger isn't defined yet
        if historical_block_start > 0 and not logger_defined:
            # Insert logger configuration before Historical Data Manager
            if '# Import Historical Data Manager' in line:
                fixed_lines.append('# Configure logging (moved up to fix NameError)\n')
                fixed_lines.append('logging.basicConfig(level=logging.INFO)\n')
                fixed_lines.append('logger = logging.getLogger(__name__)\n')
                fixed_lines.append('\n')
            
        fixed_lines.append(line)
        
        # Skip the duplicate logger configuration later
        if historical_block_start > 0 and logger_defined and 'Configure logging' in line:
            # Skip the next 2 lines (the duplicate logger config)
            next(lines)
            next(lines)
    
    # Write the fixed file
    with open('backend.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed backend.py successfully!")
    print("You can now run: python backend.py")

if __name__ == "__main__":
    try:
        fix_backend()
    except Exception as e:
        print(f"Error: {e}")
        print("\nManual fix instructions:")
        print("1. Open backend.py in a text editor")
        print("2. Find the line: # Configure logging")
        print("3. Move these 2 lines BEFORE '# Import Historical Data Manager':")
        print("   logging.basicConfig(level=logging.INFO)")
        print("   logger = logging.getLogger(__name__)")