"""
v186.1 UI ENHANCEMENT PATCH
============================

Converts confidence threshold slider to a text input box for precise control.

This patch modifies the dashboard to replace the slider with a numeric text input,
allowing you to type exact threshold values (e.g., 48.5, 52.3, etc.)

Usage:
    python APPLY_UI_TEXT_INPUT_PATCH.py

Requirements:
    - v186 hotfix already applied
    - Dashboard file: unified_trading_dashboard.py (or dashboard.py)
"""

import os
import sys
import re
import shutil
from pathlib import Path


def find_dashboard_file(base_dir):
    """Find the main dashboard file"""
    candidates = [
        'unified_trading_dashboard.py',
        'dashboard.py',
        'regime_dashboard.py',
        'paper_trading_dashboard.py'
    ]
    
    for candidate in candidates:
        path = os.path.join(base_dir, candidate)
        if os.path.exists(path):
            return path
    
    return None


def backup_file(filepath):
    """Create a backup of the file"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.v186_1_backup"
        shutil.copy2(filepath, backup_path)
        print(f"✓ Backed up: {filepath} -> {backup_path}")
        return True
    else:
        print(f"✗ File not found: {filepath}")
        return False


def convert_slider_to_input(dashboard_path):
    """Convert confidence threshold slider to text input"""
    
    # Backup first
    backup_file(dashboard_path)
    
    # Read file
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: Look for dcc.Slider with confidence/threshold in the id
    slider_pattern = r'dcc\.Slider\s*\(\s*id\s*=\s*[\'"]([^\'\"]*confidence[^\'\"]*)[\'\"].*?\)'
    
    # Pattern 2: Look for common slider patterns
    patterns_to_replace = [
        # Pattern: dcc.Slider(id='confidence-threshold', ...)
        (
            r'dcc\.Slider\s*\(\s*'
            r'id\s*=\s*[\'"]confidence-threshold[\'"],\s*'
            r'min\s*=\s*(\d+),\s*'
            r'max\s*=\s*(\d+),\s*'
            r'step\s*=\s*([0-9.]+),\s*'
            r'value\s*=\s*([0-9.]+)(?:,\s*'
            r'marks\s*=\s*\{[^}]+\})?'
            r'\s*\)',
            lambda m: (
                f"dcc.Input(\n"
                f"                    id='confidence-threshold',\n"
                f"                    type='number',\n"
                f"                    min={m.group(1)},\n"
                f"                    max={m.group(2)},\n"
                f"                    step={m.group(3)},\n"
                f"                    value={m.group(4)},\n"
                f"                    style={{'width': '100px', 'padding': '5px', 'fontSize': '16px'}}\n"
                f"                )"
            )
        ),
        
        # Pattern: dcc.Slider(id='threshold-slider', ...)
        (
            r'dcc\.Slider\s*\(\s*'
            r'id\s*=\s*[\'"]threshold-slider[\'"],\s*'
            r'min\s*=\s*(\d+),\s*'
            r'max\s*=\s*(\d+),\s*'
            r'step\s*=\s*([0-9.]+),\s*'
            r'value\s*=\s*([0-9.]+)(?:,\s*'
            r'marks\s*=\s*\{[^}]+\})?'
            r'\s*\)',
            lambda m: (
                f"dcc.Input(\n"
                f"                    id='threshold-slider',\n"
                f"                    type='number',\n"
                f"                    min={m.group(1)},\n"
                f"                    max={m.group(2)},\n"
                f"                    step={m.group(3)},\n"
                f"                    value={m.group(4)},\n"
                f"                    style={{'width': '100px', 'padding': '5px', 'fontSize': '16px'}}\n"
                f"                )"
            )
        ),
        
        # Generic pattern for any slider with 'confidence' or 'threshold' in id
        (
            r'dcc\.Slider\s*\(\s*'
            r'id\s*=\s*[\'"]([^\'\"]*(?:confidence|threshold)[^\'\"]*)[\'\"],\s*'
            r'min\s*=\s*(\d+),\s*'
            r'max\s*=\s*(\d+),\s*'
            r'step\s*=\s*([0-9.]+),\s*'
            r'value\s*=\s*([0-9.]+)(?:,\s*'
            r'marks\s*=\s*\{[^}]+\})?'
            r'\s*\)',
            lambda m: (
                f"dcc.Input(\n"
                f"                    id='{m.group(1)}',\n"
                f"                    type='number',\n"
                f"                    min={m.group(2)},\n"
                f"                    max={m.group(3)},\n"
                f"                    step={m.group(4)},\n"
                f"                    value={m.group(5)},\n"
                f"                    style={{'width': '100px', 'padding': '5px', 'fontSize': '16px'}}\n"
                f"                )"
            )
        )
    ]
    
    # Try to apply patterns
    modified = False
    for pattern, replacement in patterns_to_replace:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            modified = True
            print(f"✓ Converted slider to text input using pattern")
            break
    
    if not modified:
        print("⚠ Could not automatically detect slider pattern")
        print("Please see MANUAL_UI_PATCH_GUIDE.md for manual instructions")
        return False
    
    # Write back
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Dashboard updated: {dashboard_path}")
    return True


def create_manual_guide(base_dir):
    """Create manual patching guide if automatic fails"""
    guide_path = os.path.join(base_dir, "MANUAL_UI_PATCH_GUIDE.md")
    
    guide_content = """# MANUAL UI PATCH GUIDE - Text Input Conversion

