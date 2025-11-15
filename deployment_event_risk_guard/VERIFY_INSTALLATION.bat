@echo off
REM Event Risk Guard - Installation Verification Script
REM Checks if all required packages are installed correctly

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ================================================================================
echo Event Risk Guard - Installation Verification
echo ================================================================================
echo.
echo This script will verify that all required packages are installed.
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ✗ ERROR: Python not found in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)
echo.

REM Create verification script
echo Creating verification script...
(
echo import sys
echo.
echo print^("="*80^)
echo print^("PACKAGE INSTALLATION VERIFICATION"^)
echo print^("="*80^)
echo print^(^)
echo.
echo # Core packages
echo packages = {
echo     'yfinance': 'Yahoo Finance data fetching',
echo     'yahooquery': 'Yahoo Finance fallback',
echo     'pandas': 'Data manipulation',
echo     'numpy': 'Numerical computing',
echo     'requests': 'HTTP requests',
echo     'beautifulsoup4': 'HTML parsing',
echo     'lxml': 'XML/HTML parser',
echo }
echo.
echo # ML packages - FinBERT
echo ml_packages = {
echo     'torch': 'PyTorch ^(FinBERT^)',
echo     'transformers': 'Hugging Face Transformers ^(FinBERT^)',
echo }
echo.
echo # ML packages - LSTM
echo lstm_packages = {
echo     'tensorflow': 'TensorFlow ^(LSTM^)',
echo     'keras': 'Keras ^(LSTM API^)',
echo     'sklearn': 'scikit-learn ^(ML utilities^)',
echo }
echo.
echo # Technical Analysis
echo ta_packages = {
echo     'ta': 'Technical Analysis library',
echo }
echo.
echo print^("Checking Core Packages..."^)
echo print^("-"*80^)
echo installed = []
echo missing = []
echo.
echo for package, desc in packages.items^(^):
echo     try:
echo         __import__^(package^)
echo         version = ""
echo         try:
echo             mod = __import__^(package^)
echo             version = f" ^(v{mod.__version__}^)" if hasattr^(mod, '__version__'^) else ""
echo         except:
echo             pass
echo         print^(f"✓ {package:20s} {desc:40s}{version}"^)
echo         installed.append^(package^)
echo     except ImportError:
echo         print^(f"✗ {package:20s} NOT INSTALLED - {desc}"^)
echo         missing.append^(package^)
echo.
echo print^(^)
echo print^("Checking ML Packages - FinBERT ^(REQUIRED^)..."^)
echo print^("-"*80^)
echo.
echo for package, desc in ml_packages.items^(^):
echo     try:
echo         mod = __import__^(package^)
echo         version = ""
echo         try:
echo             version = f" ^(v{mod.__version__}^)" if hasattr^(mod, '__version__'^) else ""
echo         except:
echo             pass
echo         print^(f"✓ {package:20s} {desc:40s}{version}"^)
echo         installed.append^(package^)
echo     except ImportError:
echo         print^(f"✗ {package:20s} NOT INSTALLED - {desc}"^)
echo         missing.append^(package^)
echo.
echo print^(^)
echo print^("Checking ML Packages - LSTM ^(OPTIONAL^)..."^)
echo print^("-"*80^)
echo.
echo for package, desc in lstm_packages.items^(^):
echo     try:
echo         mod = __import__^(package^)
echo         version = ""
echo         try:
echo             version = f" ^(v{mod.__version__}^)" if hasattr^(mod, '__version__'^) else ""
echo         except:
echo             pass
echo         print^(f"✓ {package:20s} {desc:40s}{version}"^)
echo         installed.append^(package^)
echo     except ImportError:
echo         print^(f"⚠ {package:20s} NOT INSTALLED - {desc}"^)
echo         print^(f"  ^(LSTM predictions will not be available^)"^)
echo.
echo print^(^)
echo print^("Checking Technical Analysis..."^)
echo print^("-"*80^)
echo.
echo for package, desc in ta_packages.items^(^):
echo     try:
echo         __import__^(package^)
echo         version = ""
echo         try:
echo             mod = __import__^(package^)
echo             version = f" ^(v{mod.__version__}^)" if hasattr^(mod, '__version__'^) else ""
echo         except:
echo             pass
echo         print^(f"✓ {package:20s} {desc:40s}{version}"^)
echo         installed.append^(package^)
echo     except ImportError:
echo         print^(f"✗ {package:20s} NOT INSTALLED - {desc}"^)
echo         missing.append^(package^)
echo.
echo print^(^)
echo print^("="*80^)
echo print^("VERIFICATION SUMMARY"^)
echo print^("="*80^)
echo print^(f"Installed: {len(installed)} packages"^)
echo print^(f"Missing: {len(missing)} packages"^)
echo print^(^)
echo.
echo if missing:
echo     print^("✗ INCOMPLETE INSTALLATION"^)
echo     print^(^)
echo     print^("Missing packages:"^)
echo     for pkg in missing:
echo         print^(f"  - {pkg}"^)
echo     print^(^)
echo     print^("Please run INSTALL.bat to install missing packages."^)
echo     sys.exit^(1^)
echo else:
echo     print^("✓ ALL REQUIRED PACKAGES INSTALLED"^)
echo     print^(^)
echo     print^("System is ready to use!"^)
echo     print^(^)
echo     print^("Next steps:"^)
echo     print^("  1. Run TEST_EVENT_RISK_GUARD.bat to test event detection"^)
echo     print^("  2. Run RUN_OVERNIGHT_PIPELINE.bat to start screening"^)
echo     sys.exit^(0^)
) > verify_packages.py

echo.
echo Running verification...
echo.

python verify_packages.py
set VERIFY_EXIT_CODE=%errorlevel%

REM Cleanup
del verify_packages.py

echo.
echo ================================================================================
echo.

if %VERIFY_EXIT_CODE% neq 0 (
    echo To install missing packages, run: INSTALL.bat
    echo.
)

pause
exit /b %VERIFY_EXIT_CODE%
