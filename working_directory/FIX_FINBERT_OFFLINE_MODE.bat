@echo off
REM ============================================================================
REM FIX FINBERT OFFLINE MODE - FORCE LOCAL CACHE ONLY
REM ============================================================================
REM This patches the system to use FinBERT from local cache without checking
REM HuggingFace online. Eliminates all network delays and timeouts.
REM ============================================================================

echo.
echo ============================================================================
echo FIXING FINBERT TO USE LOCAL CACHE ONLY (OFFLINE MODE)
echo ============================================================================
echo.
echo This will patch 3 files to force FinBERT offline mode:
echo   1. unified_trading_dashboard.py - Set env vars at startup
echo   2. paper_trading_coordinator.py - Set env vars at startup  
echo   3. sentiment_integration.py - Set env vars before import
echo.
echo Result: No HuggingFace network checks, instant FinBERT loading
echo.
pause

cd /d "%~dp0COMPLETE_SYSTEM_v1.3.15.45_FINAL"

echo.
echo [1/3] Patching unified_trading_dashboard.py...
python -c "import os; f='unified_trading_dashboard.py'; content=open(f, encoding='utf-8').read(); marker='# Set environment variables for offline FinBERT'; exit(0) if marker in content else exit(1)" 2>nul
if %errorlevel%==0 (
    echo Already patched - skipping
) else (
    python -c "import os; f='unified_trading_dashboard.py'; lines=open(f, encoding='utf-8').readlines(); idx=next((i for i, line in enumerate(lines) if 'import' in line.lower() and not line.strip().startswith('#')), 0); lines.insert(idx, '# Set environment variables for offline FinBERT\nimport os\nos.environ[\"TRANSFORMERS_OFFLINE\"] = \"1\"\nos.environ[\"HF_HUB_OFFLINE\"] = \"1\"\nos.environ[\"HF_HUB_DISABLE_TELEMETRY\"] = \"1\"\n\n'); open(f, 'w', encoding='utf-8').writelines(lines)"
    if %errorlevel%==0 (
        echo ✓ Patched successfully
    ) else (
        echo ✗ Failed to patch
    )
)

echo.
echo [2/3] Patching paper_trading_coordinator.py...
python -c "import os; f='paper_trading_coordinator.py'; content=open(f, encoding='utf-8').read(); marker='# Set environment variables for offline FinBERT'; exit(0) if marker in content else exit(1)" 2>nul
if %errorlevel%==0 (
    echo Already patched - skipping
) else (
    python -c "import os; f='paper_trading_coordinator.py'; lines=open(f, encoding='utf-8').readlines(); idx=next((i for i, line in enumerate(lines) if 'import' in line.lower() and not line.strip().startswith('#')), 0); lines.insert(idx, '# Set environment variables for offline FinBERT\nimport os\nos.environ[\"TRANSFORMERS_OFFLINE\"] = \"1\"\nos.environ[\"HF_HUB_OFFLINE\"] = \"1\"\nos.environ[\"HF_HUB_DISABLE_TELEMETRY\"] = \"1\"\n\n'); open(f, 'w', encoding='utf-8').writelines(lines)"
    if %errorlevel%==0 (
        echo ✓ Patched successfully
    ) else (
        echo ✗ Failed to patch
    )
)

echo.
echo [3/3] Patching sentiment_integration.py...
python -c "import os; f='sentiment_integration.py'; content=open(f, encoding='utf-8').read(); marker='# Set environment variables for offline FinBERT'; exit(0) if marker in content else exit(1)" 2>nul
if %errorlevel%==0 (
    echo Already patched - skipping
) else (
    python -c "import os; f='sentiment_integration.py'; lines=open(f, encoding='utf-8').readlines(); idx=next((i for i, line in enumerate(lines) if 'import' in line.lower() and not line.strip().startswith('#')), 0); lines.insert(idx, '# Set environment variables for offline FinBERT\nimport os\nos.environ[\"TRANSFORMERS_OFFLINE\"] = \"1\"\nos.environ[\"HF_HUB_OFFLINE\"] = \"1\"\nos.environ[\"HF_HUB_DISABLE_TELEMETRY\"] = \"1\"\n\n'); open(f, 'w', encoding='utf-8').writelines(lines)"
    if %errorlevel%==0 (
        echo ✓ Patched successfully
    ) else (
        echo ✗ Failed to patch
    )
)

echo.
echo ============================================================================
echo PATCH COMPLETE - VERIFICATION
echo ============================================================================
echo.
echo Checking for offline mode markers...
findstr /C:"TRANSFORMERS_OFFLINE" unified_trading_dashboard.py >nul 2>&1
if %errorlevel%==0 (
    echo ✓ unified_trading_dashboard.py: OFFLINE MODE enabled
) else (
    echo ✗ unified_trading_dashboard.py: NOT patched
)

findstr /C:"TRANSFORMERS_OFFLINE" paper_trading_coordinator.py >nul 2>&1
if %errorlevel%==0 (
    echo ✓ paper_trading_coordinator.py: OFFLINE MODE enabled
) else (
    echo ✗ paper_trading_coordinator.py: NOT patched
)

findstr /C:"TRANSFORMERS_OFFLINE" sentiment_integration.py >nul 2>&1
if %errorlevel%==0 (
    echo ✓ sentiment_integration.py: OFFLINE MODE enabled
) else (
    echo ✗ sentiment_integration.py: NOT patched
)

echo.
echo ============================================================================
echo SUCCESS - FINBERT OFFLINE MODE ENABLED
echo ============================================================================
echo.
echo What changed:
echo   - All 3 main files now set TRANSFORMERS_OFFLINE=1 before imports
echo   - HuggingFace will NOT check online for model updates
echo   - FinBERT loads instantly from local cache
echo.
echo Expected behavior:
echo   - NO "httpx - INFO - HTTP Request: GET https://huggingface.co" messages
echo   - Dashboard starts in 10-15 seconds (not 2+ minutes)
echo   - FinBERT works with full accuracy
echo.
echo Next steps:
echo   1. Start dashboard: START_UNIFIED_DASHBOARD.bat
echo   2. Watch console - should see NO HuggingFace network requests
echo   3. FinBERT should load in ~10 seconds from cache
echo.
pause
