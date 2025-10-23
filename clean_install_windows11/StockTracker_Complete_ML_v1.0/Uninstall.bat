@echo off
title Stock Tracker Uninstaller
color 0C

echo ===============================================================================
echo                        STOCK TRACKER UNINSTALLER
echo ===============================================================================
echo.

set /p confirm="Remove Stock Tracker? (Y/N): "
if /i "%confirm%" neq "Y" exit /b 0

echo Removing desktop shortcut...
del "%USERPROFILE%\Desktop\Stock Tracker.lnk" 2>nul

echo Stopping services...
taskkill /f /im python.exe 2>nul

echo.
echo Uninstall complete!
echo You can now delete this folder.
pause