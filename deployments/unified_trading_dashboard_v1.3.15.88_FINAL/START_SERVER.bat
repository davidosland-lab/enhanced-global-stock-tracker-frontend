@echo off
REM ============================================================================
REM  FinBERT v4.4.4 - Server Startup Script
REM ============================================================================

echo.
echo ============================================================================
echo   Starting FinBERT v4.4.4 Server
echo ============================================================================
echo.

REM Set Keras backend to TensorFlow (critical for LSTM training)
set KERAS_BACKEND=tensorflow

REM Skip .env file loading (avoids encoding issues)
set FLASK_SKIP_DOTENV=1

REM Start Flask server
python app_finbert_v4_dev.py

pause
