import requests
import json

base_url = "http://localhost:8000"

# Test fetching AAPL data
print("1. Fetching AAPL data...")
response = requests.post(f"{base_url}/api/fetch", 
    json={"symbol": "AAPL", "period": "1mo", "dataSource": "auto"})

if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Got {len(data['prices'])} price points")
    print(f"   Current price: ${data['current_price']:.2f}")
    
    # Test indicators
    print("\n2. Calculating indicators...")
    ind_response = requests.post(f"{base_url}/api/indicators",
        json={"prices": data['prices'], "volumes": data.get('volume')})
    
    if ind_response.status_code == 200:
        indicators = ind_response.json()
        print(f"   ✓ Got {len(indicators)} indicators")
        for key, value in list(indicators.items())[:5]:
            if value is not None:
                print(f"   - {key}: {value:.2f}")
    else:
        print(f"   ✗ Indicators failed: {ind_response.text}")
    
    # Test predictions
    print("\n3. Getting ML predictions...")
    pred_response = requests.post(f"{base_url}/api/predict",
        json={"data": data})
    
    if pred_response.status_code == 200:
        predictions = pred_response.json()
        if 'error' not in predictions:
            print(f"   ✓ Prediction: ${predictions.get('ensemble', 'N/A')}")
            print(f"   ✓ Confidence: {predictions.get('confidence', 0)*100:.1f}%")
            print(f"   ✓ Recommendation: {predictions.get('recommendation', 'N/A')}")
        else:
            print(f"   ⚠ Prediction error: {predictions['error']}")
    else:
        print(f"   ✗ Prediction failed: {pred_response.text}")
else:
    print(f"   ✗ Fetch failed: {response.text}")
