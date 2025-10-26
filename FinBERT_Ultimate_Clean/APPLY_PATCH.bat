@echo off
echo ================================================================
echo    APPLY NEXT DAY PRICE PATCH
echo ================================================================
echo.
echo This will add next day price prediction to your existing system.
echo NO REINSTALLATION NEEDED!
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Backup current file
echo.
echo Creating backup of current app_finbert_ultimate.py...
copy app_finbert_ultimate.py app_finbert_ultimate_before_patch.py
echo Backup saved as: app_finbert_ultimate_before_patch.py
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Python not found. Please apply the patch manually.
    echo See PATCH_NEXT_DAY_PRICE.py for instructions.
    pause
    exit /b 1
)

echo Applying patch...
echo.

REM Since we can't easily do automated patching in batch, provide instructions
echo ================================================================
echo MANUAL PATCH INSTRUCTIONS:
echo ================================================================
echo.
echo Since you already have a working system, you just need to:
echo.
echo 1. The backup has been created: app_finbert_ultimate_before_patch.py
echo.
echo 2. Open app_finbert_ultimate.py in Notepad or any text editor
echo.
echo 3. Search for this line (around line 845):
echo    "# Calculate price target and timeframe"
echo.
echo 4. The patch adds a "next_day" calculation section
echo    See PATCH_NEXT_DAY_PRICE.py for the exact code
echo.
echo 5. Also update the display section (around line 1462)
echo    Search for: "// Current price and estimated price"
echo.
echo ================================================================
echo.
echo Or simply use the already-patched version in this package!
echo The current app_finbert_ultimate.py already includes the patch.
echo.
pause