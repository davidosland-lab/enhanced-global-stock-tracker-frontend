import requests
import json

base_url = "http://localhost:8000"

# Test with SPY
print("Testing with SPY (S&P 500 ETF)...")
print("=" * 50)

response = requests.post(f"{base_url}/api/fetch", 
    json={"symbol": "SPY", "period": "3mo", "dataSource": "yahoo"})

if response.status_code == 200:
    data = response.json()
    print(f"1. Data Fetch: ✓")
    print(f"   - Symbol: {data['symbol']}")
    print(f"   - Current Price: ${data['current_price']:.2f}")
    print(f"   - Data Points: {len(data['prices'])}")
    print(f"   - Source: {data['data_source']}")
    
    # Test indicators
    ind_response = requests.post(f"{base_url}/api/indicators",
        json={"prices": data['prices'], "volumes": data.get('volume')})
    
    if ind_response.status_code == 200:
        indicators = ind_response.json()
        print(f"\n2. Technical Indicators: ✓")
        for key, value in indicators.items():
            if value is not None:
                print(f"   - {key}: {value:.2f}")
                if len([k for k, v in indicators.items() if v is not None]) >= 5:
                    break
    
    # Test predictions
    pred_response = requests.post(f"{base_url}/api/predict",
        json={"data": data})
    
    if pred_response.status_code == 200:
        predictions = pred_response.json()
        print(f"\n3. ML Predictions: ✓")
        if 'error' not in predictions or 'note' in predictions:
            print(f"   - Current: ${predictions.get('current_price', 0):.2f}")
            print(f"   - Predicted: ${predictions.get('ensemble', 0):.2f}")
            print(f"   - Change: {predictions.get('predicted_change', 0):.2f}%")
            print(f"   - Confidence: {predictions.get('confidence', 0)*100:.1f}%")
            print(f"   - Recommendation: {predictions.get('recommendation', 'N/A')}")
            if 'note' in predictions:
                print(f"   - Note: {predictions['note']}")
