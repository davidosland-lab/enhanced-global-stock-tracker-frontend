@echo off
title Create Desktop Shortcuts
color 0E

echo ================================================================================
echo                    CREATE STOCK TRACKER DESKTOP SHORTCUTS
echo ================================================================================
echo.
echo This will create desktop shortcuts for easy access to Stock Tracker
echo.

:: Get Desktop path
set "desktop=%USERPROFILE%\Desktop"

echo Creating shortcuts on your desktop...
echo.

:: Create Stock Tracker Control Panel shortcut
echo [1/4] Creating Stock Tracker Control Panel shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\Stock Tracker Control Panel.lnk'); $Shortcut.TargetPath = '%~dp0StockTracker.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Description = 'Stock Tracker Control Panel - Manage all services'; $Shortcut.Save()"
echo    ✓ Created: Stock Tracker Control Panel.lnk

:: Create Quick Start shortcut
echo [2/4] Creating Quick Start shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\Stock Tracker - Quick Start.lnk'); $Shortcut.TargetPath = '%~dp0startup.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,76'; $Shortcut.Description = 'Quickly start Stock Tracker and open in browser'; $Shortcut.Save()"
echo    ✓ Created: Stock Tracker - Quick Start.lnk

:: Create Shutdown shortcut
echo [3/4] Creating Shutdown shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\Stock Tracker - Shutdown.lnk'); $Shortcut.TargetPath = '%~dp0shutdown.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,27'; $Shortcut.Description = 'Stop all Stock Tracker services'; $Shortcut.Save()"
echo    ✓ Created: Stock Tracker - Shutdown.lnk

:: Create Web Interface shortcut
echo [4/4] Creating Web Interface shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\Stock Tracker - Web Interface.lnk'); $Shortcut.TargetPath = 'http://localhost:8000'; $Shortcut.IconLocation = 'shell32.dll,14'; $Shortcut.Description = 'Open Stock Tracker in your browser'; $Shortcut.Save()"
echo    ✓ Created: Stock Tracker - Web Interface.lnk

echo.
echo ================================================================================
echo ✓ All desktop shortcuts created successfully!
echo ================================================================================
echo.
echo You can now access Stock Tracker from your desktop:
echo   • Stock Tracker Control Panel - Full service management
echo   • Stock Tracker Quick Start - Start everything with one click
echo   • Stock Tracker Shutdown - Stop all services
echo   • Stock Tracker Web Interface - Direct browser access
echo.
pause