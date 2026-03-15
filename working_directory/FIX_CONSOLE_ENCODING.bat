@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM   FIX WINDOWS CONSOLE ENCODING ERRORS
REM   Removes emoji characters from log messages
REM ============================================================================
REM
REM   This patch fixes:
REM   - UnicodeEncodeError: 'charmap' codec can't encode character
REM   - Windows console can't display emoji characters (✅, ❌, ⚠️, etc.)
REM   - Replaces emojis with text equivalents
REM
REM   Version: 1.3.2 FINAL - WINDOWS COMPATIBLE
REM   Date: December 29, 2024
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   FIX WINDOWS CONSOLE ENCODING ERRORS
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   This patch removes emoji characters that cause encoding errors
echo   on Windows console.
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Change to script directory
cd /d "%~dp0"

echo [Step 1/4] Checking current directory...
echo           Working directory: %CD%
echo.

REM ============================================================================
REM Fix adaptive_ml_integration.py
REM ============================================================================
echo [Step 2/4] Fixing ml_pipeline/adaptive_ml_integration.py...

set "FILE1=ml_pipeline\adaptive_ml_integration.py"

if not exist "%FILE1%" (
    echo           [ERROR] File not found: %FILE1%
    echo.
    pause
    exit /b 1
)

REM Create backup
copy "%FILE1%" "%FILE1%.backup" >nul 2>&1
if exist "%FILE1%.backup" (
    echo           Created backup: %FILE1%.backup
) else (
    echo           [WARNING] Could not create backup
)

REM Remove emojis using PowerShell
echo           Removing emoji characters...
powershell -Command "$content = Get-Content '%FILE1%' -Raw -Encoding UTF8; $content = $content -replace '🤖', '[ML]'; $content = $content -replace '✅', '[OK]'; $content = $content -replace '📦', '[INFO]'; $content = $content -replace '⚠️', '[WARN]'; $content = $content -replace '❌', '[ERROR]'; $content = $content -replace '🎯', '[TARGET]'; $content = $content -replace '🏦', '[BANK]'; Set-Content '%FILE1%' $content -Encoding UTF8 -NoNewline"

echo           [SUCCESS] Emojis removed from adaptive_ml_integration.py
echo.

REM ============================================================================
REM Fix swing_signal_generator.py
REM ============================================================================
echo [Step 3/4] Fixing ml_pipeline/swing_signal_generator.py...

set "FILE2=ml_pipeline\swing_signal_generator.py"

if not exist "%FILE2%" (
    echo           [WARNING] File not found: %FILE2%
    echo           Skipping...
) else (
    REM Create backup
    copy "%FILE2%" "%FILE2%.backup" >nul 2>&1
    if exist "%FILE2%.backup" (
        echo           Created backup: %FILE2%.backup
    )
    
    REM Remove emojis
    echo           Removing emoji characters...
    powershell -Command "$content = Get-Content '%FILE2%' -Raw -Encoding UTF8; $content = $content -replace '🎯', '[SIGNAL]'; $content = $content -replace '📊', '[STATS]'; Set-Content '%FILE2%' $content -Encoding UTF8 -NoNewline"
    
    echo           [SUCCESS] Emojis removed from swing_signal_generator.py
)
echo.

REM ============================================================================
REM Fix cba_enhanced_prediction_system.py
REM ============================================================================
echo [Step 4/4] Fixing ml_pipeline/cba_enhanced_prediction_system.py...

set "FILE3=ml_pipeline\cba_enhanced_prediction_system.py"

if not exist "%FILE3%" (
    echo           [WARNING] File not found: %FILE3%
    echo           Skipping...
) else (
    REM Create backup
    copy "%FILE3%" "%FILE3%.backup" >nul 2>&1
    if exist "%FILE3%.backup" (
        echo           Created backup: %FILE3%.backup
    )
    
    REM Remove emojis
    echo           Removing emoji characters...
    powershell -Command "$content = Get-Content '%FILE3%' -Raw -Encoding UTF8; $content = $content -replace '🏦', '[CBA]'; Set-Content '%FILE3%' $content -Encoding UTF8 -NoNewline"
    
    echo           [SUCCESS] Emojis removed from cba_enhanced_prediction_system.py
)
echo.

REM ============================================================================
REM Summary
REM ============================================================================
echo ════════════════════════════════════════════════════════════════════════
echo   FIX COMPLETE
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   Status: ✅ Emoji characters removed successfully!
echo.
echo   Emoji Replacements:
echo   • ✅ → [OK]
echo   • ❌ → [ERROR]
echo   • ⚠️ → [WARN]
echo   • 📦 → [INFO]
echo   • 🤖 → [ML]
echo   • 🎯 → [SIGNAL/TARGET]
echo   • 🏦 → [BANK/CBA]
echo   • 📊 → [STATS]
echo.
echo   Backups created with .backup extension
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

REM ============================================================================
REM Next steps
REM ============================================================================
echo NEXT STEPS:
echo.
echo 1. Test paper trading:
echo    cd phase3_intraday_deployment
echo    python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals
echo.
echo    Expected: No more UnicodeEncodeError!
echo.
echo 2. If you see encoding errors, try setting console encoding:
echo    chcp 65001
echo    python paper_trading_coordinator.py ...
echo.
echo 3. To restore backups:
echo    copy ml_pipeline\adaptive_ml_integration.py.backup ml_pipeline\adaptive_ml_integration.py
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

echo Press any key to exit...
pause >nul
