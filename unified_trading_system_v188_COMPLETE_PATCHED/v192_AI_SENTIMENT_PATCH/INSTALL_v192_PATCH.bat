@echo off
REM ============================================================================
REM  AI-Enhanced Macro Sentiment Analysis - Patch v192
REM  For: v188_COMPLETE_PATCHED, v190_COMPLETE, v191.x
REM  Date: 2026-02-28
REM  Author: FinBERT v4.4.4 Enhanced
REM ============================================================================

echo.
echo ========================================================================
echo  AI-Enhanced Macro Sentiment Analysis - Patch v192 Installer
echo ========================================================================
echo.
echo This patch fixes the CRITICAL bug:
echo   - Iran-US conflict NOW detected as -0.70 CRITICAL (was 0.00 NEUTRAL)
echo   - Automatic position reduction by 50 percent during crises
echo   - Keyword-based crisis detection (wars, tariffs, banking crises)
echo.
echo Installation: Run this BAT file, it will copy all necessary files
echo Time: 30 seconds
echo Cost: $0 (no AI API required)
echo.
pause

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.7+ and add it to PATH
    echo.
    pause
    exit /b 1
)

REM Run the Python installer
python install_v192_patch.py

echo.
echo ========================================================================
echo  Patch installation completed!
echo ========================================================================
echo.
echo Next step: Run the test suite to verify installation
echo   Command: python test_ai_macro_sentiment.py
echo.
pause