If the automatic patch didn't work, follow these steps to manually convert the slider to a text input box.

## Step 1: Find the Slider Code

Open your dashboard file (unified_trading_dashboard.py or dashboard.py) and search for:

```python
dcc.Slider(
    id='confidence-threshold',  # or similar id
    min=0,
    max=100,
    step=1,
    value=48,
    marks={...}
)
```

## Step 2: Replace with Text Input

Replace the entire `dcc.Slider(...)` block with:

```python
dcc.Input(
    id='confidence-threshold',  # Keep same id as before!
    type='number',
    min=0,
    max=100,
    step=0.1,  # Allows decimals like 48.5
    value=48,
    style={'width': '100px', 'padding': '5px', 'fontSize': '16px'}
)
```

## Step 3: Add Label (Optional but Recommended)

Add a label before the input:

```python
html.Label("Confidence Threshold (%):"),
dcc.Input(
    id='confidence-threshold',
    type='number',
    min=0,
    max=100,
    step=0.1,
    value=48,
    style={'width': '100px', 'padding': '5px', 'fontSize': '16px'}
)
```

## Step 4: Verify

Save the file and restart the dashboard. You should now see a text input box instead of a slider.

## Benefits of Text Input

- ✅ Type exact values (e.g., 48.5, 52.3)
- ✅ Faster to set specific values
- ✅ More precise control
- ✅ No need to drag slider

## Example Values to Try

- **48** - Default (recommended)
- **45** - More trades (higher risk)
- **52** - Moderate filtering
- **55** - Conservative
- **60** - Very conservative
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✓ Created manual guide: {guide_path}")


def main():
    print("="*60)
    print("v186.1 UI ENHANCEMENT PATCH")
    print("Convert Confidence Threshold Slider → Text Input")
    print("="*60)
    print()
    
    # Detect directory
    current_dir = os.getcwd()
    
    # Find dashboard file
    dashboard_path = find_dashboard_file(current_dir)
    
    if not dashboard_path:
        print("✗ Could not find dashboard file")
        print()
        print("Expected files:")
        print("  - unified_trading_dashboard.py")
        print("  - dashboard.py")
        print("  - regime_dashboard.py")
        print()
        print("Please run this script from your trading system root directory")
        sys.exit(1)
    
    print(f"✓ Found dashboard: {dashboard_path}")
    print()
    print("This will convert the confidence threshold slider to a text input box")
    print("Benefits:")
    print("  - Type exact values (e.g., 48.5, 52.3)")
    print("  - More precise control")
    print("  - Faster to set specific values")
    print()
    print("Backup will be created: .v186_1_backup")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Aborted.")
        sys.exit(0)
    
    print()
    print("Applying UI patch...")
    print("-"*60)
    
    # Apply patch
    success = convert_slider_to_input(dashboard_path)
    
    # Create manual guide
    create_manual_guide(current_dir)
    
    print()
    print("="*60)
    if success:
        print("✓ UI PATCH APPLIED SUCCESSFULLY")
        print("="*60)
        print()
        print("Next steps:")
        print("  1. Restart your dashboard")
        print("  2. Open http://localhost:8050")
        print("  3. Look for confidence threshold text input box")
        print("  4. Type exact values (e.g., 48, 48.5, 52.3)")
        print()
        print("To rollback:")
        print(f"  Copy-Item \"{dashboard_path}.v186_1_backup\" -Destination \"{dashboard_path}\" -Force")
        print()
    else:
        print("⚠ AUTOMATIC PATCH FAILED")
        print("="*60)
        print()
        print("Please follow manual instructions in:")
        print("  MANUAL_UI_PATCH_GUIDE.md")
        print()
        print("Or share your dashboard file for a custom patch.")
        sys.exit(1)


if __name__ == "__main__":
    main()
