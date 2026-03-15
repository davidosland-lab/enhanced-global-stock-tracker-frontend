@echo off
REM Download Unified Trading Platform from GitHub

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         DOWNLOADING UNIFIED TRADING PLATFORM                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Downloading unified_trading_platform.py from GitHub...
echo.

REM GitHub raw file URL
set "FILE_URL=https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/unified_trading_platform.py"

REM Download using PowerShell
powershell -Command "& {Invoke-WebRequest -Uri '%FILE_URL%' -OutFile 'unified_trading_platform.py'}"

if %errorlevel% equ 0 (
    echo.
    echo ✅ Download complete!
    echo.
    echo File saved to: %CD%\unified_trading_platform.py
    echo.
    echo You can now run: START_UNIFIED_PLATFORM.bat
    echo Or: python unified_trading_platform.py --paper-trading
    echo.
) else (
    echo.
    echo ❌ Download failed!
    echo.
    echo Please download manually from:
    echo https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
    echo Branch: market-timing-critical-fix
    echo File: working_directory/unified_trading_platform.py
    echo.
)

pause
