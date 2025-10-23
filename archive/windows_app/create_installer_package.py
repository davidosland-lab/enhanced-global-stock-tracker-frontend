#!/usr/bin/env python3
"""
Create a complete installer package for Stock Predictor Pro
This script creates a distributable ZIP file with all necessary components
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
import json
from datetime import datetime

def create_installer_package():
    """Create a complete installer package"""
    
    print("📦 Creating Stock Predictor Pro Installer Package")
    print("=" * 60)
    
    # Define paths
    root_dir = Path(__file__).parent
    output_dir = root_dir / "installer_package"
    
    # Clean and create output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # Files to include
    files_to_copy = [
        # Main application
        "stock_predictor_pro.py",
        "local_predictor.py",
        "local_trainer.py",
        "local_backtester.py",
        "cloud_client.py",
        
        # Configuration and requirements
        "requirements.txt",
        "README.md",
        
        # Installation scripts
        "install.bat",
        "Install-StockPredictor.ps1",
        
        # Setup files
        "setup.py",
        "build_installer.py",
    ]
    
    # Copy files
    print("\n📁 Copying application files...")
    for file_name in files_to_copy:
        src = root_dir / file_name
        if src.exists():
            dst = output_dir / file_name
            shutil.copy2(src, dst)
            print(f"  ✓ {file_name}")
        else:
            print(f"  ⚠ {file_name} not found")
    
    # Create assets directory
    assets_dir = output_dir / "assets"
    assets_dir.mkdir()
    
    # Create a simple icon placeholder (you would use a real .ico file)
    icon_path = assets_dir / "icon.ico"
    icon_path.write_bytes(b'')  # Placeholder
    print("  ✓ Created assets directory")
    
    # Create config directory
    config_dir = output_dir / "config"
    config_dir.mkdir()
    
    # Create default configuration
    default_config = {
        "version": "1.0.0",
        "cloud_api": "https://8000-default.e2b.dev",
        "theme": "dark",
        "auto_sync": False,
        "cache_duration": 3600,
        "max_workers": 4,
        "gpu_enabled": False
    }
    
    config_file = config_dir / "default_config.json"
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)
    print("  ✓ Created default configuration")
    
    # Create sample data directory
    data_dir = output_dir / "sample_data"
    data_dir.mkdir()
    
    # Create LICENSE file
    license_content = """
Stock Predictor Pro - License Agreement

Copyright (c) 2024 Stock Predictor Team

This is proprietary software. All rights reserved.

For evaluation and personal use only.
Commercial use requires a license.

Contact: support@stockpredictorpro.com
"""
    
    license_file = output_dir / "LICENSE"
    license_file.write_text(license_content.strip())
    print("  ✓ Created LICENSE file")
    
    # Create QUICK_START.txt
    quick_start = """
STOCK PREDICTOR PRO - QUICK START GUIDE
========================================

INSTALLATION:
1. Right-click on "install.bat" and select "Run as Administrator"
2. Follow the installation prompts
3. Launch from desktop shortcut

ALTERNATIVE INSTALLATION:
1. Open PowerShell as Administrator
2. Run: powershell -ExecutionPolicy Bypass -File Install-StockPredictor.ps1

REQUIREMENTS:
- Windows 10 or Windows 11
- Python 3.9 or higher
- 8 GB RAM minimum
- 10 GB free disk space

FIRST RUN:
1. Launch Stock Predictor Pro
2. Go to Settings to configure
3. Connect to cloud API (optional)
4. Start with a simple prediction

SUPPORT:
- README.md for detailed documentation
- GitHub: https://github.com/stockpredictorpro
- Email: support@stockpredictorpro.com

Thank you for choosing Stock Predictor Pro!
"""
    
    quick_start_file = output_dir / "QUICK_START.txt"
    quick_start_file.write_text(quick_start.strip())
    print("  ✓ Created QUICK_START guide")
    
    # Create minimal requirements.txt if it doesn't exist
    req_file = output_dir / "requirements.txt"
    if not req_file.exists():
        minimal_requirements = """
# Minimal requirements for Stock Predictor Pro
customtkinter>=5.2.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
xgboost>=2.0.0
yfinance>=0.2.28
requests>=2.31.0
pillow>=10.0.0
"""
        req_file.write_text(minimal_requirements.strip())
        print("  ✓ Created minimal requirements.txt")
    
    # Create the ZIP package
    print("\n🗜️ Creating ZIP package...")
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"StockPredictorPro_Installer_v1.0.0_{timestamp}.zip"
    zip_path = root_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(output_dir)
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")
    
    # Get package size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print("✅ Installer Package Created Successfully!")
    print(f"📦 Package: {zip_name}")
    print(f"📁 Location: {zip_path}")
    print(f"💾 Size: {size_mb:.2f} MB")
    print("\n📋 Installation Instructions:")
    print("1. Extract the ZIP file to a folder")
    print("2. Right-click 'install.bat' and Run as Administrator")
    print("3. Follow the installation prompts")
    print("\n🚀 Ready for distribution!")
    
    # Clean up temporary directory
    shutil.rmtree(output_dir)
    
    return zip_path

def create_portable_version():
    """Create a portable version that runs without installation"""
    
    print("\n📱 Creating Portable Version...")
    print("=" * 60)
    
    root_dir = Path(__file__).parent
    portable_dir = root_dir / "portable_version"
    
    # Clean and create directory
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir()
    
    # Copy essential files
    essential_files = [
        "stock_predictor_pro.py",
        "local_predictor.py",
        "local_trainer.py", 
        "local_backtester.py",
        "cloud_client.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file_name in essential_files:
        src = root_dir / file_name
        if src.exists():
            dst = portable_dir / file_name
            shutil.copy2(src, dst)
    
    # Create portable launcher
    launcher_content = """@echo off
echo Stock Predictor Pro - Portable Version
echo ======================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\\Scripts\\activate.bat
    echo Installing dependencies...
    pip install --upgrade pip
    pip install customtkinter numpy pandas scikit-learn xgboost yfinance requests pillow
) else (
    call venv\\Scripts\\activate.bat
)

echo.
echo Launching Stock Predictor Pro...
python stock_predictor_pro.py

pause
"""
    
    launcher_file = portable_dir / "run_portable.bat"
    launcher_file.write_text(launcher_content)
    
    # Create portable ZIP
    timestamp = datetime.now().strftime("%Y%m%d")
    portable_zip = root_dir / f"StockPredictorPro_Portable_v1.0.0_{timestamp}.zip"
    
    with zipfile.ZipFile(portable_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in portable_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(portable_dir)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(portable_dir)
    
    size_mb = portable_zip.stat().st_size / (1024 * 1024)
    print(f"✅ Portable version created: {portable_zip.name}")
    print(f"💾 Size: {size_mb:.2f} MB")
    
    return portable_zip

if __name__ == "__main__":
    # Create installer package
    installer_path = create_installer_package()
    
    # Create portable version
    portable_path = create_portable_version()
    
    print("\n" + "=" * 60)
    print("🎉 All packages created successfully!")
    print(f"📦 Installer: {installer_path.name}")
    print(f"📱 Portable: {portable_path.name}")
    print("\nReady for distribution to Windows 11 users!")
    print("=" * 60)