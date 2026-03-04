@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  LSTM TRAINING FIX - ENABLE IN ALL PIPELINES (AU/US/UK)
REM  Version: v1.3.15.47
REM  Date: 2026-01-29
REM  
REM  Purpose: Verify and enable LSTM training in all three overnight pipelines
REM  
REM  What This Script Does:
REM  1. Verifies FinBERT installation and train_lstm.py module
REM  2. Checks LSTM training configuration in screening_config.json
REM  3. Tests LSTM trainer initialization
REM  4. Verifies all three pipelines have LSTM integration
REM  5. Runs a test training for one symbol (optional)
REM  
REM  Prerequisites:
REM  - FinBERT v4.4.4 installed in finbert_v4.4.4/ directory
REM  - Python 3.8+ with TensorFlow/Keras
REM  - Screening config with lstm_training section
REM ═══════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   LSTM TRAINING VERIFICATION AND FIX
echo   Checking all three pipelines: AU, US, UK
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 1: Check FinBERT Installation
REM ──────────────────────────────────────────────────────────────────────────

echo [STEP 1] Checking FinBERT v4.4.4 Installation...
echo.

if not exist "finbert_v4.4.4\" (
    echo [ERROR] FinBERT directory not found: finbert_v4.4.4\
    echo.
    echo Please ensure FinBERT v4.4.4 is installed in the correct location.
    echo Expected path: %CD%\finbert_v4.4.4\
    pause
    exit /b 1
)

echo [OK] FinBERT directory found: finbert_v4.4.4\
echo.

REM Check for critical LSTM training files
set "CRITICAL_FILES=finbert_v4.4.4\models\train_lstm.py finbert_v4.4.4\models\lstm_predictor.py models\screening\lstm_trainer.py"

for %%F in (%CRITICAL_FILES%) do (
    if not exist "%%F" (
        echo [ERROR] Critical file missing: %%F
        echo.
        echo This file is required for LSTM training to work.
        pause
        exit /b 1
    ) else (
        echo [OK] Found: %%F
    )
)

echo.
echo [SUCCESS] All critical LSTM files present
echo.

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 2: Check LSTM Configuration
REM ──────────────────────────────────────────────────────────────────────────

echo [STEP 2] Checking LSTM Training Configuration...
echo.

if not exist "models\config\screening_config.json" (
    echo [ERROR] Configuration file not found: models\config\screening_config.json
    pause
    exit /b 1
)

echo [OK] Configuration file found
echo.

REM Show current LSTM config (using Python to parse JSON)
python -c "import json; f=open('models/config/screening_config.json'); c=json.load(f); lstm=c.get('lstm_training',{}); print('[LSTM Training Config]'); print(f\"  Enabled: {lstm.get('enabled', True)}\"); print(f\"  Max Models/Night: {lstm.get('max_models_per_night', 20)}\"); print(f\"  Stale Threshold: {lstm.get('stale_threshold_days', 7)} days\"); print(f\"  Epochs: {lstm.get('epochs', 50)}\"); print(f\"  Priority Strategy: {lstm.get('priority_strategy', 'highest_opportunity_score')}\"); f.close()" 2>nul

if errorlevel 1 (
    echo [WARNING] Could not parse LSTM config (Python error^)
    echo Continuing anyway...
) else (
    echo.
    echo [OK] LSTM Training configuration loaded
)

echo.

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 3: Test LSTM Trainer Initialization
REM ──────────────────────────────────────────────────────────────────────────

echo [STEP 3] Testing LSTM Trainer Initialization...
echo.

python -c "import sys; sys.path.insert(0, 'models/screening'); from lstm_trainer import LSTMTrainer; trainer = LSTMTrainer(); print('[OK] LSTM Trainer initialized successfully'); print(f'  Enabled: {trainer.enabled}'); print(f'  Max models: {trainer.max_models_per_night}'); print(f'  Epochs: {trainer.epochs}')" 2>nul

if errorlevel 1 (
    echo [ERROR] LSTM Trainer initialization failed
    echo.
    echo Testing with detailed error output:
    python -c "import sys; sys.path.insert(0, 'models/screening'); from lstm_trainer import LSTMTrainer; trainer = LSTMTrainer()"
    pause
    exit /b 1
)

echo.
echo [SUCCESS] LSTM Trainer initialization test passed
echo.

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 4: Verify Pipeline Integration
REM ──────────────────────────────────────────────────────────────────────────

echo [STEP 4] Verifying LSTM Integration in All Pipelines...
echo.

set "PIPELINES=overnight_pipeline.py us_overnight_pipeline.py uk_overnight_pipeline.py"
set "PIPELINE_NAMES=AU US UK"
set "ALL_INTEGRATED=1"

