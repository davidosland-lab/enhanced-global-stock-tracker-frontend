@echo off
echo ======================================================================
echo       STOCK ANALYSIS SYSTEM - UNINSTALLER
echo ======================================================================
echo.
echo This will remove the virtual environment and clean up the installation.
echo Your code files will be preserved.
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Removing virtual environment...
if exist "venv\" (
    rmdir /s /q venv
    echo Virtual environment removed.
) else (
    echo No virtual environment found.
)

echo.
echo Cleaning up Python cache...
if exist "__pycache__\" (
    rmdir /s /q __pycache__
    echo Cache cleaned.
)

echo.
echo ======================================================================
echo       UNINSTALL COMPLETED
echo ======================================================================
echo.
echo The system has been uninstalled.
echo Your source files are still available if you want to reinstall later.
echo.
pause