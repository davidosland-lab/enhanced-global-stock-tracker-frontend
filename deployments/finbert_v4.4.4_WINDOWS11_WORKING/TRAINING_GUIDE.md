# LSTM Training Guide - FinBERT v4.4.4

## 🎯 Quick Start

### Train via Web UI
1. Open `http://localhost:5001`
2. Enter symbol: `AAPL`
3. Set epochs: `50`
4. Click "Train Model"
5. Wait 30-60 seconds

### Train via Command Line
```batch
python models\train_lstm.py --symbol AAPL --epochs 50
```

### Train via API
```batch
curl -X POST http://localhost:5001/api/train/AAPL ^
     -H "Content-Type: application/json" ^
     -d "{\"epochs\": 50, \"sequence_length\": 60}"
```

---

## 📊 What You'll See

### Successful Training
```
INFO:models.train_lstm:Starting LSTM training for AAPL
INFO:models.train_lstm:Fetching training data for AAPL (period: 2y)
INFO:models.train_lstm:✓ Successfully fetched 502 days of data
INFO:models.train_lstm:✓ Data validation passed: 502 data points
INFO:models.train_lstm:✓ Features prepared: 8 features
INFO:models.train_lstm:Starting training on 8 features...

Epoch 1/50
12/12 [==============================] - 2s 15ms/step - loss: 0.0234 - mae: 0.0156 - val_loss: 0.0198
Epoch 2/50
12/12 [==============================] - 0s 12ms/step - loss: 0.0198 - mae: 0.0132 - val_loss: 0.0167
Epoch 3/50
12/12 [==============================] - 0s 11ms/step - loss: 0.0178 - mae: 0.0119 - val_loss: 0.0145
...
Epoch 50/50
12/12 [==============================] - 0s 11ms/step - loss: 0.0089 - mae: 0.0067 - val_loss: 0.0091

INFO:models.train_lstm:✓ Training complete for AAPL
INFO:models.train_lstm:✓ Model saved to models/lstm_AAPL.keras
INFO:models.train_lstm:✓ Metadata saved to models/lstm_AAPL_metadata.json
```

### Key Indicators
- ✅ **Epoch progress**: Shows each epoch completing
- ✅ **Loss decreasing**: Final loss < 0.01 is good
- ✅ **Validation loss**: Should be close to training loss
- ✅ **Time**: 30-60 seconds for 50 epochs

---

## 🎛️ Training Parameters

### Epochs
- **Default**: 50
- **Range**: 10-100
- **Recommendation**: 
  - Testing: 10-20 (faster)
  - Production: 50-100 (more accurate)

### Sequence Length
- **Default**: 60
- **Range**: 30-120
- **Recommendation**: 60 (2-3 months of trading days)

### Example Configurations

**Fast Testing**:
```json
{
  "epochs": 10,
  "sequence_length": 30
}
```

**Balanced**:
```json
{
  "epochs": 50,
  "sequence_length": 60
}
```

**High Accuracy**:
```json
{
  "epochs": 100,
  "sequence_length": 90
}
```

---

## 📈 Supported Stocks

### US Stocks (240)
```
AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, JPM, BAC, WFC, etc.
```

### Australian Stocks (240) - Use .AX suffix
```
BHP.AX, CBA.AX, WBC.AX, ANZ.AX, NAB.AX, RIO.AX, CSL.AX, etc.
```

### UK Stocks (240) - Use .L suffix
```
HSBA.L, BP.L, SHEL.L, ULVR.L, AZN.L, GSK.L, BARC.L, etc.
```

**Total**: 720 stocks

---

## 🔍 Verification

### Check Model File
```batch
dir models\lstm_AAPL.keras
```

Should show file with size ~1-2 MB

### Check Metadata
```batch
type models\lstm_AAPL_metadata.json
```

Should show:
```json
{
  "symbol": "AAPL",
  "training_date": "2026-02-05T...",
  "data_points": 502,
  "features": ["close", "volume", "high", "low", "open", "sma_20", "rsi", "macd"],
  "sequence_length": 60,
  "epochs": 50,
  "results": {
    "status": "success",
    "epochs_trained": 50,
    "final_loss": 0.0089,
    "final_val_loss": 0.0091,
    "model_path": "models/lstm_AAPL.keras"
  }
}
```

### Test Prediction
```batch
curl http://localhost:5001/api/stock/AAPL
```

Should include LSTM predictions in response.

---

## ❌ Troubleshooting

### No Epoch Progress Shown

**Symptom**: Training says "complete" but no epochs displayed

**Cause**: Old cached model or TensorFlow not available

**Fix**:
```batch
# Delete old models
cd models
del lstm_AAPL.*

# Verify TensorFlow
python -c "import tensorflow as tf; print(tf.__version__)"

# Restart server
START_SERVER.bat
```

### RuntimeError: Can't call numpy() on Tensor

**Cause**: Keras backend set to PyTorch

**Fix**:
```batch
# Check backend
python -c "import keras; print(keras.backend.backend())"

# Should output: tensorflow

# If not, copy keras.json
copy keras.json %USERPROFILE%\.keras\keras.json

# Restart with proper environment
START_SERVER.bat
```

### Training Fails: Insufficient Data

**Cause**: Stock doesn't have 2 years of history

**Fix**: Choose a different stock with more history

### Training Hangs at Specific Epoch

**Cause**: Memory or disk I/O bottleneck

**Fix**:
- Reduce batch size (edit `lstm_predictor.py`)
- Close other applications
- Reduce epochs to 20-30

---

## 🎯 Batch Training

### Train Multiple Stocks

Create `train_batch.py`:
```python
import requests
import time

stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

for stock in stocks:
    print(f"Training {stock}...")
    response = requests.post(
        f'http://localhost:5001/api/train/{stock}',
        json={'epochs': 50}
    )
    print(f"  Result: {response.json()['status']}")
    time.sleep(5)  # Wait between trainings

print("Batch training complete!")
```

Run:
```batch
python train_batch.py
```

---

## 📊 Expected Training Times

| Epochs | Time (approx) |
|--------|---------------|
| 10     | 10-15 seconds |
| 20     | 20-30 seconds |
| 50     | 30-60 seconds |
| 100    | 60-120 seconds |

*Times vary based on CPU speed and data size*

---

## 🎉 Success Checklist

After training, verify:

- [ ] Epoch progress shown (Epoch 1/50, 2/50, etc.)
- [ ] Loss values decrease over epochs
- [ ] Final loss < 0.01
- [ ] Model file created (*.keras)
- [ ] Metadata file created (*_metadata.json)
- [ ] Metadata shows today's date
- [ ] Metadata shows "status": "success"
- [ ] Predictions include LSTM component

---

**You're ready to train all 720 stocks!** 🚀
