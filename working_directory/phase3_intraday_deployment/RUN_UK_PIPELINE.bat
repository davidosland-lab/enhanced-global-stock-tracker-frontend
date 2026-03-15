@echo off
REM UK Market Pipeline Runner - Windows Launcher
REM LSE Trading Automation

echo ========================================
echo   UK Market Pipeline Runner v1.3.11
echo   LSE Trading Automation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo Select an option:
echo.
echo [1] FTSE 100 Top 10 (SHEL, AZN, HSBA, ULVR, BP, GSK, DGE, RIO, REL, NG)
echo [2] FTSE 100 Banks (HSBA, LLOY, BARC, NWG, STAN)
echo [3] FTSE 100 Energy (SHEL, BP, SSE, CNA, NG)
echo [4] FTSE 100 Pharma (AZN, GSK, HLMA)
echo [5] UK Blue Chips (HSBA, SHEL, BP, AZN, ULVR, GSK, DGE, RIO)
echo [6] UK Dividend (SHEL, BP, HSBA, GSK, VOD, IMB, SSE, NG)
echo [7] Custom symbols
echo [8] List all presets
echo.
set /p CHOICE="Enter choice (1-8): "

if "%CHOICE%"=="1" set PRESET=FTSE 100 Top 10
if "%CHOICE%"=="2" set PRESET=FTSE 100 Banks
if "%CHOICE%"=="3" set PRESET=FTSE 100 Energy
if "%CHOICE%"=="4" set PRESET=FTSE 100 Pharma
if "%CHOICE%"=="5" set PRESET=UK Blue Chips
if "%CHOICE%"=="6" set PRESET=UK Dividend
if "%CHOICE%"=="8" goto :list_presets

if "%CHOICE%"=="7" (
    echo.
    set /p SYMBOLS="Enter LSE symbols (comma-separated, e.g., HSBA.L,BP.L,SHEL.L): "
    echo.
    set /p CAPITAL="Enter initial capital in GBP (default: 100000): "
    if "!CAPITAL!"=="" set CAPITAL=100000
    
    echo.
    echo Starting UK Pipeline with custom symbols...
    echo Symbols: !SYMBOLS!
    echo Capital: £!CAPITAL! GBP
    echo.
    python run_uk_pipeline.py --symbols "!SYMBOLS!" --capital !CAPITAL!
    goto :end
)

if not defined PRESET (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
set /p CAPITAL="Enter initial capital in GBP (default: 100000): "
if "%CAPITAL%"=="" set CAPITAL=100000

echo.
set /p IGNORE_HOURS="Ignore market hours? (y/N): "

echo.
echo Starting UK Pipeline...
echo Preset: %PRESET%
echo Capital: £%CAPITAL% GBP
echo.

if /i "%IGNORE_HOURS%"=="y" (
    python run_uk_pipeline.py --preset "%PRESET%" --capital %CAPITAL% --ignore-market-hours
) else (
    python run_uk_pipeline.py --preset "%PRESET%" --capital %CAPITAL%
)
goto :end

:list_presets
python run_uk_pipeline.py --list-presets
pause
exit /b 0

:end
pause
