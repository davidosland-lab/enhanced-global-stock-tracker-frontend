# Stock Analysis with Market Sentiment - Phase 1

## ✅ FIXED: IndentationError Issue Resolved

The IndentationError at line 700 has been fixed in `app_enhanced_sentiment_fixed.py`. The issue was caused by improper indentation of a comment line before the Flask routes.

## Features

### Market Sentiment Indicators (Phase 1)
- **VIX Fear Gauge**: Real-time market fear/greed indicator
- **Market Breadth**: Analysis of advancing vs declining stocks
- **Bond Yields**: 10-year Treasury yield tracking
- **Dollar Strength**: DXY index monitoring
- **Sector Rotation**: Performance analysis across major sectors

### Core Features
- **Real-time Yahoo Finance data** (primary source)
- **Alpha Vantage fallback** (API key: 68ZFANK047DL0KSR)
- **Australian stocks support** (automatic .AX suffix)
- **ML predictions** with RandomForestRegressor
- **Technical indicators**: RSI, MACD, Bollinger Bands, SMA, EMA, ATR
- **Interactive charts** with zoom functionality
- **NO mock/synthetic data** - 100% real market data

## Installation (Windows)

1. **Install dependencies**:
   ```batch
   INSTALL_SENTIMENT.bat
   ```

2. **Run the application**:
   ```batch
   RUN_SENTIMENT_FINAL.bat
   ```

## Manual Installation

If the batch files don't work, run these commands manually:

```bash
# Set encoding (Windows)
set PYTHONIOENCODING=utf-8
set FLASK_SKIP_DOTENV=1

# Install packages
pip install -r requirements_sentiment.txt

# Run the app
python app_enhanced_sentiment_fixed.py
```

## Access the Application

Once running, open your browser to:
- http://localhost:5000

## API Endpoints

### Stock Data
- `/api/stock/<symbol>` - Get stock data with indicators and predictions
  - Query params: `period` (1d, 5d, 1mo, 3mo, 6mo, 1y), `interval` (1m, 5m, 15m, 30m, 1h, 1d)

### Sentiment Endpoints
- `/api/sentiment` - Combined market sentiment
- `/api/sentiment/vix` - VIX fear gauge
- `/api/sentiment/breadth` - Market breadth analysis
- `/api/sentiment/sectors` - Sector rotation data

## File Structure

```
SentimentUpdate/
├── app_enhanced_sentiment_fixed.py  # Main application (FIXED)
├── requirements_sentiment.txt       # Python dependencies
├── INSTALL_SENTIMENT.bat           # Windows installer
├── RUN_SENTIMENT_FINAL.bat        # Windows runner (handles encoding)
└── README_SENTIMENT.md             # This file
```

## Troubleshooting

### IndentationError (FIXED)
The IndentationError at line 700 has been resolved by:
1. Properly indenting the comment line before Flask routes
2. Adding missing global instance declarations

### Unicode/Encoding Errors
The batch files now include:
- `set PYTHONIOENCODING=utf-8`
- `set FLASK_SKIP_DOTENV=1`

### Port 5000 Already in Use
The batch file automatically kills existing processes on port 5000.

### Dependencies Not Found
Run `INSTALL_SENTIMENT.bat` or manually install with pip.

## Technical Details

### ML Model Configuration
- Algorithm: RandomForestRegressor
- Trees: 150 (enhanced from 100)
- Max Depth: 7 (enhanced from 5)
- Features: ~25 (including sentiment indicators)

### Sentiment Scoring
- Composite score: -100 (extreme fear) to +100 (extreme greed)
- VIX levels: <12 (low fear), 12-20 (normal), 20-30 (elevated), >30 (high fear)
- Updates: Real-time from market data

## Next Phases (Planned)

### Phase 2: News Sentiment
- FinBERT integration for financial news analysis
- Real-time news feed processing
- Sentiment scoring from headlines

### Phase 3: Macroeconomic Data
- FRED API integration
- GDP, inflation, employment data
- Economic indicator dashboard

## Support

If you encounter any issues:
1. Check that Python 3.8+ is installed
2. Verify all dependencies are installed
3. Ensure port 5000 is available
4. Check the console for error messages

## Version

Current: Phase 1 - Market Sentiment Integration (FIXED)
- IndentationError resolved
- Windows compatibility improved
- Encoding issues handled