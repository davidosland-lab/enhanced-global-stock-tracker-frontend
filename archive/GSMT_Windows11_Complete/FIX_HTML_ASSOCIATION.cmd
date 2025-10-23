@echo off
cls
color 0E
title Fix HTML File Association

echo ============================================================
echo     FIX HTML FILE ASSOCIATION
echo     This will set HTML files to open in browser
echo ============================================================
echo.
echo Your HTML files are currently opening in Notepad.
echo This script will fix that issue.
echo.
echo Press any key to fix the file association...
pause >nul

echo.
echo Fixing HTML file association...

REM Method 1: Using assoc and ftype commands
assoc .html=htmlfile >nul 2>&1
ftype htmlfile="%%ProgramFiles%%\Internet Explorer\iexplore.exe" %%1 >nul 2>&1

REM Method 2: Try to set default browser associations
echo Setting browser as default for HTML files...

REM Try to use Windows settings
start ms-settings:defaultapps >nul 2>&1

echo.
echo ============================================================
echo     MANUAL FIX INSTRUCTIONS
echo ============================================================
echo.
echo If the automatic fix didn't work:
echo.
echo 1. Right-click any .html file
echo 2. Select "Open with" → "Choose another app"
echo 3. Select your preferred browser (Chrome, Edge, Firefox)
echo 4. Check "Always use this app to open .html files"
echo 5. Click OK
echo.
echo OR:
echo.
echo 1. Go to Windows Settings → Apps → Default apps
echo 2. Find your preferred browser
echo 3. Click on it and set it as default for .html files
echo.
echo ============================================================
echo.
echo After fixing the association, run LAUNCH_GSMT.cmd again.
echo.
pause