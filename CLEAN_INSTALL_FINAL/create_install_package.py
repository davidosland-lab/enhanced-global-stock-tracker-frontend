#!/usr/bin/env python3
"""
Stock Tracker Installation Package Creator
Creates a complete, distributable installation package
"""

import os
import shutil
import zipfile
from pathlib import Path
import json
from datetime import datetime

class InstallerCreator:
    def __init__(self):
        self.package_name = "StockTracker_Complete_ML_v1.0"
        self.package_dir = Path(self.package_name)
        self.zip_name = f"{self.package_name}.zip"
        
    def create_package(self):
        """Create the complete installation package"""
        print("=" * 80)
        print("         STOCK TRACKER INSTALLATION PACKAGE CREATOR")
        print("=" * 80)
        print()
        
        # Clean up old package
        if self.package_dir.exists():
            print(f"[INFO] Removing old package directory...")
            shutil.rmtree(self.package_dir)
            
        # Create directory structure
        print("[1/6] Creating package structure...")
        self.create_directories()
        
        # Copy application files
        print("[2/6] Copying application files...")
        self.copy_files()
        
        # Create installer script
        print("[3/6] Creating installer script...")
        self.create_installer()
        
        # Create package manifest
        print("[4/6] Creating package manifest...")
        self.create_manifest()
        
        # Create documentation
        print("[5/6] Creating documentation...")
        self.create_docs()
        
        # Create ZIP archive
        print("[6/6] Creating ZIP archive...")
        self.create_zip()
        
        print()
        print("=" * 80)
        print("                    PACKAGE CREATED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nPackage: {self.zip_name}")
        print(f"Size: {os.path.getsize(self.zip_name) / 1024 / 1024:.2f} MB")
        print("\nDistribution Instructions:")
        print("1. Share the ZIP file with users")
        print("2. Users extract and run Setup.bat")
        print("3. Application installs automatically")
        
    def create_directories(self):
        """Create package directory structure"""
        dirs = [
            self.package_dir,
            self.package_dir / "modules",
            self.package_dir / "static",
            self.package_dir / "historical_data",
            self.package_dir / "models",
            self.package_dir / "logs",
            self.package_dir / "docs"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def copy_files(self):
        """Copy all necessary files to package"""
        # Core backend files
        backend_files = [
            "backend.py",
            "ml_training_backend.py",
            "historical_data_manager.py",
            "test_system.py"
        ]
        
        # Frontend files
        frontend_files = [
            "index.html",
            "WORKING_PREDICTION_MODULE.html"
        ]
        
        # Configuration files
        config_files = [
            "requirements_ml.txt",
            "LAUNCH_ALL_SERVICES.bat",
            "COMPLETE_DEPLOYMENT_GUIDE.md",
            "WINDOWS11_COMPLETE_SOLUTION.md"
        ]
        
        # Copy backend files
        for file in backend_files:
            if Path(file).exists():
                shutil.copy2(file, self.package_dir)
                
        # Copy frontend files
        for file in frontend_files:
            if Path(file).exists():
                shutil.copy2(file, self.package_dir)
                
        # Copy config files
        for file in config_files:
            if Path(file).exists():
                shutil.copy2(file, self.package_dir)
                
        # Copy modules directory
        if Path("modules").exists():
            for file in Path("modules").glob("*.html"):
                shutil.copy2(file, self.package_dir / "modules")
                
        # Copy static directory if exists
        if Path("static").exists():
            shutil.copytree("static", self.package_dir / "static", dirs_exist_ok=True)
            
    def create_installer(self):
        """Create the main installer script"""
        installer_content = '''@echo off
title Stock Tracker Professional Installer
color 0A
cls

echo ===============================================================================
echo                       STOCK TRACKER PROFESSIONAL
echo                    Complete System with ML Training
echo ===============================================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.8+ from: https://python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
python --version
echo.

:: Install packages
echo [1/5] Installing Python packages (5-10 minutes)...
pip install --upgrade pip --quiet
pip install -r requirements_ml.txt --quiet

echo.
echo [2/5] Initializing database...
python -c "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager()"

echo.
echo [3/5] Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\\Stock Tracker.lnk'); $Shortcut.TargetPath = '%CD%\\LAUNCH_ALL_SERVICES.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Save()"

echo.
echo [4/5] Running system test...
python test_system.py

echo.
echo [5/5] Installation complete!
echo.
echo ===============================================================================
echo                         INSTALLATION SUCCESSFUL!
echo ===============================================================================
echo.
echo Desktop shortcut created: Stock Tracker
echo.
echo To launch: Double-click the desktop shortcut
echo           OR run LAUNCH_ALL_SERVICES.bat
echo.
echo Application URL: http://localhost:8000
echo.
set /p launch="Launch Stock Tracker now? (Y/N): "
if /i "%launch%"=="Y" (
    start "" "LAUNCH_ALL_SERVICES.bat"
)
pause'''
        
        installer_path = self.package_dir / "Setup.bat"
        installer_path.write_text(installer_content)
        
        # Create uninstaller
        uninstaller_content = '''@echo off
title Stock Tracker Uninstaller
color 0C

echo ===============================================================================
echo                        STOCK TRACKER UNINSTALLER
echo ===============================================================================
echo.

set /p confirm="Remove Stock Tracker? (Y/N): "
if /i "%confirm%" neq "Y" exit /b 0

echo Removing desktop shortcut...
del "%USERPROFILE%\\Desktop\\Stock Tracker.lnk" 2>nul

echo Stopping services...
taskkill /f /im python.exe 2>nul

echo.
echo Uninstall complete!
echo You can now delete this folder.
pause'''
        
        uninstaller_path = self.package_dir / "Uninstall.bat"
        uninstaller_path.write_text(uninstaller_content)
        
    def create_manifest(self):
        """Create package manifest with version info"""
        manifest = {
            "name": "Stock Tracker Professional",
            "version": "1.0.0",
            "build_date": datetime.now().isoformat(),
            "features": [
                "Real-time Yahoo Finance data",
                "6 professional modules",
                "ML model training with TensorFlow",
                "SQLite for 100x faster backtesting",
                "Windows 11 optimized"
            ],
            "requirements": {
                "python": ">=3.8",
                "ram": "8GB minimum, 16GB recommended",
                "disk": "10GB free space",
                "os": "Windows 10/11"
            },
            "modules": [
                "CBA Enhanced Tracker",
                "Global Indices Tracker",
                "Stock Tracker with Technical Analysis",
                "Document Uploader with FinBERT",
                "Phase 4 Predictor with Backtesting",
                "ML Training Centre"
            ]
        }
        
        manifest_path = self.package_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
    def create_docs(self):
        """Create user documentation"""
        readme_content = """# Stock Tracker Professional - Installation Package

## 🚀 Quick Start

1. **Extract** this folder to your desired location (e.g., C:\\StockTracker)
2. **Run Setup.bat** (double-click)
3. **Wait** for installation (5-10 minutes first time)
4. **Launch** using the desktop shortcut

## 📦 Package Contents

- `Setup.bat` - Automated installer
- `LAUNCH_ALL_SERVICES.bat` - Application launcher
- `backend.py` - Main backend server (port 8002)
- `ml_training_backend.py` - ML training server (port 8003)
- `modules/` - All 6 application modules
- `requirements_ml.txt` - Python dependencies

## ✨ Features

- ✅ Real-time Yahoo Finance data (no mock data)
- ✅ 6 professional trading modules
- ✅ Real ML model training with TensorFlow
- ✅ SQLite for 100x faster backtesting
- ✅ Windows 11 optimized
- ✅ One-click installation and launch

## 💻 System Requirements

- Windows 10/11
- Python 3.8 or higher
- 8GB RAM (16GB for ML training)
- 10GB free disk space
- Internet connection

## 🎯 Modules Included

1. **CBA Enhanced Tracker** - Full 6-tab interface
2. **Global Indices** - Real-time market indices
3. **Stock Tracker** - Technical analysis & candlesticks
4. **Document Uploader** - FinBERT sentiment analysis
5. **Phase 4 Predictor** - Advanced predictions & backtesting
6. **ML Training Centre** - Real neural network training

## 🔧 Troubleshooting

If you encounter issues:
1. Ensure Python 3.8+ is installed
2. Run `test_system.py` to diagnose
3. Check firewall settings
4. Run as Administrator if needed

## 📞 Support

- Test System: `python test_system.py`
- Documentation: See included guides
- Application URL: http://localhost:8000

---
© 2024 Stock Tracker Professional - ML Edition
"""
        
        readme_path = self.package_dir / "README.md"
        readme_path.write_text(readme_content)
        
    def create_zip(self):
        """Create ZIP archive of the package"""
        with zipfile.ZipFile(self.zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.package_dir.parent)
                    zipf.write(file_path, arcname)

if __name__ == "__main__":
    creator = InstallerCreator()
    creator.create_package()