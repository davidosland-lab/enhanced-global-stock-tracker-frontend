#!/usr/bin/env python3
"""
Build script for creating Windows installer package
Handles PyInstaller bundling and NSIS installer creation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json
import zipfile
import argparse
from datetime import datetime

class InstallerBuilder:
    """Handles the complete build process for Windows installer"""
    
    def __init__(self, version="1.0.0"):
        self.version = version
        self.root_dir = Path(__file__).parent
        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"
        self.output_dir = self.root_dir / "output"
        
    def clean_build_dirs(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning build directories...")
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def create_pyinstaller_spec(self):
        """Create PyInstaller spec file for building executable"""
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['stock_predictor_pro.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('models', 'models'),
        ('config', 'config'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'sklearn.utils._typedefs',
        'sklearn.utils._heap',
        'sklearn.utils._sorting',
        'sklearn.utils._vector_sentinel',
        'sklearn.neighbors._partition_nodes',
        'sklearn.metrics._pairwise_distances_reduction._datasets_pair',
        'sklearn.metrics._pairwise_distances_reduction._middle_term_computer',
        'customtkinter',
        'PIL._tkinter_finder',
        'tensorflow',
        'torch',
        'xgboost',
        'lightgbm',
        'catboost',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'pytest', 'ipython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StockPredictorPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    version_file='version_info.txt',
    uac_admin=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StockPredictorPro',
)
'''
        spec_file = self.root_dir / "StockPredictorPro.spec"
        spec_file.write_text(spec_content.strip())
        print(f"✅ Created PyInstaller spec file: {spec_file}")
        return spec_file
        
    def create_version_info(self):
        """Create version info file for Windows executable"""
        version_info = f'''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({self.version.replace(".", ", ")}, 0),
    prodvers=({self.version.replace(".", ", ")}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [
          StringStruct(u'CompanyName', u'Stock Predictor Team'),
          StringStruct(u'FileDescription', u'AI-Powered Stock Prediction System'),
          StringStruct(u'FileVersion', u'{self.version}'),
          StringStruct(u'InternalName', u'StockPredictorPro'),
          StringStruct(u'LegalCopyright', u'Copyright © 2024 Stock Predictor Team'),
          StringStruct(u'OriginalFilename', u'StockPredictorPro.exe'),
          StringStruct(u'ProductName', u'Stock Predictor Pro'),
          StringStruct(u'ProductVersion', u'{self.version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        version_file = self.root_dir / "version_info.txt"
        version_file.write_text(version_info.strip())
        print(f"✅ Created version info file: {version_file}")
        return version_file
        
    def create_batch_scripts(self):
        """Create batch scripts for installation and setup"""
        
        # Install dependencies batch script
        install_deps = '''@echo off
echo Installing Stock Predictor Pro dependencies...
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\\Scripts\\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install some dependencies
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully!
echo.
pause
'''
        
        # Run application batch script
        run_app = '''@echo off
REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Running install_deps.bat...
    call install_deps.bat
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Run the application
python stock_predictor_pro.py

pause
'''
        
        # Create files
        (self.dist_dir / "install_deps.bat").write_text(install_deps)
        (self.dist_dir / "run_app.bat").write_text(run_app)
        print("✅ Created batch scripts")
        
    def build_executable(self):
        """Build executable using PyInstaller"""
        print("🔨 Building executable with PyInstaller...")
        
        spec_file = self.create_pyinstaller_spec()
        version_file = self.create_version_info()
        
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        try:
            subprocess.run(cmd, check=True, cwd=self.root_dir)
            print("✅ Executable built successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build executable: {e}")
            return False
        
        return True
        
    def copy_additional_files(self):
        """Copy additional files to distribution directory"""
        print("📁 Copying additional files...")
        
        files_to_copy = [
            "requirements.txt",
            "README.md",
            "LICENSE",
            "stock_predictor_pro.py",
            "local_predictor.py",
            "local_trainer.py",
            "local_backtester.py",
            "cloud_client.py",
        ]
        
        for file in files_to_copy:
            src = self.root_dir / file
            if src.exists():
                dst = self.dist_dir / "StockPredictorPro" / file
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  ✓ Copied {file}")
        
        # Create assets directory
        assets_dir = self.dist_dir / "StockPredictorPro" / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Create default icon if not exists
        icon_path = assets_dir / "icon.ico"
        if not icon_path.exists():
            # Create a placeholder icon file
            icon_path.write_bytes(b'')
            
        self.create_batch_scripts()
        
    def build_nsis_installer(self):
        """Build NSIS installer"""
        print("📦 Building NSIS installer...")
        
        nsis_script = self.root_dir / "installer.nsi"
        
        # Check if NSIS is installed
        nsis_path = r"C:\Program Files (x86)\NSIS\makensis.exe"
        if not Path(nsis_path).exists():
            nsis_path = r"C:\Program Files\NSIS\makensis.exe"
            if not Path(nsis_path).exists():
                print("⚠️  NSIS not found. Please install NSIS from https://nsis.sourceforge.io")
                return False
        
        # Run NSIS
        cmd = [nsis_path, "/V2", str(nsis_script)]
        
        try:
            subprocess.run(cmd, check=True, cwd=self.root_dir)
            print("✅ NSIS installer created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to create NSIS installer: {e}")
            return False
        
    def create_portable_zip(self):
        """Create portable ZIP package"""
        print("🗜️ Creating portable ZIP package...")
        
        zip_name = f"StockPredictorPro_Portable_v{self.version}.zip"
        zip_path = self.output_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from dist directory
            dist_path = self.dist_dir / "StockPredictorPro"
            if dist_path.exists():
                for file_path in dist_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.dist_dir)
                        zipf.write(file_path, arcname)
        
        print(f"✅ Created portable package: {zip_path}")
        return zip_path
        
    def create_installer_package(self):
        """Create the complete installer package"""
        print(f"🚀 Building Stock Predictor Pro Installer v{self.version}")
        print("=" * 60)
        
        # Clean build directories
        self.clean_build_dirs()
        
        # Copy source files first
        self.copy_additional_files()
        
        # Build executable
        if not self.build_executable():
            print("❌ Build failed!")
            return False
        
        # Copy additional files after build
        self.copy_additional_files()
        
        # Try to build NSIS installer
        nsis_success = self.build_nsis_installer()
        
        # Create portable ZIP
        zip_path = self.create_portable_zip()
        
        print("\n" + "=" * 60)
        print("✅ Build completed successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        
        if nsis_success:
            print(f"📦 Installer: StockPredictorPro_Setup_v{self.version}.exe")
        else:
            print("⚠️  NSIS installer not created (NSIS not installed)")
        
        print(f"🗜️ Portable package: {zip_path.name}")
        
        return True

def main():
    """Main entry point for build script"""
    parser = argparse.ArgumentParser(description="Build Stock Predictor Pro installer")
    parser.add_argument("--version", default="1.0.0", help="Version number")
    parser.add_argument("--skip-exe", action="store_true", help="Skip executable build")
    parser.add_argument("--portable-only", action="store_true", help="Create portable ZIP only")
    
    args = parser.parse_args()
    
    builder = InstallerBuilder(version=args.version)
    
    if args.portable_only:
        builder.clean_build_dirs()
        builder.copy_additional_files()
        builder.create_portable_zip()
    else:
        builder.create_installer_package()

if __name__ == "__main__":
    main()