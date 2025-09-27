#!/usr/bin/env python3
"""
Create Fixed Installer Package for Stock Predictor Pro
Handles Python 3.14 compatibility issues and missing dependencies
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
import json
from datetime import datetime

def create_fixed_installer_package():
    """Create a fixed installer package with compatibility updates"""
    
    print("📦 Creating Stock Predictor Pro FIXED Installer Package")
    print("=" * 60)
    
    # Define paths
    root_dir = Path(__file__).parent
    output_dir = root_dir / "fixed_installer"
    
    # Clean and create output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    print("📁 Preparing fixed installer files...")
    
    # Files to include
    files_to_copy = [
        # Main application
        "stock_predictor_pro.py",
        "local_predictor.py",
        "local_trainer.py",
        "local_backtester.py",
        "cloud_client.py",
        
        # Fixed installation files
        "install_fixed.bat",
        "fix_dependencies.py",
        "requirements_compatible.txt",
        
        # Documentation
        "README.md",
        "DEPLOYMENT_GUIDE.md",
    ]
    
    # Copy files
    for file_name in files_to_copy:
        src = root_dir / file_name
        if src.exists():
            dst = output_dir / file_name
            shutil.copy2(src, dst)
            print(f"  ✓ {file_name}")
    
    # Create assets directory
    assets_dir = output_dir / "assets"
    assets_dir.mkdir()
    (assets_dir / "icon.ico").write_bytes(b'')  # Placeholder
    
    # Create INSTALL_INSTRUCTIONS.txt
    instructions = """
STOCK PREDICTOR PRO - INSTALLATION INSTRUCTIONS
================================================

⚠️ IMPORTANT: Python Version Compatibility ⚠️
This version is designed to work with Python 3.9, 3.10, or 3.11

If you have Python 3.14 installed:
----------------------------------
Python 3.14 is too new and causes compatibility issues with many packages.
You need to install Python 3.11 alongside it:

1. Download Python 3.11 from:
   https://www.python.org/downloads/release/python-3119/

2. During installation:
   - Check "Add Python 3.11 to PATH"
   - Choose "Install for all users"
   - Complete installation

3. After installing Python 3.11, run the fixed installer


INSTALLATION STEPS:
==================

Method 1: Automatic Installation (Recommended)
----------------------------------------------
1. Right-click on "install_fixed.bat"
2. Select "Run as Administrator"
3. The installer will:
   - Detect compatible Python version
   - Create virtual environment
   - Install all dependencies
   - Create shortcuts

Method 2: Fix Dependencies First
---------------------------------
1. Open Command Prompt as Administrator
2. Navigate to this folder
3. Run: python fix_dependencies.py
   (This will check your Python version and install compatible packages)
4. Then run: install_fixed.bat

Method 3: Manual Installation
-----------------------------
1. Ensure Python 3.9, 3.10, or 3.11 is installed
2. Open Command Prompt in this folder
3. Create virtual environment:
   python3.11 -m venv venv
   
4. Activate environment:
   venv\Scripts\activate
   
5. Install dependencies:
   pip install -r requirements_compatible.txt
   
6. Run the application:
   python stock_predictor_pro.py


TROUBLESHOOTING:
===============

Issue: "pandas-ta not found"
Solution: This package has compatibility issues. The app uses 'ta' library instead.

Issue: Desktop shortcut not created
Solution: Manually create shortcut to launch.bat in installation folder

Issue: Some packages fail to install
Solution: Run fix_dependencies.py to install compatible versions

Issue: Application won't start
Solution: Check that you're using Python 3.9-3.11, not 3.14


AFTER INSTALLATION:
==================
1. Launch from desktop shortcut or Start Menu
2. Configure cloud API connection (optional)
3. Start with a simple prediction
4. Check Help menu for user guide


SUPPORT:
========
- Run fix_dependencies.py for dependency issues
- Check DEPLOYMENT_GUIDE.md for detailed instructions
- Email: support@stockpredictorpro.com


Thank you for choosing Stock Predictor Pro!
"""
    
    instructions_file = output_dir / "INSTALL_INSTRUCTIONS.txt"
    instructions_file.write_text(instructions)
    print("  ✓ Created INSTALL_INSTRUCTIONS.txt")
    
    # Create launch.bat
    launch_script = """@echo off
echo Starting Stock Predictor Pro...
cd /d "%~dp0"
if exist venv (
    call venv\\Scripts\\activate.bat
    python stock_predictor_pro.py
) else (
    echo Virtual environment not found!
    echo Please run install_fixed.bat first
    pause
)
"""
    
    (output_dir / "launch.bat").write_text(launch_script)
    print("  ✓ Created launch.bat")
    
    # Create test_installation.py
    test_script = '''#!/usr/bin/env python3
"""Test if installation is working correctly"""

import sys
print(f"Python version: {sys.version}")
print("-" * 40)

packages = [
    ("numpy", "Numerical computing"),
    ("pandas", "Data processing"),
    ("customtkinter", "GUI framework"),
    ("sklearn", "Machine learning"),
    ("xgboost", "XGBoost ML"),
    ("yfinance", "Financial data"),
    ("requests", "HTTP requests"),
    ("ta", "Technical analysis"),
]

print("Checking installed packages:")
for package, description in packages:
    try:
        __import__(package)
        print(f"✅ {description} ({package})")
    except ImportError:
        print(f"❌ {description} ({package}) - NOT INSTALLED")

print("-" * 40)
print("\\nTest complete!")
input("\\nPress Enter to exit...")
'''
    
    (output_dir / "test_installation.py").write_text(test_script)
    print("  ✓ Created test_installation.py")
    
    # Create the ZIP package
    print("\n🗜️ Creating ZIP package...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = f"StockPredictorPro_FIXED_Installer_{timestamp}.zip"
    zip_path = root_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(output_dir)
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")
    
    # Get package size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    # Clean up temporary directory
    shutil.rmtree(output_dir)
    
    print("\n" + "=" * 60)
    print("✅ FIXED Installer Package Created Successfully!")
    print(f"📦 Package: {zip_name}")
    print(f"📁 Location: {zip_path}")
    print(f"💾 Size: {size_mb:.2f} MB")
    print("\n📋 Key Features of Fixed Version:")
    print("  • Handles Python 3.14 compatibility issues")
    print("  • Uses alternative to pandas-ta")
    print("  • Better error handling for shortcuts")
    print("  • Includes dependency fixer script")
    print("  • Compatible requirements file")
    print("\n🚀 Ready for use with Python version issues resolved!")
    
    return zip_path

if __name__ == "__main__":
    package_path = create_fixed_installer_package()
    print(f"\n✅ Use this package: {package_path.name}")
    print("This version will work with your Python 3.9 installation!")