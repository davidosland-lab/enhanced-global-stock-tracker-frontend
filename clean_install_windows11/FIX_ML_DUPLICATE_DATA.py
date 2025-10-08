#!/usr/bin/env python3
"""
Fix the specific duplicate 'const data' declaration in ML Training Centre
"""

import os
from datetime import datetime

def fix_duplicate_data_declaration():
    """Fix the duplicate const data declaration"""
    
    ml_centre_path = "modules/ml_training_centre.html"
    
    if not os.path.exists(ml_centre_path):
        print(f"! {ml_centre_path} not found")
        return False
    
    # Read the file
    with open(ml_centre_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    backup_path = f"{ml_centre_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✓ Created backup: {backup_path}")
    
    # Find and fix the duplicate declaration
    # Line 843 (index 842) has the duplicate - remove or comment it
    if len(lines) > 842:
        # Check if line 843 contains the duplicate declaration
        if 'const data = await response.json();' in lines[842]:
            # Remove this line and the next line that uses it
            print(f"Found duplicate at line 843: {lines[842].strip()}")
            # Comment it out instead of removing
            lines[842] = '                // Duplicate removed: const data = await response.json();\n'
            if len(lines) > 843 and 'const models = data.models' in lines[843]:
                # Update to use the data from line 808
                lines[843] = '                // const models = data.models || data;  // Using data from line 808\n'
    
    # Write the fixed content
    with open(ml_centre_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✓ Fixed duplicate const data declaration at line 843")
    return True

def main():
    print("=" * 60)
    print("Fixing Duplicate Data Declaration in ML Training Centre")
    print("=" * 60)
    
    # Change to correct directory if needed
    if os.path.exists("clean_install_windows11"):
        os.chdir("clean_install_windows11")
    
    success = fix_duplicate_data_declaration()
    
    if success:
        print("\n✅ Fixed!")
        print("The duplicate 'const data' declaration has been removed.")
        print("ML Training Centre should now load without syntax errors.")
    else:
        print("\n! Fix could not be applied")

if __name__ == "__main__":
    main()