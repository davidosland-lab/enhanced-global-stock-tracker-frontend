#!/usr/bin/env python3
"""
Test FinBERT Installation
"""

import sys
import os

print("="*60)
print("TESTING FINBERT INSTALLATION")
print("="*60)
print()

# Test 1: Check numpy
try:
    import numpy as np
    print(f"✓ NumPy {np.__version__} installed")
    if tuple(map(int, np.__version__.split('.')[:2])) >= (1, 26):
        print("  ✓ NumPy is Python 3.12 compatible")
    else:
        print("  ⚠ NumPy version may not be Python 3.12 compatible")
except ImportError as e:
    print(f"✗ NumPy not installed: {e}")
    sys.exit(1)

# Test 2: Check PyTorch
try:
    import torch
    print(f"✓ PyTorch {torch.__version__} installed")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    print(f"  Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
except ImportError as e:
    print(f"✗ PyTorch not installed: {e}")
    print("  Fix: pip install torch --index-url https://download.pytorch.org/whl/cpu")
    sys.exit(1)

# Test 3: Check transformers
try:
    import transformers
    print(f"✓ Transformers {transformers.__version__} installed")
except ImportError as e:
    print(f"✗ Transformers not installed: {e}")
    print("  Fix: pip install transformers")
    sys.exit(1)

# Test 4: Try to load FinBERT
print()
print("Testing FinBERT model loading...")
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    print("✓ Can import AutoTokenizer and AutoModel")
    
    # Try to initialize (won't download if not present)
    print("Attempting to initialize FinBERT tokenizer...")
    model_name = "ProsusAI/finbert"
    
    # This will download if not cached
    print(f"Loading tokenizer from {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./cache")
    print("✓ Tokenizer loaded successfully!")
    
    print(f"Loading model from {model_name}...")
    print("(This will download ~400MB on first run)")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir="./cache")
    print("✓ Model loaded successfully!")
    
    # Test inference
    print()
    print("Testing inference...")
    test_text = "Apple stock rises on strong earnings report"
    inputs = tokenizer(test_text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predictions = predictions.numpy()[0]
    
    print(f"Test text: '{test_text}'")
    print(f"Sentiment scores:")
    print(f"  Positive: {predictions[0]:.3f}")
    print(f"  Negative: {predictions[1]:.3f}")
    print(f"  Neutral:  {predictions[2]:.3f}")
    
    print()
    print("="*60)
    print("✓ FINBERT IS FULLY OPERATIONAL!")
    print("="*60)
    
except Exception as e:
    print(f"✗ Error loading FinBERT: {e}")
    print()
    print("Possible fixes:")
    print("1. Make sure PyTorch is installed first")
    print("2. Check internet connection for model download")
    print("3. Try reinstalling transformers")
    sys.exit(1)

print()
input("Press Enter to exit...")