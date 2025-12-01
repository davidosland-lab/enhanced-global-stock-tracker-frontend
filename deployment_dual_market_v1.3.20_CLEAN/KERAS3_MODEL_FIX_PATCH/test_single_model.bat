@echo off
REM ============================================================================
REM Test Keras 3 Fix with Single Model Training
REM ============================================================================

echo.
echo ============================================================================
echo KERAS 3 FIX - SINGLE MODEL TEST
echo ============================================================================
echo.
echo This script will train ONE model (BHP.AX) with 5 epochs (~2-3 minutes)
echo to verify that the Keras 3 fix is working correctly.
echo.
echo Expected results:
echo   - Training completes successfully
echo   - File created: models\BHP.AX_lstm_model.h5 (~500KB)
echo   - File created: models\lstm_BHP.AX_metadata.json
echo   - Log shows: "Model saved to models/lstm_model.h5 (Keras 3 format)"
echo.
echo ============================================================================
echo.

pause

echo.
echo [STEP 1] Checking if fix is applied...
echo.

python verify_keras_fix.py
if errorlevel 1 (
    echo.
    echo [ERROR] Fix verification failed!
    echo Please run: install_keras_fix.bat first
    pause
    exit /b 1
)

echo.
echo [STEP 2] Training single model (BHP.AX with 5 epochs)...
echo.
echo This will take approximately 2-3 minutes...
echo.

python finbert_v4.4.4\models\train_lstm.py --symbol BHP.AX --epochs 5

if errorlevel 1 (
    echo.
    echo [ERROR] Training failed!
    echo Check logs: models\screening\logs\lstm_training.log
    pause
    exit /b 1
)

echo.
echo [STEP 3] Verifying model files were created...
echo.

if exist "models\BHP.AX_lstm_model.h5" (
    echo [OK] Model file created: models\BHP.AX_lstm_model.h5
    for %%A in (models\BHP.AX_lstm_model.h5) do (
        set size=%%~zA
        echo     File size: %%~zA bytes
    )
    
    REM Check if file is larger than 100KB (should be ~500KB)
    for %%A in (models\BHP.AX_lstm_model.h5) do (
        if %%~zA GTR 100000 (
            echo     [OK] File size is valid ^(^>100KB^)
        ) else (
            echo     [WARNING] File size seems small ^(should be ~500KB^)
        )
    )
) else (
    echo [ERROR] Model file NOT created!
    echo.
    echo This means the Keras 3 fix is not working properly.
    echo.
    echo Troubleshooting steps:
    echo 1. Check if fix was applied: python verify_keras_fix.py
    echo 2. Check training logs for errors
    echo 3. Try manual fix (see README.txt)
    pause
    exit /b 1
)

if exist "models\lstm_BHP.AX_metadata.json" (
    echo [OK] Metadata file created: models\lstm_BHP.AX_metadata.json
) else (
    echo [WARNING] Metadata file not found
)

echo.
echo ============================================================================
echo TEST PASSED!
echo ============================================================================
echo.
echo The Keras 3 fix is working correctly!
echo.
echo Files created:
if exist "models\BHP.AX_lstm_model.h5" echo   - models\BHP.AX_lstm_model.h5
if exist "models\lstm_BHP.AX_metadata.json" echo   - models\lstm_BHP.AX_metadata.json
echo.
echo You can now run the full pipeline with confidence:
echo   RUN_PIPELINE_TEST.bat
echo.
echo The pipeline will:
echo   - Train 139 models and SAVE them as .h5 files
echo   - Next run will LOAD existing models (fast!)
echo   - Runtime will be 30-45 minutes (instead of 2+ hours)
echo.
echo ============================================================================
echo.

pause
