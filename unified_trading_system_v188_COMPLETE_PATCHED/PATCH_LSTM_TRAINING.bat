@echo off
REM ================================================================================
REM LSTM TRAINING HOT-PATCH - v1.3.15.87
REM ================================================================================
REM
REM Fixes: Flask routes to support symbols with dots (BHP.AX, HSBA.L, etc.)
REM Issue: "Training failed: BAD REQUEST" for ASX/LSE stocks
REM 
REM This patch can be applied while the dashboard is running.
REM The Flask server will auto-reload and pick up the changes.
REM
REM ================================================================================

echo.
echo ================================================================================
echo   LSTM TRAINING HOT-PATCH v1.3.15.87
echo ================================================================================
echo.
echo This patch fixes Flask routes to support symbols with dots
echo (e.g., BHP.AX, CBA.AX, HSBA.L, BP.L)
echo.
echo Target file: finbert_v4.4.4\app_finbert_v4_dev.py
echo Changes: 7 route definitions updated
echo.

REM Check if we're in the right directory
if not exist "finbert_v4.4.4\app_finbert_v4_dev.py" (
    echo [ERROR] Cannot find finbert_v4.4.4\app_finbert_v4_dev.py
    echo.
    echo Please run this patch from the unified_trading_dashboard_v1.3.15.87_ULTIMATE directory
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [OK] Found target file
echo.

REM Create backup
echo Creating backup...
set BACKUP_FILE=finbert_v4.4.4\app_finbert_v4_dev.py.backup_%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_FILE=%BACKUP_FILE: =0%
copy /Y "finbert_v4.4.4\app_finbert_v4_dev.py" "%BACKUP_FILE%" >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Failed to create backup
    pause
    exit /b 1
)

echo [OK] Backup created: %BACKUP_FILE%
echo.

REM Apply patches using PowerShell for better text replacement
echo Applying patches...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$content = Get-Content 'finbert_v4.4.4\app_finbert_v4_dev.py' -Raw -Encoding UTF8; ^
$changes = 0; ^
if ($content -match '@app\.route\(''/api/train/<symbol>''\)') { ^
    $content = $content -replace '@app\.route\(''/api/train/<symbol>''\)', '@app.route(''/api/train/<path:symbol>'')'; ^
    Write-Host '  [1/7] Fixed /api/train/<symbol> route'; ^
    $changes++; ^
} else { ^
    Write-Host '  [1/7] Already patched or not found: /api/train/<symbol>'; ^
} ^
if ($content -match '@app\.route\(''/api/stock/<symbol>''\)') { ^
    $content = $content -replace '@app\.route\(''/api/stock/<symbol>''\)', '@app.route(''/api/stock/<path:symbol>'')'; ^
    Write-Host '  [2/7] Fixed /api/stock/<symbol> route'; ^
    $changes++; ^
} else { ^
    Write-Host '  [2/7] Already patched or not found: /api/stock/<symbol>'; ^
} ^
if ($content -match '@app\.route\(''/api/sentiment/<symbol>''\)') { ^
    $content = $content -replace '@app\.route\(''/api/sentiment/<symbol>''\)', '@app.route(''/api/sentiment/<path:symbol>'')'; ^
    Write-Host '  [3/7] Fixed /api/sentiment/<symbol> route'; ^
    $changes++; ^
} else { ^
    Write-Host '  [3/7] Already patched or not found: /api/sentiment/<symbol>'; ^
} ^
if ($content -match '@app\.route\(''/api/predictions/<symbol>''\)' -and $content -notmatch '/api/predictions/<symbol>/') { ^
    $content = $content -replace '(@app\.route\(''/api/predictions/)<symbol>(''[^/]))', '$1<path:symbol>$2'; ^
    Write-Host '  [4/7] Fixed /api/predictions/<symbol> route'; ^
    $changes++; ^
} else { ^
    Write-Host '  [4/7] Already patched or not found: /api/predictions/<symbol>'; ^
} ^
if ($content -match '@app\.route\(''/api/predictions/<symbol>/history''\)') { ^
    $content = $content -replace '@app\.route\(''/api/predictions/<symbol>/history''\)', '@app.route(''/api/predictions/<path:symbol>/history'')'; ^
    Write-Host '  [5/7] Fixed /api/predictions/<symbol>/history route'; ^
    $changes++; ^
} else { ^
    Write-Host '  [5/7] Already patched or not found: /api/predictions/<symbol>/history'; ^
} ^
if ($content -match '@app\.route\(''/api/predictions/<symbol>/accuracy''\)') { ^
    $content = $content -replace '@app\.route\(''/api/predictions/<symbol>/accuracy''\)', '@app.route(''/api/predictions/<path:symbol>/accuracy'')'; ^
    Write-Host '  [6/7] Fixed /api/predictions/<symbol>/accuracy route'; ^
    $changes++; ^
} else { ^
    Write-Host '  [6/7] Already patched or not found: /api/predictions/<symbol>/accuracy'; ^
} ^
if ($content -match '@app\.route\(''/api/trading/positions/<symbol>/close''\)') { ^
    $content = $content -replace '@app\.route\(''/api/trading/positions/<symbol>/close''\)', '@app.route(''/api/trading/positions/<path:symbol>/close'')'; ^
    Write-Host '  [7/7] Fixed /api/trading/positions/<symbol>/close route'; ^
    $changes++; ^
} else { ^
    Write-Host '  [7/7] Already patched or not found: /api/trading/positions/<symbol>/close'; ^
} ^
if ($changes -gt 0) { ^
    $content | Set-Content 'finbert_v4.4.4\app_finbert_v4_dev.py' -Encoding UTF8 -NoNewline; ^
    Write-Host ''; ^
    Write-Host '[OK] Applied' $changes 'patches successfully'; ^
    exit 0; ^
} else { ^
    Write-Host ''; ^
    Write-Host '[INFO] No patches applied (already patched or routes not found)'; ^
    exit 0; ^
}"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to apply patches
    echo Restoring from backup...
    copy /Y "%BACKUP_FILE%" "finbert_v4.4.4\app_finbert_v4_dev.py" >nul 2>&1
    echo [OK] Restored from backup
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   PATCH APPLIED SUCCESSFULLY
echo ================================================================================
echo.
echo Changes made:
echo   - All Flask routes now accept symbols with dots
echo   - Examples: BHP.AX, CBA.AX, HSBA.L, BP.L, SHOP.TO
echo.
echo If Flask server is running with auto-reload enabled:
echo   - Flask will detect the change and reload automatically
echo   - You should see: "Detected change... Reloading"
echo   - Wait 2-3 seconds for reload to complete
echo.
echo If Flask server is NOT running or auto-reload is disabled:
echo   - Restart the Flask server manually:
echo     cd finbert_v4.4.4
echo     python app_finbert_v4_dev.py
echo.
echo Test the fix:
echo   1. Open: http://localhost:5000
echo   2. Click: "Train LSTM Model" button
echo   3. Enter symbol: BHP.AX
echo   4. Set epochs: 50
echo   5. Click: "Start Training"
echo.
echo Expected result: SUCCESS (no more "BAD REQUEST" error)
echo.
echo Backup saved to: %BACKUP_FILE%
echo.
echo ================================================================================
echo.
pause
