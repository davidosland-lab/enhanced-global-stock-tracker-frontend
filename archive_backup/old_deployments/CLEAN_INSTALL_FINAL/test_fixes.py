import requests
import time

print("Testing Fixed Endpoints...")
print("=" * 50)

# Test backend status
try:
    resp = requests.get("http://localhost:8002/api/status")
    if resp.status_code == 200:
        print("✅ Backend status: ONLINE")
    else:
        print("❌ Backend status: ERROR")
except:
    print("❌ Backend not running on port 8002")

# Test batch download endpoint
try:
    resp = requests.post("http://localhost:8002/api/historical/batch-download")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Batch download: {data.get('count', 0)} symbols")
    else:
        print(f"❌ Batch download: Status {resp.status_code}")
except:
    print("❌ Batch download endpoint not working")

# Test CBA.AX price
try:
    resp = requests.get("http://localhost:8002/api/stock/CBA.AX")
    if resp.status_code == 200:
        data = resp.json()
        price = data.get('price', 0)
        if 150 < price < 200:
            print(f"✅ CBA.AX price: ${price:.2f} (realistic)")
        else:
            print(f"⚠️  CBA.AX price: ${price:.2f} (seems wrong)")
    else:
        print("❌ Cannot fetch CBA.AX")
except:
    print("❌ Error fetching CBA.AX")

print("\nTest complete!")
