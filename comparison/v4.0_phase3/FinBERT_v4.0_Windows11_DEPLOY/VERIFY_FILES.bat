@echo off
echo ============================================================================
echo   FinBERT v4.0 - File Integrity Check
echo ============================================================================
echo.

set ERROR_COUNT=0

echo [1/8] Checking main application file...
if exist app_finbert_v4_dev.py (
    echo    [OK] app_finbert_v4_dev.py
) else (
    echo    [MISSING] app_finbert_v4_dev.py
    set /a ERROR_COUNT+=1
)

echo [2/8] Checking configuration file...
if exist config_dev.py (
    echo    [OK] config_dev.py
) else (
    echo    [MISSING] config_dev.py
    set /a ERROR_COUNT+=1
)

echo [3/8] Checking templates directory...
if exist templates\ (
    echo    [OK] templates\ directory exists
    if exist templates\finbert_v4_enhanced_ui.html (
        echo    [OK] templates\finbert_v4_enhanced_ui.html
    ) else (
        echo    [MISSING] templates\finbert_v4_enhanced_ui.html - THIS IS CRITICAL!
        set /a ERROR_COUNT+=1
    )
) else (
    echo    [MISSING] templates\ directory - THIS IS CRITICAL!
    set /a ERROR_COUNT+=1
)

echo [4/8] Checking models directory...
if exist models\ (
    echo    [OK] models\ directory exists
    if exist models\news_sentiment_real.py (
        echo    [OK] models\news_sentiment_real.py
    ) else (
        echo    [MISSING] models\news_sentiment_real.py
        set /a ERROR_COUNT+=1
    )
) else (
    echo    [MISSING] models\ directory
    set /a ERROR_COUNT+=1
)

echo [5/8] Checking scripts directory...
if exist scripts\ (
    echo    [OK] scripts\ directory exists
    if exist scripts\INSTALL_WINDOWS11.bat (
        echo    [OK] scripts\INSTALL_WINDOWS11.bat
    ) else (
        echo    [MISSING] scripts\INSTALL_WINDOWS11.bat
        set /a ERROR_COUNT+=1
    )
) else (
    echo    [MISSING] scripts\ directory
    set /a ERROR_COUNT+=1
)

echo [6/8] Checking requirements files...
if exist requirements-full.txt (
    echo    [OK] requirements-full.txt
) else (
    echo    [MISSING] requirements-full.txt
    set /a ERROR_COUNT+=1
)

echo [7/8] Checking startup script...
if exist START_FINBERT_V4.bat (
    echo    [OK] START_FINBERT_V4.bat
) else (
    echo    [MISSING] START_FINBERT_V4.bat
    set /a ERROR_COUNT+=1
)

echo [8/8] Checking documentation...
if exist README.md (
    echo    [OK] README.md
) else (
    echo    [MISSING] README.md
    set /a ERROR_COUNT+=1
)

echo.
echo ============================================================================
if %ERROR_COUNT%==0 (
    echo   Result: ALL FILES PRESENT - Package is complete!
    echo.
    echo   Next steps:
    echo   1. Run: scripts\INSTALL_WINDOWS11.bat
    echo   2. Run: START_FINBERT_V4.bat
) else (
    echo   Result: %ERROR_COUNT% FILES MISSING - Package is incomplete!
    echo.
    echo   SOLUTION: Re-extract the ZIP file completely
    echo   Make sure to extract ALL files and folders
)
echo ============================================================================
echo.
pause
