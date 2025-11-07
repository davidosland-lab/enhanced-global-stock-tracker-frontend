#!/usr/bin/env python3
"""
Download FinBERT model to cache
"""

print("="*60)
print("DOWNLOADING FINBERT MODEL")
print("="*60)
print("\nThis will download the FinBERT model (~400MB)")
print("This only needs to be done once.\n")

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    
    model_name = "ProsusAI/finbert"
    
    print(f"Downloading tokenizer from {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("✓ Tokenizer downloaded")
    
    print(f"\nDownloading model from {model_name}...")
    print("This may take a few minutes...")
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    print("✓ Model downloaded")
    
    # Test it
    print("\nTesting model...")
    text = "Apple stock rises on strong earnings"
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    print("✓ Model works!")
    
    print("\n" + "="*60)
    print("SUCCESS! FinBERT is ready to use.")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nThis might be a network issue. Make sure you have internet access.")
    print("The model needs to download from HuggingFace.")

input("\nPress Enter to exit...")