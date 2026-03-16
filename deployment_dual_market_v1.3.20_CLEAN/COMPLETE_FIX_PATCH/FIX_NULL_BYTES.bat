@echo off
echo ============================================================
echo     NULL BYTE CLEANER - Fix Corrupted Python Files
echo ============================================================
echo.
echo This script removes null bytes from Python files that may
echo have been corrupted during installation or editing.
echo.
echo Checking files...
echo.

cd "%~dp0\.."

echo Cleaning finbert_v4.4.4\models\lstm_predictor.py...
python -c "file='finbert_v4.4.4/models/lstm_predictor.py'; data=open(file,'rb').read(); nulls=data.count(b'\x00'); print(f'  Found {nulls} null bytes'); data_clean=data.replace(b'\x00',b''); open(file,'wb').write(data_clean); print('  ✓ Cleaned')"

echo.
echo Cleaning finbert_v4.4.4\models\train_lstm.py...
python -c "file='finbert_v4.4.4/models/train_lstm.py'; data=open(file,'rb').read(); nulls=data.count(b'\x00'); print(f'  Found {nulls} null bytes'); data_clean=data.replace(b'\x00',b''); open(file,'wb').write(data_clean); print('  ✓ Cleaned')"

echo.
echo Cleaning models\screening\finbert_bridge.py...
python -c "file='models/screening/finbert_bridge.py'; data=open(file,'rb').read(); nulls=data.count(b'\x00'); print(f'  Found {nulls} null bytes'); data_clean=data.replace(b'\x00',b''); open(file,'wb').write(data_clean); print('  ✓ Cleaned')"

echo.
echo ============================================================
echo Cleaning Complete!
echo ============================================================
echo.
echo Now clearing Python cache...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
echo Python cache cleared.
echo.
echo ============================================================
echo Next Steps:
echo ============================================================
echo 1. Run: python VERIFY_INSTALLATION.py
echo 2. Run: python web_ui.py
echo.
pause
