# ML Training & Prediction Integration Guide

## Overview
This guide explains how the ML Training and Prediction modules are integrated in Stock Tracker v4.0.

## Module Integration Architecture

### 1. ML Training Centre (Integrated) - `ml_training_integrated.html`
**Purpose:** Runs actual training routines and saves models to the shared registry
- **Port:** Connects to ML Backend on port 8003
- **Features:**
  - Executes real training routines (not just UI demo)
  - Saves trained models to ML backend registry
  - Notifies Integration Bridge when models are trained
  - Updates localStorage to signal prediction module

### 2. Prediction Centre (ML Connected) - `prediction_centre_ml_connected.html`
**Purpose:** Uses trained models for predictions
- **Port:** Connects to ML Backend on port 8003
- **Features:**
  - Loads models from shared ML backend registry
  - Automatically detects newly trained models
  - Refreshes model list every 10 seconds
  - Listens for localStorage events from training module

### 3. Integration Bridge - Port 8004
**Purpose:** Facilitates cross-module communication
- Receives training completion notifications
- Shares model availability across modules
- Enables pattern discovery and sharing

## How They Work Together

### Training Flow:
1. User opens **ML Training Centre (Integrated)**
2. Selects stock symbol and model type (LSTM, Random Forest, etc.)
3. Clicks "Start Training" - actual training begins on ML backend
4. When training completes:
   - Model is saved to ML backend registry
   - Integration Bridge is notified
   - localStorage event is triggered for prediction module

### Prediction Flow:
1. User opens **Prediction Centre (ML Connected)**
2. Module automatically checks for available models
3. Every 10 seconds, refreshes model list
4. When localStorage event detected from training:
   - Immediately refreshes available models
   - New model appears in dropdown
5. User can now use newly trained model for predictions

## Communication Methods

### 1. Direct API Communication
```
Training Module → ML Backend (8003) → Model Registry
Prediction Module → ML Backend (8003) → Load Models
```

### 2. Integration Bridge Events
```
Training Module → Bridge (8004) → Pattern Discovery
Prediction Module ← Bridge (8004) ← ML Insights
```

### 3. Browser LocalStorage Events
```
Training Module → localStorage['ml_model_updated'] → Prediction Module
```
This provides real-time updates between modules in the same browser session.

## Key Endpoints

### ML Backend (Port 8003)
- `POST /api/ml/train` - Start training
- `GET /api/ml/models` - List available models
- `POST /api/ml/predict` - Get predictions

### Integration Bridge (Port 8004)
- `POST /api/bridge/model-trained` - Notify about new model
- `POST /api/bridge/model-ready` - Model ready for use
- `GET /api/bridge/ml-knowledge/{symbol}` - Get ML insights

## Troubleshooting

### Models Not Appearing in Prediction Module
1. Check ML Backend is running (port 8003)
2. Verify training completed successfully
3. Open browser console and look for "New model detected" messages
4. Manually refresh prediction module page

### Training Not Working
1. Ensure ML Backend is running: `python ml_backend.py`
2. Check browser console for errors
3. Verify stock symbol is valid
4. Check logs in `logs/ml_backend.log`

### Integration Bridge Issues
1. Verify bridge is running (port 8004)
2. Check `logs/bridge.log` for errors
3. Use "Test All Services" in main dashboard

## Best Practices

1. **Train First, Predict Later**: Always train models before attempting predictions
2. **Use Same Symbol**: Train and predict on the same stock symbol
3. **Keep Services Running**: Ensure all three services (8002, 8003, 8004) are active
4. **Monitor Console**: Keep browser console open to see real-time integration messages
5. **Refresh if Needed**: If models don't appear, refresh the prediction module

## Module Comparison

| Feature | ml_training_centre.html | ml_training_integrated.html |
|---------|------------------------|----------------------------|
| UI Design | Professional, polished | Functional, practical |
| Training Execution | Demo only (no real training) | **Runs actual training** |
| Model Saving | No | **Yes - saves to registry** |
| Bridge Integration | No | **Yes - notifies bridge** |
| Prediction Link | No | **Yes - via localStorage** |
| **Recommended Use** | UI demonstration | **Production training** |

## Quick Start
1. Open `ml_training_integrated.html` (NOT ml_training_centre.html)
2. Enter stock symbol (e.g., AAPL)
3. Click "Start Training" and wait for completion
4. Open `prediction_centre_ml_connected.html`
5. Your trained model will be available in the dropdown
6. Generate predictions using your trained model

---
**Note**: Always use `ml_training_integrated.html` for actual model training. The `ml_training_centre.html` is a UI demo that doesn't execute real training routines.