# Installation Guide - FinBERT v4.0 Prediction System

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 11 (Windows 10 also compatible)
- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 500 MB free space
- **Internet**: Active connection for stock data

### Recommended Requirements
- **Operating System**: Windows 11 (latest updates)
- **Python**: 3.10 or 3.11
- **RAM**: 8 GB or more
- **Storage**: 2 GB free space (for models and cache)
- **Internet**: Broadband connection

## 🔧 Installation Steps

### Step 1: Install Python

1. **Download Python**
   - Visit: https://www.python.org/downloads/
   - Download Python 3.11.x (latest stable version)

2. **Install Python**
   - Run the installer
   - ✅ **IMPORTANT**: Check "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation**
   ```powershell
   # Open PowerShell and run:
   python --version
   # Should show: Python 3.11.x
   
   pip --version
   # Should show: pip 23.x.x
   ```

### Step 2: Extract the Package

1. **Locate the ZIP file**
   - Find: `FinBERT_v4.0_Windows11_Prediction_System.zip`

2. **Extract Files**
   - Right-click the ZIP file
   - Select "Extract All..."
   - Choose a location (e.g., `C:\FinBERT_v4.0\`)
   - Click "Extract"

3. **Verify Extraction**
   - Open the extracted folder
   - You should see:
     - `app_finbert_v4_dev.py`
     - `finbert_v4_enhanced_ui.html`
     - `requirements.txt`
     - `models/` folder
     - Documentation files

### Step 3: Install Dependencies

1. **Open PowerShell in the Extracted Folder**
   - Navigate to the extracted folder in File Explorer
   - Hold Shift + Right-click in empty space
   - Select "Open PowerShell window here" or "Open in Terminal"

2. **Install Basic Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
   
   This installs:
   - Flask (web framework)
   - yfinance (stock data)
   - pandas (data processing)
   - numpy (numerical computing)
   - APScheduler (task scheduling)

3. **Install Optional Dependencies (Recommended)**
   ```powershell
   # For LSTM neural networks
   pip install tensorflow
   
   # For FinBERT sentiment analysis
   pip install transformers torch
   
   # Alternative lightweight option
   pip install tensorflow-cpu  # CPU-only version
   ```

4. **Verify Installation**
   ```powershell
   python -c "import flask, yfinance, pandas; print('All dependencies installed!')"
   ```

### Step 4: First Run

1. **Start the Server**
   ```powershell
   python app_finbert_v4_dev.py
   ```

2. **Expected Output**
   ```
   ======================================================================
     FinBERT v4.0 Development Server - FULL AI/ML Experience
   ======================================================================
   
   🎯 Features:
   ○ LSTM Neural Networks: Available (needs training)
   ✓ FinBERT Sentiment: Active
   ✓ Ensemble Predictions (Multi-Model)
   ✓ Enhanced Technical Analysis
   ✓ Real-time Market Data (Yahoo Finance)
   ✓ Candlestick & Volume Charts
   
   📊 API Endpoints:
     /api/stock/<symbol>    - Stock data with AI predictions
     /api/sentiment/<symbol> - FinBERT sentiment analysis
     /api/predictions/<symbol> - Cached predictions
   
   🚀 Server starting on http://localhost:5001
   ======================================================================
   
   INFO:werkzeug: * Running on http://127.0.0.1:5001
   ```

3. **Test the Server**
   - Open your web browser
   - Navigate to: `http://localhost:5001`
   - You should see the FinBERT v4.0 interface

### Step 5: Test the System

1. **Test in Browser**
   - Enter a stock symbol: `AAPL`
   - Click "Analyze"
   - View prediction, charts, and sentiment
   - Check prediction status indicator

2. **Test API Endpoints**
   ```powershell
   # In a new PowerShell window:
   
   # Test cached prediction
   curl http://localhost:5001/api/predictions/AAPL
   
   # Test scheduler status
   curl http://localhost:5001/api/predictions/scheduler/status
   
   # Test health endpoint
   curl http://localhost:5001/api/health
   ```

3. **Test Multiple Markets**
   - US Stock: `AAPL`, `TSLA`, `MSFT`
   - AU Stock: `BHP.AX`, `CBA.AX`
   - UK Stock: `BP.L`, `HSBA.L`

## 🗄️ Database Setup

The system automatically creates databases on first run:

1. **trading.db**
   - Stores cached predictions
   - Tracks accuracy statistics
   - Location: Same folder as app

2. **news_sentiment_cache.db**
   - Caches sentiment analysis results
   - Speeds up repeated requests
   - Location: Same folder as app

**No manual database setup required!** ✅

## ⚙️ Configuration (Optional)

### Change Server Port

Edit `config_dev.py`:
```python
PORT = 5001  # Change to your preferred port
```

### Adjust Cache Duration

Edit `config_dev.py`:
```python
PREDICTION_CACHE_HOURS = 24  # Cache predictions for 24 hours
```

### Enable/Disable Scheduler

Edit `config_dev.py`:
```python
ENABLE_SCHEDULER = True  # Set to False to disable auto-validation
```

## 🚀 Advanced Setup (Optional)

### Train LSTM Model

For improved predictions, train LSTM models:

```powershell
# Train for AAPL
python models/train_lstm.py --symbol AAPL --epochs 50

# Train for TSLA
python models/train_lstm.py --symbol TSLA --epochs 50

# Train for BHP.AX (Australian)
python models/train_lstm.py --symbol BHP.AX --epochs 50
```

Models are saved in `trained_models/` folder.

### Install GPU Support (NVIDIA Only)

For faster neural network predictions:

```powershell
# Uninstall CPU-only TensorFlow
pip uninstall tensorflow

# Install GPU version
pip install tensorflow-gpu

# Verify GPU detection
python -c "import tensorflow as tf; print('GPUs:', tf.config.list_physical_devices('GPU'))"
```

Requires NVIDIA GPU with CUDA support.

## 🔧 Troubleshooting

### Issue 1: Python not found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Reinstall Python with "Add to PATH" checked
2. Or use full path: `C:\Python311\python.exe app_finbert_v4_dev.py`

### Issue 2: pip install fails
**Error**: `ERROR: Could not install packages`

**Solution**:
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Retry installation
pip install -r requirements.txt
```

### Issue 3: Port already in use
**Error**: `Address already in use`

**Solution**:
1. Change port in `config_dev.py`
2. Or kill existing process:
   ```powershell
   # Find process using port 5001
   netstat -ano | findstr :5001
   
   # Kill process (replace PID with actual number)
   taskkill /PID <PID> /F
   ```

### Issue 4: ModuleNotFoundError
**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```powershell
# Make sure you're in the correct folder
cd C:\path\to\FinBERT_v4.0_Windows11_Prediction_System

# Install dependencies again
pip install -r requirements.txt
```

### Issue 5: Database locked
**Error**: `database is locked`

**Solution**:
1. Close all other instances of the app
2. Delete `trading.db-journal` file if it exists
3. Restart the application

### Issue 6: TensorFlow warnings
**Warning**: `TensorFlow not installed. LSTM features will be limited.`

**Solution** (Optional):
```powershell
# Install TensorFlow
pip install tensorflow

# Or CPU-only version
pip install tensorflow-cpu
```

System works without TensorFlow, but LSTM predictions will be unavailable.

## 📁 File Structure

```
FinBERT_v4.0_Windows11_Prediction_System/
│
├── 📄 app_finbert_v4_dev.py          ← Main application
├── 📄 finbert_v4_enhanced_ui.html    ← Web interface
├── 📄 config_dev.py                   ← Configuration
├── 📄 requirements.txt                ← Dependencies list
│
├── 📁 models/
│   ├── lstm_predictor.py             ← LSTM neural network
│   ├── finbert_sentiment.py          ← Sentiment analyzer
│   ├── prediction_manager.py         ← Prediction controller
│   ├── market_timezones.py           ← Timezone handler
│   ├── prediction_scheduler.py       ← Auto-validation
│   └── trading/
│       ├── prediction_database.py    ← Database operations
│       ├── portfolio_manager.py      ← Portfolio tracking
│       └── risk_manager.py           ← Risk management
│
├── 📁 trained_models/                 ← LSTM models (created after training)
│
├── 📊 trading.db                      ← Prediction database (auto-created)
├── 📊 news_sentiment_cache.db         ← Sentiment cache (auto-created)
│
└── 📚 Documentation/
    ├── README_PREDICTION_SYSTEM.md   ← System overview
    ├── INSTALLATION_GUIDE.md         ← This file
    └── MULTI_TIMEZONE_PREDICTIONS.md ← Technical docs
```

## 🎯 Next Steps

After successful installation:

1. **Explore the Interface**
   - Try different stock symbols
   - View prediction status indicators
   - Check accuracy dashboard

2. **Test Multiple Markets**
   - US: AAPL, TSLA, MSFT
   - Australia: BHP.AX, CBA.AX, ANZ.AX
   - UK: BP.L, HSBA.L, VOD.L

3. **Monitor Scheduler**
   - Check scheduler status: `http://localhost:5001/api/predictions/scheduler/status`
   - View next validation times
   - Wait for market close to see auto-validation

4. **Train LSTM Models** (Optional)
   - Improves prediction accuracy
   - Takes 10-30 minutes per symbol
   - See "Advanced Setup" section

5. **Read Documentation**
   - README_PREDICTION_SYSTEM.md for features
   - MULTI_TIMEZONE_PREDICTIONS.md for technical details

## 📞 Support

If you encounter issues:

1. **Check Troubleshooting Section**: Common problems and solutions
2. **Verify Requirements**: Python version, dependencies installed
3. **Review Error Messages**: Look for specific error details
4. **Test Step-by-Step**: Follow installation guide carefully

## 🎉 Success Indicators

You've successfully installed when:

✅ Server starts without errors
✅ Browser shows FinBERT interface
✅ Stock analysis works (AAPL)
✅ Predictions show status indicators
✅ Scheduler shows 3 validation jobs
✅ Database files created automatically
✅ API endpoints respond correctly

**Congratulations! You're ready to use FinBERT v4.0!** 🚀

---

**Installation Support**: Check README_PREDICTION_SYSTEM.md for usage guide
**Last Updated**: November 3, 2025
**Version**: 4.0.0
