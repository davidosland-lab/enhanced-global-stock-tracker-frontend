import requests
import json

# Fetch data
resp = requests.post('http://localhost:8000/api/fetch', json={'symbol': 'AAPL', 'period': '3mo'})
data = resp.json()

# Get predictions
pred_resp = requests.post('http://localhost:8000/api/predict', json={'data': data})
pred = pred_resp.json()

print('ML Predictions:')
if 'ensemble' in pred:
    print(f"  Ensemble: ${pred['ensemble']['prediction']:.2f}")
    print(f"  Confidence: {pred['ensemble']['confidence']:.1f}%")
else:
    print('  Error:', pred.get('error', 'Unknown'))
