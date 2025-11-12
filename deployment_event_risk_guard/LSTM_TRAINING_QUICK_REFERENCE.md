# LSTM Training - Quick Reference

## Training Parameters Summary

| Parameter | Default | Min-Max | Description |
|-----------|---------|---------|-------------|
| **Epochs** | 50 | 20-100 | Training iterations through dataset |
| **Sequence Length** | 60 days | 30-120 | Historical days for prediction |
| **Batch Size** | 32 | 16-64 | Samples per weight update |
| **Validation Split** | 20% | 10-30% | Data reserved for validation |
| **Training Data** | 2 years | 1y-5y | Historical data period |

---

## Quick Start Commands

### Train 10 Priority ASX Stocks (Recommended)
```batch
TRAIN_LSTM_OVERNIGHT.bat
```
**Time:** 1.5-2 hours  
**Stocks:** CBA.AX, ANZ.AX, NAB.AX, WBC.AX, MQG.AX, BHP.AX, RIO.AX, CSL.AX, WES.AX, BOQ.AX

### Custom Interactive Training
```batch
TRAIN_LSTM_CUSTOM.bat
```
**Options:**
- Pre-defined lists (US tech, ASX, UK FTSE)
- Manual symbol entry
- Load from file

### Train Single Stock
```batch
TRAIN_LSTM_SINGLE.bat CBA.AX
TRAIN_LSTM_SINGLE.bat AAPL
```
**Time:** 10-15 minutes per stock

---

## Parameter Recommendations by Use Case

### Standard Training (Most Users)
```
Epochs: 50
Sequence Length: 60 days
Batch Size: 32
Validation Split: 20%
Training Period: 2 years
Expected Time: 10-15 min/stock
```

### Quick Testing
```
Epochs: 20
Sequence Length: 40 days
Batch Size: 32
Validation Split: 15%
Training Period: 1 year
Expected Time: 4-6 min/stock
```

### High Accuracy
```
Epochs: 70-100
Sequence Length: 90 days
Batch Size: 32
Validation Split: 20%
Training Period: 5 years
Expected Time: 20-30 min/stock
```

### Low Memory Systems (8 GB RAM)
```
Epochs: 50
Sequence Length: 60 days
Batch Size: 16
Validation Split: 20%
Training Period: 2 years
Expected Time: 15-20 min/stock
```

---

## Training Output

### Success Indicators
✅ **Good Model:**
```
Final Loss: 0.0042
Validation Loss: 0.0038
Status: EXCELLENT (val < training, both low)
```

⚠️ **Acceptable Model:**
```
Final Loss: 0.0089
Validation Loss: 0.0112
Status: ACCEPTABLE (val slightly higher, still reasonable)
```

❌ **Poor Model (Retrain Needed):**
```
Final Loss: 0.0023
Validation Loss: 0.0245
Status: OVERFITTING (val >> training, retrain with less epochs)
```

---

## File Locations

### Trained Models
```
models/lstm_CBA.AX_model.keras        # Model file
models/lstm_CBA.AX_metadata.json      # Training metadata
```

### Training Logs
```
logs/screening/lstm_training.log      # Training execution log
logs/lstm_training/YYYY-MM-DD_training_log.jsonl  # Daily training log
```

---

## Common Adjustments

### Training Too Slow?
1. Reduce sequence length: 60 → 40 days
2. Reduce epochs: 50 → 30
3. Increase batch size: 32 → 64 (if RAM available)

### Poor Accuracy?
1. Increase epochs: 50 → 70
2. Increase training data: 2y → 5y
3. Increase sequence length: 60 → 90 days

### Out of Memory?
1. Reduce batch size: 32 → 16
2. Reduce sequence length: 60 → 40
3. Train fewer stocks at once

---

## Pre-defined Stock Lists

### Australian (ASX)
CBA.AX, BHP.AX, WBC.AX, ANZ.AX, NAB.AX, CSL.AX, WES.AX, FMG.AX

### US Tech
AAPL, MSFT, GOOGL, NVDA, AMD, INTC

### US Mega Caps
AAPL, MSFT, GOOGL, AMZN, META, TSLA

### UK FTSE
BP.L, SHEL.L, HSBA.L, ULVR.L, AZN.L

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| TensorFlow not installed | `pip install tensorflow>=2.13.0` |
| Training too slow | Reduce epochs to 30 |
| Out of memory | Reduce batch size to 16 |
| Model not improving | Increase epochs to 70 |
| Download errors | Check internet, retry later |

---

## Integration Notes

### Prediction Weights (LSTM Available)
- LSTM: 45%
- Trend Analysis: 25%
- Technical Indicators: 15%
- FinBERT Sentiment: 15%

### Prediction Weights (No LSTM)
- Trend Analysis: 40%
- Technical Indicators: 35%
- FinBERT Sentiment: 25%

### Event Risk Guard Impact
- Risk Score ≥ 0.8: 70% confidence haircut
- Risk Score ≥ 0.5: 45% confidence haircut
- Risk Score ≥ 0.25: 20% confidence haircut
- Skip Trading: Force HOLD (overrides LSTM)

---

## Performance Targets

### Training Time Targets
- Single stock: 10-15 minutes ✅
- 10 stocks: 1.5-2 hours ✅
- 20 stocks: 3-4 hours ✅

### Accuracy Targets
- Good model: Loss < 0.01 ✅
- Validation ratio: < 1.5 ✅
- Prediction improvement: +15-25% ✅

### Resource Limits
- RAM usage: 2-4 GB per stock ✅
- Disk space: 2-5 MB per model ✅
- CPU cores: 4+ recommended ✅

---

## Training Schedule Recommendations

### Monthly (Recommended)
```batch
REM First weekend of each month
TRAIN_LSTM_OVERNIGHT.bat
```

### After Major Events
```batch
REM Train affected stocks immediately
TRAIN_LSTM_SINGLE.bat CBA.AX
TRAIN_LSTM_SINGLE.bat NAB.AX
```

### Model Staleness Check
```python
# Models > 7 days old are considered stale
# Run overnight_pipeline.py to auto-detect stale models
python models/screening/overnight_pipeline.py
```

---

## Need More Details?

📖 **Full Documentation:** See `LSTM_TRAINING_GUIDE.md` (16 KB, comprehensive)

📋 **Deployment Guide:** See `README_DEPLOYMENT.md`

🔧 **Technical Details:** See `docs/EVENT_RISK_GUARD_IMPLEMENTATION.md`

---

**Last Updated:** 2025-11-12  
**System:** Event Risk Guard v1.0  
**Status:** Production Ready ✅
