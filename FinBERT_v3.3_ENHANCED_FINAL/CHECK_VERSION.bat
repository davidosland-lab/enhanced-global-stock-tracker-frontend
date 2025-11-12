@echo off
echo.
echo ============================================
echo    FINBERT VERSION CHECKER
echo ============================================
echo.
echo Checking installed version...
echo.

findstr /C:"v3.3" finbert_charts_complete.html >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Version 3.3 ENHANCED detected!
    echo.
    echo You have the correct enhanced version with:
    echo - Time descriptors on x-axis
    echo - Synchronized volume chart
    echo - Color-coded volume bars
    echo.
) else (
    echo [WARNING] Version 3.3 not detected
    echo.
    echo You may have an older version.
    echo Please ensure you extracted the correct ZIP file.
    echo.
)

echo ============================================
echo.
pause