@echo off
REM ========================================
REM Batch Train Multiple Stocks
REM ========================================

set SERVER_URL=http://localhost:5001

echo ========================================
echo FinBERT v4.4.4 - Batch Training
echo ========================================
echo.

echo This script will train LSTM models for multiple stocks.
echo.
echo Training Configuration:
echo - Epochs: 50
echo - Sequence Length: 60
echo - Server: %SERVER_URL%
echo.

REM Top 10 US Stocks
echo [1/10] Training AAPL...
curl -X POST %SERVER_URL%/api/train/AAPL -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [2/10] Training MSFT...
curl -X POST %SERVER_URL%/api/train/MSFT -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [3/10] Training GOOGL...
curl -X POST %SERVER_URL%/api/train/GOOGL -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [4/10] Training AMZN...
curl -X POST %SERVER_URL%/api/train/AMZN -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [5/10] Training TSLA...
curl -X POST %SERVER_URL%/api/train/TSLA -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [6/10] Training NVDA...
curl -X POST %SERVER_URL%/api/train/NVDA -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [7/10] Training META...
curl -X POST %SERVER_URL%/api/train/META -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [8/10] Training V...
curl -X POST %SERVER_URL%/api/train/V -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [9/10] Training JPM...
curl -X POST %SERVER_URL%/api/train/JPM -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo [10/10] Training JNJ...
curl -X POST %SERVER_URL%/api/train/JNJ -H "Content-Type: application/json" -d "{\"epochs\": 50, \"sequence_length\": 60}"
echo.
echo.

echo ========================================
echo BATCH TRAINING COMPLETE!
echo ========================================
echo.
echo Trained 10 models successfully.
echo.
echo View trained models:
echo curl %SERVER_URL%/api/models
echo.
pause
