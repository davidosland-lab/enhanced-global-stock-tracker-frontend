# FinBERT v4.0 - Installation Instructions

## ⚠️ IMPORTANT: Correct Installation Steps

### Step 1: Extract the ZIP File
Extract `FinBERT_v4.0_Parameter_Optimization_Windows11_FINAL.zip` to a directory on your computer.

Example: `C:\FinBERT_v4.0\`

### Step 2: Run the Installation Script
**Location**: `scripts\INSTALL_WINDOWS11.bat`

NOT the root `INSTALL.bat` (if one exists) - use the one in the `scripts` folder!

1. Navigate to the extracted folder
2. Go into the `scripts` subfolder
3. **RIGHT-CLICK** on `INSTALL_WINDOWS11.bat`
4. Select "Run as Administrator"

### Step 3: Choose Installation Type

The installer will prompt you:

```
[1] FULL INSTALL - Complete AI/ML Experience (Recommended)
    Size: ~900 MB download, 2 GB installed
    Time: 10-20 minutes
    
[2] MINIMAL INSTALL - Basic Features Only
    Size: ~50 MB download, 500 MB installed
    Time: 2-3 minutes
```

**Recommendation**: Choose **[1] FULL INSTALL** to get all features including:
- Real FinBERT sentiment analysis
- LSTM predictions  
- Parameter optimization
- Portfolio backtesting

### Step 4: Wait for Installation
- The installation will create a virtual environment
- Install all required Python packages
- This may take 10-20 minutes for FULL install
- DO NOT close the window until you see "Installation Complete!"

### Step 5: Start the Application
After installation completes:

1. Go back to the main folder (parent of `scripts`)
2. Double-click `START_FINBERT_V4.bat`
3. A terminal window will open showing "Starting FinBERT v4.0 server..."
4. Open your web browser to: **http://127.0.0.1:5001**

## Troubleshooting

### Error: "Virtual environment not found"
**Cause**: You didn't run `scripts\INSTALL_WINDOWS11.bat` yet  
**Solution**: Run the installation script from the `scripts` folder first

### Error: "Python is not installed"
**Cause**: Python 3.8+ is not installed or not in PATH  
**Solution**:
1. Download Python 3.8 or higher from https://www.python.org/downloads/
2. During installation, CHECK the box "Add Python to PATH"
3. Restart your computer
4. Run the installation script again

### Installation goes very fast (less than 30 seconds)
**Cause**: The installation script failed silently  
**Solution**:
1. Open Command Prompt as Administrator
2. Navigate to the scripts folder: `cd C:\FinBERT_v4.0\scripts`
3. Run: `INSTALL_WINDOWS11.bat`
4. Watch for any error messages

### Backtest shows "No data available"
**Possible causes**:
1. **Running old deployment** - Make sure you extracted and installed the LATEST ZIP file
2. **Date range issue** - Try using dates from 6 months ago to yesterday
3. **Internet connection** - Yahoo Finance requires internet access
4. **Installation incomplete** - Re-run `scripts\INSTALL_WINDOWS11.bat`

## Verifying Installation

After installation, you should see:
```
✓ Flask: 3.0.0
✓ NumPy: 1.26.x
✓ Pandas: 2.1.x
✓ yfinance installed
✓ TensorFlow: 2.13.x
✓ PyTorch: 2.0.x
✓ Transformers: 4.30.x
```

## Features Available After Installation

### Single Stock Backtesting
- Test trading strategies on historical data
- Choose from 4 model types:
  - **Ensemble** (LSTM + Technical + Momentum) - Recommended
  - **LSTM** Neural Network
  - **Technical** Analysis
  - **Momentum** Strategy

### Parameter Optimization
- Grid Search: Test all parameter combinations
- Random Search: Efficient parameter exploration
- Train-Test Split: Validate against overfitting
- Overfitting Detection: Performance degradation scoring

### Portfolio Backtesting
- Test strategies on multiple stocks simultaneously
- Track individual stock contributions
- Monitor total equity over time

### AI Predictions
- Real-time FinBERT sentiment analysis
- LSTM price predictions
- Confidence scoring

## Directory Structure

```
FinBERT_v4.0_Windows11_ENHANCED/
├── scripts/
│   └── INSTALL_WINDOWS11.bat    ← RUN THIS FIRST
├── START_FINBERT_V4.bat          ← RUN THIS TO START
├── app_finbert_v4_dev.py         (Main application)
├── templates/
│   └── finbert_v4_enhanced_ui.html
├── models/
│   ├── backtesting/              (Backtesting framework)
│   ├── finbert_sentiment.py
│   └── lstm_predictor.py
├── docs/
│   └── (Documentation files)
├── venv/                         (Created by installer)
├── cache/                        (Created automatically)
└── logs/                         (Created automatically)
```

## Support

If you continue to have issues:
1. Check `logs/backtest_engine.log` for error details
2. Verify Python version: `python --version` (should be 3.8+)
3. Verify packages installed: `pip list` (should show Flask, pandas, etc.)
4. Try running test_backtest_flow.py to verify the backtesting framework

## Version Information

- **Version**: 4.0 Parameter Optimization Edition
- **Release Date**: November 1, 2025
- **Python Required**: 3.8 or higher
- **Platform**: Windows 11 (may work on Windows 10)

---

**Important**: Always use `scripts\INSTALL_WINDOWS11.bat` for installation, not any INSTALL.bat in the root directory!
