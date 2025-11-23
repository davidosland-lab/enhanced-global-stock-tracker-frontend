@echo off
REM ============================================================================
REM CLEAR PYTHON CACHE - Dual Market Screening System
REM ============================================================================
REM
REM This script removes all Python cache files (.pyc, __pycache__) that may
REM cause old code to be executed even after updating files.
REM
REM IMPORTANT: Run this BEFORE running the screening system after any update!
REM
REM ============================================================================

echo.
echo ============================================================================
echo   CLEARING PYTHON CACHE - Dual Market Screening System
echo ============================================================================
echo.
echo This will remove all cached Python files (.pyc, __pycache__)
echo to ensure you're running the latest code version.
echo.
pause

echo.
echo [1/3] Removing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Removing: %%d
    rd /s /q "%%d"
)

echo.
echo [2/3] Removing .pyc files...
del /s /q *.pyc 2>nul

echo.
echo [3/3] Removing .pyo files...
del /s /q *.pyo 2>nul

echo.
echo ============================================================================
echo   CACHE CLEARED SUCCESSFULLY!
echo ============================================================================
echo.
echo You can now run the screening system with the latest code.
echo.
echo Next steps:
echo   1. Run QUICK TEST.bat to verify the system
echo   2. Or run RUN_BOTH_MARKETS.bat for full dual-market screening
echo.
pause
