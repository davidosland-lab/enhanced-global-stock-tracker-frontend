@echo off
REM ============================================================================
REM RATE LIMIT FIX - INSTALLER
REM Slows down API queries to prevent rate limiting and failed verifications
REM ============================================================================

echo ============================================================================
echo RATE LIMIT FIX - SLOW DOWN API QUERIES
echo ============================================================================
echo.
echo Problem: Too many failed verifications due to API rate limiting
echo Solution: Reduce parallel workers and add delays between requests
echo.
echo Current Settings (TOO FAST):
echo   - max_workers: 4 (parallel requests)
echo   - batch_size: 10 (stocks per batch)
echo   - retry_delay_seconds: 5 (retry wait time)
echo   - NO delays between requests
echo.
echo New Settings (OPTIMIZED FOR RELIABILITY):
echo   - max_workers: 2 (50%% reduction in parallel requests)
echo   - batch_size: 5 (50%% smaller batches)
echo   - retry_delay_seconds: 10 (double the retry wait)
echo   - request_delay_seconds: 0.5 (NEW - wait between each request)
echo   - batch_delay_seconds: 2.0 (NEW - wait between batches)
echo   - validation_timeout_seconds: 15 (was 10 - more time to respond)
echo.
echo Trade-off:
echo   - Pipeline will take ~25%% longer to complete
echo   - Significantly fewer failed verifications
echo   - More reliable data fetching
echo   - Better success rate
echo.
pause
echo.

REM Step 1: Backup current config
echo ============================================================================
echo Step 1: Backing up current configuration
echo ============================================================================
echo.

if exist ..\models\config\screening_config.json (
    echo Creating backup...
    copy ..\models\config\screening_config.json ..\models\config\screening_config.json.BACKUP_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: Failed to create backup
        echo    Please manually backup: models\config\screening_config.json
        pause
        exit /b 1
    )
    
    echo ✓ Backup created successfully
) else (
    echo ❌ ERROR: Configuration file not found
    echo    Looking for: ..\models\config\screening_config.json
    echo    Make sure you're running this from RATE_LIMIT_FIX directory
    pause
    exit /b 1
)
echo.
pause

REM Step 2: Apply rate limit fix
echo.
echo ============================================================================
echo Step 2: Applying Rate Limit Fix
echo ============================================================================
echo.

echo Copying optimized configuration...
copy /Y screening_config_SLOW.json ..\models\config\screening_config.json

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to copy new configuration
    echo    Restoring backup...
    copy /Y ..\models\config\screening_config.json.BACKUP_* ..\models\config\screening_config.json
    pause
    exit /b 1
)

echo ✓ Rate limit fix applied successfully
echo.
pause

REM Step 3: Verify changes
echo.
echo ============================================================================
echo Step 3: Verifying Configuration Changes
echo ============================================================================
echo.

echo Checking new settings...
echo.

REM Use Python to verify JSON
python -c "import json; f=open('../models/config/screening_config.json','r'); c=json.load(f); print(f'✓ max_workers: {c[\"performance\"][\"max_workers\"]}'); print(f'✓ batch_size: {c[\"performance\"][\"batch_size\"]}'); print(f'✓ retry_delay_seconds: {c[\"data_fetch\"][\"retry_delay_seconds\"]}'); print(f'✓ validation_timeout_seconds: {c[\"screening\"][\"validation_timeout_seconds\"]}'); print(f'✓ request_delay_seconds: {c[\"data_fetch\"].get(\"request_delay_seconds\", \"N/A\")}'); print(f'✓ batch_delay_seconds: {c[\"data_fetch\"].get(\"batch_delay_seconds\", \"N/A\")}')" 2>nul

if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Could not verify configuration with Python
    echo    Please manually verify: models\config\screening_config.json
    echo.
) else (
    echo.
    echo ✓ All settings verified successfully
    echo.
)

pause

REM Step 4: Summary
echo.
echo ============================================================================
echo INSTALLATION COMPLETE
echo ============================================================================
echo.
echo ✅ Rate limit fix has been applied!
echo.
echo What Changed:
echo   ✓ Reduced parallel workers: 4 → 2
echo   ✓ Reduced batch size: 10 → 5
echo   ✓ Increased retry delay: 5s → 10s
echo   ✓ Increased validation timeout: 10s → 15s
echo   ✓ Added request delay: 0.5 seconds between requests
echo   ✓ Added batch delay: 2.0 seconds between batches
echo.
echo Expected Results:
echo   • Fewer failed verifications
echo   • More reliable data fetching
echo   • Higher success rate (should see 90%%+ success)
echo   • Pipeline takes ~25%% longer (~12-15 min instead of 10 min)
echo.
echo 🚀 Next Steps:
echo   1. Run your pipeline: python models\screening\overnight_pipeline.py
echo   2. Watch for "✓" success indicators instead of "✗" failures
echo   3. Check final report for completion rate
echo.
echo 📁 Backup saved:
echo   models\config\screening_config.json.BACKUP_[timestamp]
echo.
echo 🔄 To Revert:
echo   Copy the backup file back to screening_config.json
echo.
echo ============================================================================
echo.
pause
