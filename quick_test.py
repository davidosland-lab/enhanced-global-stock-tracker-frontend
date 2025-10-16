#!/usr/bin/env python3
"""Quick test to verify ML core is working"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing ML Core System...")

# 1. Check if service is running
try:
    r = requests.get(BASE_URL, timeout=2)
    if r.status_code == 200:
        print("✅ Service is running")
        data = r.json()
        print(f"   Version: {data.get('version', 'N/A')}")
        print(f"   Status: {data.get('status', 'N/A')}")
    else:
        print(f"❌ Service error: {r.status_code}")
except Exception as e:
    print(f"❌ Service not running: {e}")
    print("Starting service...")
    import subprocess
    subprocess.Popen(["python", "ml_core_enhanced_production.py"])
    import time
    time.sleep(5)

# 2. Test cache stats
try:
    r = requests.get(f"{BASE_URL}/api/cache/stats", timeout=2)
    if r.status_code == 200:
        print("✅ Cache working")
        data = r.json()
        print(f"   Hit rate: {data.get('hit_rate', 0):.1f}%")
except Exception as e:
    print(f"❌ Cache error: {e}")

# 3. Check models
try:
    r = requests.get(f"{BASE_URL}/api/models", timeout=2)
    if r.status_code == 200:
        models = r.json()
        print(f"✅ Models endpoint working ({len(models)} models)")
except Exception as e:
    print(f"❌ Models error: {e}")

print("\nCore system check complete!")