#!/usr/bin/env python3
"""
Test importing the main app to find the exact error
"""

import os
import sys

# Set environment
os.environ['FLASK_SKIP_DOTENV'] = '1'
os.environ['YFINANCE_CACHE_DISABLE'] = '1'

print("="*60)
print("TESTING IMPORTS FROM MAIN APP")
print("="*60)

try:
    print("\n1. Testing basic imports...")
    import numpy as np
    print(f"   ✓ numpy {np.__version__}")
    import pandas as pd
    print(f"   ✓ pandas {pd.__version__}")
    import yfinance as yf
    print(f"   ✓ yfinance {yf.__version__}")
    import flask
    print(f"   ✓ flask {flask.__version__}")
    
    print("\n2. Testing FinBERT imports...")
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    print(f"   ✓ transformers imported")
    import torch
    print(f"   ✓ torch {torch.__version__}")
    
    print("\n3. Testing other imports...")
    import ta
    print(f"   ✓ ta imported")
    import feedparser
    print(f"   ✓ feedparser imported")
    from sklearn.ensemble import RandomForestClassifier
    print(f"   ✓ sklearn imported")
    
    print("\n4. Attempting to import the main app...")
    import app_finbert_ultimate_original_with_key
    print("   ✓ Main app imported successfully!")
    
    print("\n5. Testing FinBERT model load...")
    model_name = "ProsusAI/finbert"
    print(f"   Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("   ✓ Tokenizer loaded")
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    print("   ✓ Model loaded")
    
    print("\n✅ ALL IMPORTS SUCCESSFUL - The app should work!")
    
except Exception as e:
    print(f"\n❌ ERROR FOUND: {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    
    print("\n" + "="*60)
    print("This is the error preventing the app from starting.")
    print("="*60)

input("\nPress Enter to exit...")