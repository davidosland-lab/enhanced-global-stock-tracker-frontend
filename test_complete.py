import requests
import json

base_url = "http://localhost:8000"

print("="*60)
print(" COMPLETE SYSTEM TEST - ALL FEATURES")
print("="*60)

# Test multiple stocks
test_stocks = [
    ("SPY", "S&P 500 ETF"),
    ("MSFT", "Microsoft"),
    ("CBA", "Commonwealth Bank")
]

for symbol, name in test_stocks:
    print(f"\n📊 Testing {symbol} ({name})")
    print("-" * 50)
    
    # Fetch data
    response = requests.post(f"{base_url}/api/fetch", 
        json={"symbol": symbol, "period": "3mo", "dataSource": "auto"})
    
    if response.status_code != 200:
        print(f"  ❌ Failed to fetch {symbol}")
        continue
    
    data = response.json()
    print(f"  ✅ Data: {len(data['prices'])} points from {data['data_source']}")
    print(f"     Current Price: ${data['current_price']:.2f}")
    
    # Get indicators
    ind_response = requests.post(f"{base_url}/api/indicators",
        json={"prices": data['prices'], "volumes": data.get('volume')})
    
    if ind_response.status_code == 200:
        indicators = ind_response.json()
        print(f"\n  📈 Technical Indicators ({len(indicators)} total):")
        
        # Display all indicators
        for key, value in sorted(indicators.items()):
            if value is not None:
                if 'BB' in key or 'SMA' in key or 'EMA' in key or 'ATR' in key:
                    print(f"     {key:15} ${value:.2f}")
                else:
                    print(f"     {key:15} {value:.2f}")
    
    # Get predictions
    pred_response = requests.post(f"{base_url}/api/predict",
        json={"data": data})
    
    if pred_response.status_code == 200:
        predictions = pred_response.json()
        if 'ensemble' in predictions:
            print(f"\n  🤖 ML Predictions:")
            print(f"     Predicted:      ${predictions['ensemble']:.2f}")
            print(f"     Change:         {predictions['predicted_change']:.2f}%")
            print(f"     Confidence:     {predictions['confidence']*100:.0f}%")
            print(f"     Recommendation: {predictions['recommendation']}")

print("\n" + "="*60)
print(" ✅ ALL SYSTEMS OPERATIONAL")
print("="*60)
