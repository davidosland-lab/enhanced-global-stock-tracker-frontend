import requests
import json

resp = requests.post('http://localhost:8000/api/fetch', json={'symbol': 'AAPL', 'period': '3mo'})
data = resp.json()

pred_resp = requests.post('http://localhost:8000/api/predict', json={'data': data})
pred = pred_resp.json()

print('Prediction response:', json.dumps(pred, indent=2)[:500])
