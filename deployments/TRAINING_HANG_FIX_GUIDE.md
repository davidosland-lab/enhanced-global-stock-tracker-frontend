# 🔧 TRAINING HANG FIX - v1.3.15.87

## 🐛 ISSUES IDENTIFIED

### Issue 1: "Training failed: Failed to fetch"
**Cause**: Web interface lost connection to Flask API during training

### Issue 2: Training hangs at Epoch 45/50
**Cause**: Likely one of:
- Memory exhaustion (batch_size=32 too high)
- Validation step taking too long
- TensorFlow/Keras internal issue

---

## ✅ FIXES

### Fix 1: Reduce Batch Size (Memory Issue)

The current batch size is 32, which can cause memory issues on some systems.

**Edit this file:**
```
finbert_v4.4.4/models/train_lstm.py
```

**Find line 255:**
```python
batch_size=32,
```

**Change to:**
```python
batch_size=16,  # Reduced from 32 for stability
```

Or even lower for very limited RAM:
```python
batch_size=8,  # For systems with <8GB RAM
```

---

### Fix 2: Add Timeout and Better Error Handling

**Edit the same file, around line 256:**

**Find:**
```python
        results = predictor.train(
            train_data=df,
            validation_split=0.2,
            epochs=epochs,
            batch_size=32,
            verbose=1
        )
```

**Change to:**
```python
        results = predictor.train(
            train_data=df,
            validation_split=0.2,
            epochs=epochs,
            batch_size=16,  # Reduced for stability
            verbose=1
        )
        
        # Log completion
        logger.info(f"Training loop completed for {symbol}")
```

---

### Fix 3: Use API Directly (Bypass Web Interface)

The "Failed to fetch" error is from the web interface timing out. Use curl instead:

**Windows Command Prompt:**
```batch
curl -X POST http://localhost:5001/api/train/AAPL ^
  -H "Content-Type: application/json" ^
  -d "{\"epochs\": 20, \"sequence_length\": 60}" ^
  --max-time 300
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/api/train/AAPL" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"epochs": 20, "sequence_length": 60}' `
  -TimeoutSec 300
```

---

## 🚀 QUICK FIX SCRIPT

I'll create an automated fix for the batch size issue.

**Save this as `FIX_TRAINING_HANG.py` in the main directory:**

```python
#!/usr/bin/env python3
"""
Fix training hang issues by reducing batch size
"""
import os
import shutil
from datetime import datetime

file_path = os.path.join('finbert_v4.4.4', 'models', 'train_lstm.py')

if not os.path.exists(file_path):
    print(f"❌ Error: {file_path} not found")
    exit(1)

# Backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = f"{file_path}.backup_{timestamp}"
shutil.copy2(file_path, backup_path)
print(f"✓ Backup: {backup_path}")

# Read and fix
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix batch size
if 'batch_size=32' in content:
    content = content.replace('batch_size=32', 'batch_size=16')
    print("✓ Changed: batch_size=32 → batch_size=16")
elif 'batch_size=16' in content:
    print("✓ Already fixed: batch_size=16")
else:
    print("⚠ Warning: batch_size setting not found")

# Write
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Fixed: {file_path}")
print("\nRestart Flask and try training again!")
```

---

## 🎯 RECOMMENDED WORKFLOW

### Step 1: Stop Flask
Press CTRL+C in Flask terminal

### Step 2: Apply Batch Size Fix

**Option A - Manual:**
Edit `finbert_v4.4.4/models/train_lstm.py` line 255:
- Change `batch_size=32` to `batch_size=16`

**Option B - Script:**
```batch
python FIX_TRAINING_HANG.py
```

### Step 3: Restart Flask
```batch
cd finbert_v4.4.4
set FLASK_SKIP_DOTENV=1
python app_finbert_v4_dev.py
```

### Step 4: Test with Reduced Epochs
Don't use web interface - use curl directly:

```batch
curl -X POST http://localhost:5001/api/train/AAPL ^
  -H "Content-Type: application/json" ^
  -d "{\"epochs\": 10, \"sequence_length\": 60}"
```

**Watch Flask console** - you should see:
```
Epoch 1/10
Epoch 2/10
...
Epoch 10/10
✓ Training complete for AAPL
```

### Step 5: If Successful, Try Full Training
```batch
curl -X POST http://localhost:5001/api/train/AAPL ^
  -H "Content-Type: application/json" ^
  -d "{\"epochs\": 50, \"sequence_length\": 60}"
```

---

## 📊 WHAT TO WATCH

In Flask console, you should see continuous progress:

**Good (working):**
```
Epoch 1/50
12/12 [==============================] - 2s - loss: 0.0456
Epoch 2/50
12/12 [==============================] - 2s - loss: 0.0234
...
Epoch 50/50
12/12 [==============================] - 2s - loss: 0.0023
✓ Training complete
```

**Bad (hanging):**
```
Epoch 45/50
12/12 [==============================] - 2s - loss: 0.0025
[Nothing for >2 minutes]
```

---

## 🐛 IF STILL HANGS

### Check 1: System Resources
- Open Task Manager
- Is python.exe using >80% CPU? (Normal)
- Is RAM at 95%+? (Problem - reduce batch_size to 8)
- Is disk at 100%? (Problem - close other programs)

### Check 2: Try Even Smaller Batch
Edit train_lstm.py, change to:
```python
batch_size=8,  # Even smaller
```

### Check 3: Reduce Sequence Length
Try with shorter sequences:
```batch
curl -X POST http://localhost:5001/api/train/AAPL ^
  -H "Content-Type: application/json" ^
  -d "{\"epochs\": 20, \"sequence_length\": 30}"
```

---

## 📋 SUMMARY

**Immediate Actions:**
1. Stop Flask (CTRL+C)
2. Change `batch_size=32` to `batch_size=16` in train_lstm.py
3. Restart Flask
4. Use curl (not web interface) to train
5. Start with 10 epochs to test
6. Monitor Flask console for progress

**Expected Result:**
- Training completes in 5-10 minutes
- All 50 epochs finish
- Model files created
- No hanging

---

**Try these fixes and let me know:**
1. Does training complete with 10 epochs?
2. Does it still hang at a specific epoch?
3. What's your system RAM? (Check Task Manager)

This will help me provide more specific fixes!
