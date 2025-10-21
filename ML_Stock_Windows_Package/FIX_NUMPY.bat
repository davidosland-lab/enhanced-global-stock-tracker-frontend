@echo off
REM ============================================================
REM FIX NUMPY VERSION CONFLICT
REM ============================================================
REM This fixes the NumPy 2.x compatibility issue
REM ============================================================

title Fixing NumPy Version Conflict
color 0E
cls

echo ============================================================
echo    FIXING NUMPY VERSION CONFLICT
echo ============================================================
echo.
echo You have NumPy 2.3.4 which causes compatibility issues.
echo This script will downgrade to NumPy 1.26.4 for compatibility.
echo.
echo ============================================================
echo.

REM Uninstall current NumPy
echo Step 1: Uninstalling NumPy 2.x...
pip uninstall numpy -y

echo.
echo Step 2: Installing compatible NumPy version...
pip install "numpy<2.0" --force-reinstall

echo.
echo Step 3: Updating other packages for compatibility...
pip install --upgrade scipy pandas

echo.
echo ============================================================
echo    FIX COMPLETE!
echo ============================================================
echo.
echo NumPy has been downgraded to a compatible version.
echo You can now run the server without conflicts.
echo.
pause