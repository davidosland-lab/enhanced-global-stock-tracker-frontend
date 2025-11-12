import requests
import json

# Test optimization endpoint
url = "http://localhost:5001/api/backtest/optimize"

data = {
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-10-31",
    "model_type": "ensemble",
    "initial_capital": 10000,
    "optimization_method": "random",
    "max_iterations": 5  # Quick test with 5 iterations
}

print("Testing optimization endpoint...")
print(f"POST {url}")
print(f"Request: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, timeout=120)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Optimization completed!")
        print(f"\nBest Parameters: {json.dumps(result.get('best_parameters', {}), indent=2)}")
        print(f"\nBest Performance: {json.dumps(result.get('best_performance', {}), indent=2)}")
        print(f"\nIterations: {result.get('iterations_completed', 0)}")
    else:
        print(f"\n❌ Error: {response.text}")
except Exception as e:
    print(f"\n❌ Request failed: {e}")
