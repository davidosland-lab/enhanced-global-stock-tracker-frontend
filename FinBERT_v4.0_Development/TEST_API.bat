@echo off
echo =====================================
echo   TESTING FINBERT API
echo =====================================
echo.

echo Testing health endpoint...
curl -s "http://localhost:5000/api/health" | python -m json.tool
echo.

echo Testing AAPL stock data...
curl -s "http://localhost:5000/api/stock/AAPL" | python -c "import json, sys; data = json.load(sys.stdin); print('Symbol:', data.get('symbol')); print('Current Price: $' + str(data.get('current_price'))); print('Day High: $' + str(data.get('day_high'))); print('Day Low: $' + str(data.get('day_low'))); ml = data.get('ml_prediction', {}); print('ML Prediction:', ml.get('prediction'), 'with', str(ml.get('confidence')) + '%% confidence'); sent = data.get('sentiment_analysis', {}); print('Sentiment:', sent.get('sentiment_label'), 'with', str(sent.get('confidence')) + '%% confidence')"
echo.
pause