@echo off
REM AU Market Pipeline Runner - Windows Launcher
REM ASX Trading Automation

echo ========================================
echo   AU Market Pipeline Runner v1.3.11
echo   ASX Trading Automation
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
echo [1] ASX Blue Chips (CBA, BHP, RIO, WOW, CSL, WES, NAB, ANZ)
echo [2] ASX Banks (CBA, NAB, WBC, ANZ, MQG, BOQ)
echo [3] ASX Mining (BHP, RIO, FMG, NCM, S32, IGO, MIN)
echo [4] ASX Tech (WTC, XRO, CPU, APX, TNE)
echo [5] ASX Top 20
echo [6] Custom symbols
echo [7] List all presets
echo.
set /p CHOICE="Enter choice (1-7): "

if "%CHOICE%"=="1" set PRESET=ASX Blue Chips
if "%CHOICE%"=="2" set PRESET=ASX Banks
if "%CHOICE%"=="3" set PRESET=ASX Mining
if "%CHOICE%"=="4" set PRESET=ASX Tech
if "%CHOICE%"=="5" set PRESET=ASX Top 20
if "%CHOICE%"=="7" goto :list_presets

if "%CHOICE%"=="6" (
    echo.
    set /p SYMBOLS="Enter ASX symbols (comma-separated, e.g., CBA.AX,BHP.AX): "
    echo.
    set /p CAPITAL="Enter initial capital in AUD (default: 100000): "
    if "!CAPITAL!"=="" set CAPITAL=100000
    
    echo.
    echo Starting AU Pipeline with custom symbols...
    echo Symbols: !SYMBOLS!
    echo Capital: $!CAPITAL! AUD
    echo.
    python run_au_pipeline.py --symbols "!SYMBOLS!" --capital !CAPITAL!
    goto :end
)

if not defined PRESET (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
set /p CAPITAL="Enter initial capital in AUD (default: 100000): "
if "%CAPITAL%"=="" set CAPITAL=100000

echo.
set /p IGNORE_HOURS="Ignore market hours? (y/N): "

echo.
echo Starting AU Pipeline...
echo Preset: %PRESET%
echo Capital: $%CAPITAL% AUD
echo.

if /i "%IGNORE_HOURS%"=="y" (
    python run_au_pipeline.py --preset "%PRESET%" --capital %CAPITAL% --ignore-market-hours
) else (
    python run_au_pipeline.py --preset "%PRESET%" --capital %CAPITAL%
)
goto :end

:list_presets
python run_au_pipeline.py --list-presets
pause
exit /b 0

:end
pause
