#!/usr/bin/env python3
"""
Create a foolproof installation package that handles all edge cases
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def create_foolproof_package():
    """Create the most reliable package possible"""
    
    print("📦 Creating Foolproof Stock Predictor Pro Package")
    print("=" * 60)
    
    # Define paths
    root_dir = Path(__file__).parent
    package_dir = root_dir / "foolproof_package"
    
    # Clean and create directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print("📁 Assembling foolproof package...")
    
    # Critical files
    critical_files = [
        "stock_predictor_lite.py",  # The lite version that always works
        "test_simple.py",            # Test Python installation
        "PORTABLE_RUN.bat",          # Fixed portable runner
        "RUN_DIRECTLY_FIXED.bat",    # Fixed direct runner
        "MUST_READ_FIRST.txt",       # Clear instructions
    ]
    
    # Copy critical files
    for filename in critical_files:
        src = root_dir / filename
        if src.exists():
            dst = package_dir / filename
            shutil.copy2(src, dst)
            print(f"  ✓ {filename}")
    
    # Create a super simple runner
    super_simple = '''@echo off
echo Stock Predictor Pro - Super Simple Launcher
echo.
cd /d "%~dp0"
python stock_predictor_lite.py
if errorlevel 1 py stock_predictor_lite.py
if errorlevel 1 python3 stock_predictor_lite.py  
if errorlevel 1 (
    echo.
    echo Could not start. Please install Python from python.org
    echo Then try again.
    pause
)
'''
    
    (package_dir / "CLICK_ME_TO_RUN.bat").write_text(super_simple)
    print("  ✓ Created CLICK_ME_TO_RUN.bat")
    
    # Create install-to-desktop script
    desktop_installer = '''@echo off
echo Installing to Desktop...
set DESKTOP=%USERPROFILE%\\Desktop\\StockPredictorPro
mkdir "%DESKTOP%" 2>nul
xcopy /Y /E /I *.* "%DESKTOP%\\"
echo.
echo ✓ Installed to Desktop\\StockPredictorPro
echo.
echo Now go to your Desktop, open StockPredictorPro folder,
echo and double-click CLICK_ME_TO_RUN.bat
echo.
pause
'''
    
    (package_dir / "INSTALL_TO_DESKTOP.bat").write_text(desktop_installer)
    print("  ✓ Created INSTALL_TO_DESKTOP.bat")
    
    # Optional files (nice to have but not critical)
    optional_files = [
        "stock_predictor_pro.py",
        "local_predictor.py",
        "local_trainer.py",
        "local_backtester.py",
        "cloud_client.py",
        "requirements_compatible.txt",
        "fix_dependencies.py",
    ]
    
    for filename in optional_files:
        src = root_dir / filename
        if src.exists():
            dst = package_dir / filename
            shutil.copy2(src, dst)
            print(f"  + {filename} (optional)")
    
    # Create README
    readme = """
STOCK PREDICTOR PRO - FOOLPROOF EDITION
========================================

This package is designed to work no matter what!

HOW TO USE:
-----------
1. Extract ALL files from this ZIP (important!)
2. Double-click: CLICK_ME_TO_RUN.bat
3. That's it!

IF IT DOESN'T WORK:
-------------------
1. Install Python from python.org
2. Try again

ALTERNATIVE METHODS:
-------------------
• INSTALL_TO_DESKTOP.bat - Copies everything to Desktop
• PORTABLE_RUN.bat - Searches for Python everywhere  
• test_simple.py - Tests if Python works

The LITE version (stock_predictor_lite.py) needs:
- Only Python (no extra packages)
- Works on any Windows PC with Python

© 2024 Stock Predictor Team
"""
    
    (package_dir / "README.txt").write_text(readme)
    print("  ✓ Created README.txt")
    
    # Create the ZIP
    print("\n🗜️ Creating foolproof ZIP package...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = f"StockPredictorPro_FOOLPROOF_{timestamp}.zip"
    zip_path = root_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(package_dir)
    
    # Get size
    size_kb = zip_path.stat().st_size / 1024
    
    print("\n" + "=" * 60)
    print("✅ FOOLPROOF Package Created!")
    print(f"📦 File: {zip_name}")
    print(f"💾 Size: {size_kb:.1f} KB")
    print("\n🎯 This package:")
    print("  • Works from any location")
    print("  • Handles all path issues")
    print("  • Includes Desktop installer")
    print("  • Multiple fallback methods")
    print("  • Clear instructions")
    print("\n📋 Tell user to:")
    print("  1. Extract the ZIP completely")
    print("  2. Click: CLICK_ME_TO_RUN.bat")
    print("=" * 60)
    
    return zip_path

if __name__ == "__main__":
    create_foolproof_package()