for %%P in (%PIPELINES%) do (
    echo Checking: models\screening\%%P
    
    REM Check for LSTMTrainer import
    findstr /C:"from .lstm_trainer import LSTMTrainer" "models\screening\%%P" >nul 2>&1
    if errorlevel 1 (
        findstr /C:"from lstm_trainer import LSTMTrainer" "models\screening\%%P" >nul 2>&1
        if errorlevel 1 (
            echo   [X] LSTMTrainer import NOT FOUND
            set "ALL_INTEGRATED=0"
        ) else (
            echo   [OK] LSTMTrainer import found
        )
    ) else (
        echo   [OK] LSTMTrainer import found
    )
    
    REM Check for _train_lstm_models method
    findstr /C:"def _train_lstm_models" "models\screening\%%P" >nul 2>&1
    if errorlevel 1 (
        echo   [X] _train_lstm_models method NOT FOUND
        set "ALL_INTEGRATED=0"
    ) else (
        echo   [OK] _train_lstm_models method found
    )
    
    REM Check for trainer initialization
    findstr /C:"self.trainer = LSTMTrainer" "models\screening\%%P" >nul 2>&1
    if errorlevel 1 (
        findstr /C:"self.lstm_trainer = LSTMTrainer" "models\screening\%%P" >nul 2>&1
        if errorlevel 1 (
            echo   [X] Trainer initialization NOT FOUND
            set "ALL_INTEGRATED=0"
        ) else (
            echo   [OK] Trainer initialization found
        )
    ) else (
        echo   [OK] Trainer initialization found
    )
    
    echo.
)

if "%ALL_INTEGRATED%"=="1" (
    echo [SUCCESS] All pipelines have LSTM training integrated!
    echo.
) else (
    echo [WARNING] Some pipelines are missing LSTM integration
    echo.
    echo This may cause LSTM training to fail in those pipelines.
    echo.
)

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 5: Summary and Recommendations
REM ──────────────────────────────────────────────────────────────────────────

echo [STEP 5] Summary and Recommendations
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   LSTM TRAINING STATUS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   [✓] FinBERT v4.4.4 Installation: OK
echo   [✓] Critical LSTM Files: OK
echo   [✓] Configuration File: OK
echo   [✓] Trainer Initialization: OK
if "%ALL_INTEGRATED%"=="1" (
    echo   [✓] Pipeline Integration ^(AU/US/UK^): OK
) else (
    echo   [!] Pipeline Integration ^(AU/US/UK^): PARTIAL
)
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   NEXT STEPS
echo ───────────────────────────────────────────────────────────────────────────
echo.
echo   To run LSTM training in overnight pipelines:
echo.
echo   1. AU Pipeline:
echo      LAUNCH_COMPLETE_SYSTEM.bat
echo      Choose: [1] Run AU Overnight Pipeline
echo.
echo   2. US Pipeline:
echo      LAUNCH_COMPLETE_SYSTEM.bat
echo      Choose: [2] Run US Overnight Pipeline
echo.
echo   3. UK Pipeline:
echo      LAUNCH_COMPLETE_SYSTEM.bat
echo      Choose: [3] Run UK Overnight Pipeline
echo.
echo   LSTM training occurs automatically in Phase 4.5 of each pipeline.
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   OPTIONAL: Test Single Model Training
echo ───────────────────────────────────────────────────────────────────────────
echo.
echo   Want to test LSTM training with a single stock? ^(Y/N^)
set /p "TEST_TRAINING="

if /i "%TEST_TRAINING%"=="Y" (
    echo.
    echo Enter stock symbol to test ^(e.g., CBA.AX for AU, AAPL for US, HSBA.L for UK^):
    set /p "TEST_SYMBOL="
    
    if not "!TEST_SYMBOL!"=="" (
        echo.
        echo Testing LSTM training for: !TEST_SYMBOL!
        echo This may take 1-3 minutes...
        echo.
        
        python -c "import sys; sys.path.insert(0, 'models/screening'); from lstm_trainer import LSTMTrainer; trainer = LSTMTrainer(); result = trainer.train_single_model('!TEST_SYMBOL!'); print(f\"Training result: {result.get('status')}\"); print(f\"Time: {result.get('training_time', 0):.1f}s\")"
        
        if errorlevel 1 (
            echo.
            echo [ERROR] Training test failed
            echo See error output above for details.
        ) else (
            echo.
            echo [SUCCESS] Training test completed
            echo Check logs\lstm_training\ for detailed results.
        )
    )
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   LSTM TRAINING VERIFICATION COMPLETE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
