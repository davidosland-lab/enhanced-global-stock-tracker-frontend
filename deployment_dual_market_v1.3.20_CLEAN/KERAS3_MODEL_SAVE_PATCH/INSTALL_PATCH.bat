@echo off
echo ================================================================================
echo           KERAS 3 MODEL SAVE FIX - PATCH INSTALLER
echo ================================================================================
echo.
echo This fixes models saving to same file causing overwrites.
echo.
pause

if not exist "finbert_v4.4.4\models" (
    echo ERROR: finbert_v4.4.4\models not found!
    echo Please run from C:\Users\david\AATelS
    pause
    exit /b 1
)

echo Creating backup...
set "BACKUP_DIR=finbert_v4.4.4\models\BACKUP_%date:~-4,4%%date:~-7,2%%date:~-10,2%"
mkdir "%BACKUP_DIR%" 2>nul
copy "finbert_v4.4.4\models\lstm_predictor.py" "%BACKUP_DIR%\" >nul 2>&1
copy "finbert_v4.4.4\models\train_lstm.py" "%BACKUP_DIR%\" >nul 2>&1
echo Backup complete: %BACKUP_DIR%
echo.

echo Installing fixed files...
copy /Y "KERAS3_MODEL_SAVE_PATCH\finbert_v4.4.4\models\lstm_predictor.py" "finbert_v4.4.4\models\" >nul
copy /Y "KERAS3_MODEL_SAVE_PATCH\finbert_v4.4.4\models\train_lstm.py" "finbert_v4.4.4\models\" >nul
echo Files installed!
echo.

echo Verifying installation...
python KERAS3_MODEL_SAVE_PATCH\verification\verify_fix.py
echo.

echo ================================================================================
echo Installation complete!
echo.
echo Next: Test with python finbert_v4.4.4\models\train_lstm.py --symbol BHP.AX --epochs 5
echo ================================================================================
pause
