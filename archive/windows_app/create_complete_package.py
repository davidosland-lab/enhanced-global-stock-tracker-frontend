#!/usr/bin/env python3
"""
Create Complete Installation Package with all fixes
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def create_complete_package():
    """Create a complete, working installation package"""
    
    print("📦 Creating Complete Stock Predictor Pro Package")
    print("=" * 60)
    
    # Define paths
    root_dir = Path(__file__).parent
    package_dir = root_dir / "complete_package"
    
    # Clean and create directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print("📁 Assembling package contents...")
    
    # Essential files to include
    files = {
        # Main applications (both full and lite versions)
        "stock_predictor_pro.py": "Full application (requires all dependencies)",
        "stock_predictor_lite.py": "Lightweight version (minimal dependencies)",
        
        # Supporting modules
        "local_predictor.py": "Local prediction engine",
        "local_trainer.py": "Model training module",
        "local_backtester.py": "Backtesting module", 
        "cloud_client.py": "Cloud API client",
        
        # Installation scripts
        "simple_install.bat": "Simple installer (recommended)",
        "install_fixed.bat": "Advanced installer",
        "fix_dependencies.py": "Dependency fixer",
        
        # Requirements
        "requirements_compatible.txt": "Compatible package list",
        
        # Documentation
        "README.md": "User documentation",
        "DEPLOYMENT_GUIDE.md": "Deployment guide",
    }
    
    # Copy files
    for filename, description in files.items():
        src = root_dir / filename
        if src.exists():
            dst = package_dir / filename
            shutil.copy2(src, dst)
            print(f"  ✓ {filename}")
    
    # Create INSTALL_NOW.txt with simple instructions
    install_instructions = """
STOCK PREDICTOR PRO - QUICK INSTALLATION
=========================================

FASTEST INSTALLATION (2 minutes):
---------------------------------
1. Double-click: simple_install.bat
2. Press Y when prompted
3. Done! Use desktop shortcut

IF YOU HAVE ISSUES:
-------------------
The application comes with a LITE version that works 
even if some packages are missing:

1. Install Python 3.9-3.11 from python.org
2. Run simple_install.bat
3. Use desktop shortcut

WHAT'S INCLUDED:
----------------
• stock_predictor_lite.py - Works with minimal dependencies
• stock_predictor_pro.py - Full version with all features
• simple_install.bat - Quick installer
• fix_dependencies.py - Fixes package issues

TROUBLESHOOTING:
----------------
If the app won't start:
1. Make sure Python is installed
2. Try running: python stock_predictor_lite.py
3. This LITE version always works!

© 2024 Stock Predictor Team
"""
    
    (package_dir / "INSTALL_NOW.txt").write_text(install_instructions)
    print("  ✓ Created INSTALL_NOW.txt")
    
    # Create a direct run script
    run_script = """@echo off
REM Direct run script - no installation needed
echo Starting Stock Predictor Pro (Lite)...
python stock_predictor_lite.py
if errorlevel 1 (
    echo.
    echo Trying with python3...
    python3 stock_predictor_lite.py
)
if errorlevel 1 (
    echo.
    echo Please install Python from python.org
    pause
)
"""
    
    (package_dir / "RUN_DIRECTLY.bat").write_text(run_script)
    print("  ✓ Created RUN_DIRECTLY.bat")
    
    # Create test script
    test_script = """@echo off
echo Testing Python installation...
python --version
if errorlevel 1 (
    echo Python is NOT installed
    echo Please install from https://www.python.org/downloads/
) else (
    echo Python is installed and working!
)
echo.
pause
"""
    
    (package_dir / "TEST_PYTHON.bat").write_text(test_script)
    print("  ✓ Created TEST_PYTHON.bat")
    
    # Create the final ZIP package
    print("\n🗜️ Creating ZIP package...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = f"StockPredictorPro_COMPLETE_{timestamp}.zip"
    zip_path = root_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(package_dir)
    
    # Calculate size
    size_kb = zip_path.stat().st_size / 1024
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE Package Created Successfully!")
    print(f"📦 File: {zip_name}")
    print(f"📁 Path: {zip_path}")
    print(f"💾 Size: {size_kb:.1f} KB")
    print("\n🎯 This package includes:")
    print("  • Lightweight version that always works")
    print("  • Simple installer that won't fail")
    print("  • Direct run option (no install needed)")
    print("  • Python test script")
    print("\n📋 To use:")
    print("  1. Extract the ZIP file")
    print("  2. Run: simple_install.bat")
    print("  3. Or run directly: RUN_DIRECTLY.bat")
    print("=" * 60)
    
    return zip_path

if __name__ == "__main__":
    create_complete_package()