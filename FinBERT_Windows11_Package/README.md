# 🤖 FinBERT Trading System for Windows 11

A sophisticated stock trading system that combines **FinBERT** (Financial BERT) sentiment analysis with machine learning for enhanced trading predictions.

## 🌟 Key Features

- **FinBERT Integration**: State-of-the-art financial sentiment analysis
- **Machine Learning Models**: Random Forest classifiers for price prediction
- **Real-time Data**: Live stock data from Yahoo Finance
- **Automatic Fallback**: Works even if FinBERT fails to load
- **Windows 11 Optimized**: Fully tested on Windows 11
- **Fixed Numpy Issues**: Pre-configured to avoid common numpy/transformers conflicts

## 📋 System Requirements

- **Windows 11** (also works on Windows 10)
- **Python 3.8+** (3.10 or 3.11 recommended)
- **4GB RAM minimum** (8GB recommended for FinBERT)
- **2GB free disk space** (for models and dependencies)
- **Internet connection** (for downloading stock data)

## 🚀 Quick Start

### Step 1: Install Python
If you don't have Python installed:
1. Download from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation: Open Command Prompt and type `python --version`

### Step 2: Extract Package
1. Extract this ZIP file to a folder (e.g., `C:\FinBERT_Trading`)
2. Navigate to the extracted folder

### Step 3: Install Dependencies
1. **Double-click `INSTALL.bat`**
2. Wait for all dependencies to install (5-10 minutes)
3. Choose whether to download FinBERT model now or later

### Step 4: Run the Application
1. **Double-click `RUN.bat`**
2. Open your browser and go to: **http://localhost:5000**
3. Start analyzing stocks!

## 🎯 How to Use

### Training a Model
1. Select a stock symbol from the dropdown or enter custom symbol
2. Click "Train Model"
3. Wait for training to complete (10-30 seconds)
4. Review accuracy scores and feature importance

### Making Predictions
1. Select a stock symbol
2. Click "Predict"
3. View prediction (BUY/SELL) with probability
4. Check sentiment score and technical indicators

### Testing Sentiment Analysis
1. Enter any financial text
2. Click "Analyze Sentiment"
3. View positive/negative/neutral scores

## 🔧 Troubleshooting

### Numpy Errors
If you see numpy-related errors:
1. **Run `REPAIR_NUMPY.bat`**
2. This will fix most numpy/transformers conflicts
3. Then run `RUN.bat` again

### FinBERT Not Loading
If FinBERT doesn't load (application runs in fallback mode):
1. Check internet connection (for model download)
2. Ensure you have at least 1GB free space
3. Re-run `INSTALL.bat` and choose to download model

### Port Already in Use
If port 5000 is already in use:
1. Close other applications using port 5000
2. Or edit `app_finbert_trading.py` and change the port number at the bottom

### Python Not Found
If Windows can't find Python:
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to system PATH
3. Restart Command Prompt after PATH changes

## 📊 Understanding the Output

### Model Training Results
- **Training Accuracy**: How well the model fits training data (should be 70-90%)
- **Testing Accuracy**: How well it predicts unseen data (should be 55-75%)
- **Feature Importance**: Which factors matter most for predictions

### Predictions
- **BUY Signal**: Model predicts price will go up
- **SELL Signal**: Model predicts price will go down
- **Probability**: Confidence level (>60% is considered strong)
- **Sentiment Score**: -1 (very negative) to +1 (very positive)
- **RSI**: Technical indicator (>70 overbought, <30 oversold)

### Sentiment Analysis
- **Positive**: Bullish sentiment (good news, upgrades, beats)
- **Negative**: Bearish sentiment (bad news, downgrades, misses)
- **Neutral**: No clear sentiment direction
- **Score**: Overall sentiment from -1 to +1

## 🎨 Features Explained

### FinBERT Advantage
FinBERT is specifically trained on financial texts and understands:
- Earnings reports context
- Financial terminology
- Market sentiment nuances
- Difference between general negative news and financial impact

### Fallback Mode
If FinBERT fails to load, the system automatically uses:
- Keyword-based sentiment analysis
- Still provides useful predictions
- Slightly lower accuracy but fully functional

### Technical Indicators Used
- **SMA (Simple Moving Average)**: Trend direction
- **RSI (Relative Strength Index)**: Overbought/oversold conditions
- **MACD**: Momentum changes
- **Volume Ratio**: Trading activity level
- **Volatility**: Price movement intensity

## 📁 File Structure

```
FinBERT_Windows11_Package/
│
├── app_finbert_trading.py   # Main application
├── requirements.txt          # Python dependencies
├── INSTALL.bat              # Installation script
├── RUN.bat                  # Run script
├── REPAIR_NUMPY.bat         # Numpy fix utility
├── README.md                # This file
│
├── models/                  # FinBERT model storage
├── cache/                   # Data cache
├── logs/                    # Application logs
└── data/                    # Stock data storage
```

## ⚙️ Configuration

### Changing Stock Symbols
Edit `DEFAULT_SYMBOLS` in `app_finbert_trading.py` to add your preferred stocks.

### Adjusting Model Parameters
In `MLTradingModel` class:
- `n_estimators`: Number of trees (default: 100)
- `max_depth`: Tree depth (default: 10)
- `period`: Historical data period (default: "6mo")

### Port Configuration
Change the port at the bottom of `app_finbert_trading.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## 🔒 Security Notes

- The application runs locally on your machine
- No data is sent to external servers (except fetching stock prices)
- FinBERT model runs entirely offline once downloaded
- Your trading strategies remain private

## 📈 Performance Tips

1. **First Run**: FinBERT download takes time (400MB model)
2. **Caching**: Data is cached to improve speed
3. **Multiple Stocks**: Train models for your portfolio in advance
4. **Regular Updates**: Retrain models weekly for best results

## 🐛 Known Issues

1. **Windows Defender**: May slow down first installation
2. **Corporate Firewalls**: May block model downloads
3. **Antivirus Software**: May flag .bat files (they're safe)

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review error messages in the console
3. Check `logs/finbert_trading.log` for detailed errors

## 📜 License

This software is provided as-is for educational and research purposes.

## 🙏 Credits

- **FinBERT**: ProsusAI for the pre-trained model
- **PyTorch**: Facebook AI Research
- **Transformers**: Hugging Face
- **yfinance**: Yahoo Finance data

---

**Version**: 1.0.0  
**Last Updated**: October 2024  
**Python Compatibility**: 3.8, 3.9, 3.10, 3.11  
**Windows Compatibility**: Windows 10, Windows 11