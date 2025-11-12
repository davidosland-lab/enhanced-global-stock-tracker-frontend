# Overnight Stock Screening System - Implementation Plan

## Executive Summary

Automated overnight stock screening system for Australian market that:
- Scans top 30 stocks across major ASX sectors
- Monitors SPI 200 futures for market sentiment
- Trains LSTM models on high-priority stocks
- Generates actionable morning report before market open
- Scalable architecture for multi-market expansion

---

## Phase 1: Core Architecture (Week 1-2)

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                  OVERNIGHT SCREENER SYSTEM                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Stock      │  │  SPI 200     │  │   LSTM       │    │
│  │   Scanner    │  │  Monitor     │  │   Trainer    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │             │
│         └─────────┬────────┴──────────────────┘            │
│                   ▼                                         │
│         ┌──────────────────────┐                           │
│         │  Prediction Engine   │                           │
│         └──────────┬───────────┘                           │
│                    ▼                                         │
│         ┌──────────────────────┐                           │
│         │  Scoring & Ranking   │                           │
│         └──────────┬───────────┘                           │
│                    ▼                                         │
│         ┌──────────────────────┐                           │
│         │  Report Generator    │                           │
│         └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 File Structure

```
models/
├── screening/
│   ├── __init__.py
│   ├── stock_scanner.py          # ASX stock selection
│   ├── spi_monitor.py            # SPI 200 futures tracking
│   ├── batch_predictor.py        # Mass prediction engine
│   ├── opportunity_scorer.py     # Ranking algorithm
│   └── report_generator.py       # HTML/PDF report
├── scheduling/
│   ├── __init__.py
│   ├── overnight_scheduler.py    # Windows Task Scheduler wrapper
│   └── progress_tracker.py       # Real-time progress monitoring
└── config/
    ├── asx_sectors.json          # Market categorization
    ├── screening_config.json     # Screening parameters
    └── markets_config.json       # Multi-market expansion

scripts/
├── RUN_OVERNIGHT_SCREENER.bat   # Main execution script
├── SCHEDULE_SCREENER.bat        # Setup Windows Task
└── CHECK_SCREENER_STATUS.bat    # Monitor progress

reports/
└── morning_reports/              # Generated daily reports
    └── YYYY-MM-DD_market_report.html
```

---

## Phase 2: Australian Market Implementation (Week 3-4)

### 2.1 ASX Sector Categories

**Top 30 Stocks Per Sector:**

1. **Financials** (Banks, Insurance)
   - CBA, WBC, ANZ, NAB, MQG, AMP, SUN, QBE, IAG, etc.

2. **Materials** (Mining, Resources)
   - BHP, RIO, FMG, MIN, S32, NCM, EVN, STO, WDS, etc.

3. **Healthcare** (Pharma, Medical)
   - CSL, COH, RMD, SHL, RHC, FPH, etc.

4. **Consumer Staples** (Retail, Food)
   - WES, WOW, COL, EDV, A2M, BKL, etc.

5. **Technology** (IT, Fintech)
   - XRO, WTC, CPU, NXT, APX, etc.

6. **Energy** (Oil, Gas, Renewables)
   - ORG, STO, WDS, WHC, NHC, etc.

7. **Industrials** (Infrastructure)
   - TCL, QAN, SYD, ASX, SEK, etc.

8. **Real Estate** (REITs)
   - GMG, SCG, GPT, MGR, VCX, etc.

### 2.2 Stock Selection Criteria

```python
# Selection Algorithm
1. Market Cap > $500M (exclude micro-caps)
2. Average Daily Volume > 500,000 shares (liquidity)
3. Listed > 12 months (exclude new IPOs)
4. Not in trading halt
5. Price > $0.50 (exclude penny stocks)
6. Beta 0.5-2.0 (reasonable volatility)
```

### 2.3 SPI 200 Futures Integration

**Why SPI 200 Matters:**
- Trades 5:10 PM - 8:00 AM AEST (overnight)
- Leading indicator for ASX 200 opening direction
- Tracks global market sentiment (US, Europe, Asia)

**Data Points to Capture:**
```python
{
    "timestamp": "2025-11-06 06:00:00 AEST",
    "spi_price": 8250,
    "spi_change": +45,
    "spi_change_pct": 0.55,
    "sp500_close": 5850,      # US market close
    "nasdaq_close": 18500,
    "us_sentiment": "bullish",
    "gap_prediction": "up 0.5%",  # Expected ASX open gap
    "confidence": "high"
}
```

**API Sources:**
- ASX official data feed
- Yahoo Finance (yfinance library)
- Alpha Vantage futures data
- Bloomberg Terminal (if available)

---

## Phase 3: Prediction & Scoring Engine (Week 5-6)

### 3.1 Overnight Processing Pipeline

```python
# OVERNIGHT_PIPELINE.py

def run_overnight_screening(date):
    """
    Main overnight screening function
    Runs 10:00 PM - 7:00 AM AEST
    """
    
    # STEP 1: Market Data Collection (10:00 PM - 11:00 PM)
    stocks = select_top_stocks_per_sector(top_n=30)
    spi_data = monitor_spi_200_overnight()
    
    # STEP 2: LSTM Training (11:00 PM - 3:00 AM)
    # Train on high-priority stocks that need model updates
    priority_stocks = identify_stale_models(stocks)
    for stock in priority_stocks:
        train_lstm_model(stock, epochs=50)
    
    # STEP 3: Mass Prediction (3:00 AM - 5:00 AM)
    predictions = {}
    for stock in stocks:
        pred = generate_ensemble_prediction(stock)
        predictions[stock] = pred
    
    # STEP 4: Opportunity Scoring (5:00 AM - 6:00 AM)
    scored = score_and_rank_opportunities(predictions, spi_data)
    
    # STEP 5: Report Generation (6:00 AM - 7:00 AM)
    report = generate_morning_report(scored, spi_data)
    
    # STEP 6: Notification (7:00 AM)
    send_report_email(report)
    save_report_to_file(report)
    
    return report
```

### 3.2 Opportunity Scoring Algorithm

**Composite Score (0-100):**

```python
def calculate_opportunity_score(stock, prediction, spi_data):
    """
    Multi-factor scoring system
    """
    score = 0
    
    # Factor 1: Model Confidence (0-25 points)
    confidence_score = prediction['confidence'] * 25
    
    # Factor 2: Prediction Strength (0-25 points)
    if prediction['signal'] == 'STRONG_BUY':
        signal_score = 25
    elif prediction['signal'] == 'BUY':
        signal_score = 20
    elif prediction['signal'] == 'HOLD':
        signal_score = 10
    else:
        signal_score = 0
    
    # Factor 3: Technical Indicators (0-20 points)
    technical_score = 0
    if stock['rsi'] < 30:  # Oversold
        technical_score += 10
    if stock['macd_signal'] == 'bullish':
        technical_score += 5
    if stock['price_above_50ma']:
        technical_score += 5
    
    # Factor 4: Sentiment Analysis (0-15 points)
    sentiment_score = stock['finbert_score'] * 15
    
    # Factor 5: Market Alignment (0-15 points)
    # Boost score if SPI 200 suggests bullish opening
    market_score = 0
    if spi_data['gap_prediction'] == 'up':
        if stock['beta'] > 1.0:  # High beta = more responsive
            market_score = 15
        else:
            market_score = 10
    
    # Total Score
    total = (confidence_score + signal_score + technical_score + 
             sentiment_score + market_score)
    
    return {
        'total_score': round(total, 2),
        'breakdown': {
            'confidence': confidence_score,
            'signal': signal_score,
            'technical': technical_score,
            'sentiment': sentiment_score,
            'market': market_score
        },
        'rating': get_rating(total)  # A+, A, B+, B, C
    }

def get_rating(score):
    if score >= 85: return 'A+'
    elif score >= 75: return 'A'
    elif score >= 65: return 'B+'
    elif score >= 55: return 'B'
    else: return 'C'
```

### 3.3 Risk Assessment

```python
def assess_risk(stock, historical_data):
    """
    Risk scoring (1-5 stars, 5 = lowest risk)
    """
    risk_factors = {
        'volatility': calculate_volatility(historical_data),
        'max_drawdown': calculate_max_drawdown(historical_data),
        'sharpe_ratio': calculate_sharpe_ratio(historical_data),
        'liquidity': stock['avg_volume'],
        'sector_risk': SECTOR_RISK_MAP[stock['sector']]
    }
    
    # Weighted risk score
    risk_score = (
        (5 - risk_factors['volatility'] * 2) * 0.3 +
        (5 - risk_factors['max_drawdown']) * 0.2 +
        risk_factors['sharpe_ratio'] * 0.2 +
        risk_factors['liquidity_score'] * 0.15 +
        risk_factors['sector_risk'] * 0.15
    )
    
    return {
        'risk_score': round(risk_score, 1),
        'risk_rating': convert_to_stars(risk_score),
        'factors': risk_factors
    }
```

---

## Phase 4: Morning Report Format (Week 7)

### 4.1 Report Structure

**HTML Report Template:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>ASX Morning Report - {DATE}</title>
    <style>
        /* Professional styling */
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .header { background: #1e3a8a; color: white; padding: 20px; }
        .summary { background: white; padding: 20px; margin: 20px; }
        .opportunity { border-left: 4px solid #10b981; padding: 15px; margin: 10px; }
        .high-confidence { border-left-color: #10b981; }
        .medium-confidence { border-left-color: #f59e0b; }
        .low-confidence { border-left-color: #ef4444; }
    </style>
</head>
<body>
    <!-- SECTION 1: Market Overview -->
    <div class="header">
        <h1>ASX Morning Report</h1>
        <p>{DATE} - Generated at {TIME}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Market Overview</h2>
        <table>
            <tr>
                <td><strong>SPI 200 Close:</strong></td>
                <td>8,250 (+45 / +0.55%)</td>
            </tr>
            <tr>
                <td><strong>Expected ASX 200 Open:</strong></td>
                <td>🟢 UP 0.5% (Gap Up)</td>
            </tr>
            <tr>
                <td><strong>Overnight US Markets:</strong></td>
                <td>S&P 500: +0.8% | Nasdaq: +1.2%</td>
            </tr>
            <tr>
                <td><strong>Market Sentiment:</strong></td>
                <td>BULLISH ⭐⭐⭐⭐</td>
            </tr>
        </table>
    </div>
    
    <!-- SECTION 2: Top Opportunities -->
    <div class="summary">
        <h2>🎯 Top 10 Buy Opportunities</h2>
        
        <!-- Opportunity Card -->
        <div class="opportunity high-confidence">
            <h3>1. CSL.AX - CSL Limited (Healthcare)</h3>
            <table>
                <tr>
                    <td><strong>Score:</strong></td>
                    <td>92/100 (A+) ⭐⭐⭐⭐⭐</td>
                </tr>
                <tr>
                    <td><strong>Signal:</strong></td>
                    <td>STRONG BUY (Confidence: 89%)</td>
                </tr>
                <tr>
                    <td><strong>Current Price:</strong></td>
                    <td>$315.50</td>
                </tr>
                <tr>
                    <td><strong>Target Price:</strong></td>
                    <td>$335.00 (+6.2%)</td>
                </tr>
                <tr>
                    <td><strong>Stop Loss:</strong></td>
                    <td>$305.00 (-3.3%)</td>
                </tr>
                <tr>
                    <td><strong>Risk Rating:</strong></td>
                    <td>⭐⭐⭐⭐ (Low)</td>
                </tr>
            </table>
            <p><strong>Analysis:</strong> Strong technical breakout with bullish MACD crossover. FinBERT sentiment: Positive (0.87). LSTM model predicts 5-day uptrend with 89% confidence.</p>
            <p><strong>Catalysts:</strong> Upcoming earnings report, sector rotation into healthcare.</p>
        </div>
        
        <!-- More opportunities... -->
    </div>
    
    <!-- SECTION 3: Sector Breakdown -->
    <div class="summary">
        <h2>📈 Sector Performance</h2>
        <table>
            <tr><th>Sector</th><th>Opportunities</th><th>Avg Score</th><th>Outlook</th></tr>
            <tr><td>Healthcare</td><td>3</td><td>87</td><td>🟢 Strong</td></tr>
            <tr><td>Technology</td><td>2</td><td>82</td><td>🟢 Strong</td></tr>
            <tr><td>Financials</td><td>2</td><td>75</td><td>🟡 Moderate</td></tr>
            <tr><td>Materials</td><td>1</td><td>68</td><td>🟡 Moderate</td></tr>
            <tr><td>Energy</td><td>2</td><td>71</td><td>🟡 Moderate</td></tr>
        </table>
    </div>
    
    <!-- SECTION 4: Watch List -->
    <div class="summary">
        <h2>👀 Watch List (Near Buy Signals)</h2>
        <ul>
            <li>BHP.AX - Breaking resistance at $48.50 (Current: $48.20)</li>
            <li>RIO.AX - RSI entering oversold territory</li>
            <li>FMG.AX - Testing 50-day moving average support</li>
        </ul>
    </div>
    
    <!-- SECTION 5: Warnings -->
    <div class="summary">
        <h2>⚠️ Caution Stocks (Avoid/Sell)</h2>
        <ul>
            <li>XYZ.AX - Bearish divergence detected, confidence 78%</li>
            <li>ABC.AX - Breaking key support level</li>
        </ul>
    </div>
    
    <!-- SECTION 6: Model Performance -->
    <div class="summary">
        <h2>📊 System Performance</h2>
        <table>
            <tr><td>Stocks Scanned:</td><td>210 (7 sectors × 30 stocks)</td></tr>
            <tr><td>LSTM Models Trained:</td><td>15 (stale models updated)</td></tr>
            <tr><td>Predictions Generated:</td><td>210</td></tr>
            <tr><td>Processing Time:</td><td>6h 45m</td></tr>
            <tr><td>Recent Accuracy:</td><td>87.3% (last 30 days)</td></tr>
        </table>
    </div>
    
    <div class="summary">
        <p><em>Disclaimer: This report is generated by automated ML models and should not be considered financial advice. Always conduct your own research and consult a licensed financial advisor.</em></p>
    </div>
</body>
</html>
```

### 4.2 Report Delivery Options

1. **Email** (Primary)
   - HTML email sent to configured address
   - Attachment: PDF version of report
   - Time: 7:00 AM AEST sharp

2. **Web Dashboard**
   - Accessible at http://localhost:5002/morning-report
   - Historical reports archive
   - Real-time update during processing

3. **Mobile Push Notification**
   - Summary notification: "10 opportunities identified, top pick: CSL.AX"
   - Link to full report

4. **File System**
   - Saved to: `reports/morning_reports/YYYY-MM-DD_market_report.html`
   - JSON export: `reports/morning_reports/YYYY-MM-DD_data.json`

---

## Phase 5: Scheduling & Automation (Week 8)

### 5.1 Windows Task Scheduler Configuration

**RUN_OVERNIGHT_SCREENER.bat:**
```batch
@echo off
REM ===================================================================
REM Overnight Stock Screener - Main Execution Script
REM Runs: 10:00 PM - 7:00 AM AEST
REM ===================================================================

echo ========================================
echo   Overnight Stock Screener Starting
echo ========================================
echo Start Time: %TIME%
echo.

REM Activate virtual environment
cd /d "%~dp0"
call venv\Scripts\activate.bat

REM Run the overnight screener
echo Running stock screening pipeline...
python -u models/screening/overnight_pipeline.py --mode full --date %DATE%

REM Check exit code
if errorlevel 1 (
    echo [ERROR] Screener failed with error code %ERRORLEVEL%
    echo Sending error notification...
    python models/screening/send_error_notification.py
    exit /b 1
)

echo.
echo ========================================
echo   Screening Complete!
echo ========================================
echo End Time: %TIME%
echo Report saved to: reports/morning_reports/
echo.

REM Send completion notification
python models/screening/send_completion_notification.py

pause
```

**SCHEDULE_SCREENER.bat:**
```batch
@echo off
REM Create Windows Task to run overnight screener

echo Creating scheduled task for overnight stock screener...

REM Delete existing task if it exists
schtasks /Delete /TN "FinBERT_Overnight_Screener" /F 2>nul

REM Create new task
REM Runs at 10:00 PM every day
REM Highest priority
REM Run whether user is logged in or not

schtasks /Create ^
  /TN "FinBERT_Overnight_Screener" ^
  /TR "\"%CD%\RUN_OVERNIGHT_SCREENER.bat\"" ^
  /SC DAILY ^
  /ST 22:00 ^
  /RL HIGHEST ^
  /F

if errorlevel 1 (
    echo [ERROR] Failed to create scheduled task
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Task Scheduled Successfully!
echo ========================================
echo Task Name: FinBERT_Overnight_Screener
echo Run Time: 10:00 PM Daily
echo.
echo To view task: schtasks /Query /TN "FinBERT_Overnight_Screener" /V
echo To disable: schtasks /Change /TN "FinBERT_Overnight_Screener" /DISABLE
echo.

pause
```

### 5.2 Progress Monitoring

**CHECK_SCREENER_STATUS.bat:**
```batch
@echo off
REM Check the current status of overnight screener

python models/screening/check_status.py

pause
```

**Progress Dashboard:**
```python
# models/screening/progress_tracker.py

class ScreenerProgress:
    """
    Real-time progress tracking during overnight run
    """
    
    def __init__(self):
        self.start_time = None
        self.stages = {
            'data_collection': {'status': 'pending', 'progress': 0},
            'lstm_training': {'status': 'pending', 'progress': 0},
            'prediction': {'status': 'pending', 'progress': 0},
            'scoring': {'status': 'pending', 'progress': 0},
            'report_generation': {'status': 'pending', 'progress': 0}
        }
    
    def update_stage(self, stage_name, progress, status='running'):
        self.stages[stage_name]['progress'] = progress
        self.stages[stage_name]['status'] = status
        self.save_to_file()
    
    def save_to_file(self):
        """Save progress to JSON file for web dashboard"""
        with open('reports/screener_progress.json', 'w') as f:
            json.dump({
                'start_time': self.start_time,
                'current_time': datetime.now().isoformat(),
                'stages': self.stages,
                'overall_progress': self.calculate_overall_progress()
            }, f)
    
    def calculate_overall_progress(self):
        total = sum(s['progress'] for s in self.stages.values())
        return round(total / len(self.stages), 1)
```

---

## Phase 6: Multi-Market Expansion (Week 9-10)

### 6.1 Market Configuration

**markets_config.json:**
```json
{
  "markets": [
    {
      "code": "ASX",
      "name": "Australian Securities Exchange",
      "timezone": "Australia/Sydney",
      "trading_hours": {
        "open": "10:00",
        "close": "16:00"
      },
      "futures_index": "SPI200",
      "futures_trading_hours": {
        "open": "17:10",
        "close": "08:00"
      },
      "enabled": true,
      "priority": 1
    },
    {
      "code": "NYSE",
      "name": "New York Stock Exchange",
      "timezone": "America/New_York",
      "trading_hours": {
        "open": "09:30",
        "close": "16:00"
      },
      "futures_index": "ES",
      "enabled": false,
      "priority": 2
    },
    {
      "code": "LSE",
      "name": "London Stock Exchange",
      "timezone": "Europe/London",
      "trading_hours": {
        "open": "08:00",
        "close": "16:30"
      },
      "futures_index": "FTSE",
      "enabled": false,
      "priority": 3
    },
    {
      "code": "TSE",
      "name": "Tokyo Stock Exchange",
      "timezone": "Asia/Tokyo",
      "trading_hours": {
        "open": "09:00",
        "close": "15:00"
      },
      "futures_index": "NK225",
      "enabled": false,
      "priority": 4
    }
  ]
}
```

### 6.2 Expansion Architecture

```python
# models/screening/multi_market_screener.py

class MultiMarketScreener:
    """
    Extensible screener supporting multiple markets
    """
    
    def __init__(self, config_path='models/config/markets_config.json'):
        self.config = self.load_config(config_path)
        self.active_markets = [m for m in self.config['markets'] if m['enabled']]
    
    def run_overnight_screening(self, date):
        """
        Run screening across all enabled markets
        """
        results = {}
        
        for market in self.active_markets:
            logger.info(f"Screening {market['name']}...")
            
            # Market-specific screener
            screener = self.get_market_screener(market['code'])
            market_results = screener.run(date)
            
            results[market['code']] = market_results
        
        # Generate consolidated report
        report = self.generate_multi_market_report(results)
        
        return report
    
    def get_market_screener(self, market_code):
        """
        Factory pattern for market-specific screeners
        """
        screeners = {
            'ASX': ASXScreener(),
            'NYSE': NYSEScreener(),
            'LSE': LSEScreener(),
            'TSE': TSEScreener()
        }
        return screeners.get(market_code)
```

---

## Phase 7: Implementation Files

### 7.1 Core Files to Create

**1. models/screening/stock_scanner.py**
```python
"""
ASX Stock Scanner
Selects top 30 stocks per sector based on defined criteria
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ASX Sector Definitions
ASX_SECTORS = {
    'Financials': ['CBA.AX', 'WBC.AX', 'ANZ.AX', 'NAB.AX', 'MQG.AX', ...],
    'Materials': ['BHP.AX', 'RIO.AX', 'FMG.AX', 'MIN.AX', 'S32.AX', ...],
    'Healthcare': ['CSL.AX', 'COH.AX', 'RMD.AX', 'SHL.AX', 'RHC.AX', ...],
    # ... more sectors
}

class StockScanner:
    def __init__(self):
        self.sectors = ASX_SECTORS
    
    def select_top_stocks(self, sector, top_n=30):
        """
        Select top N stocks from sector based on criteria
        """
        stocks = self.sectors[sector]
        validated = []
        
        for symbol in stocks:
            if self.validate_stock(symbol):
                stock_data = self.get_stock_metrics(symbol)
                validated.append(stock_data)
        
        # Sort by composite score
        validated.sort(key=lambda x: x['screening_score'], reverse=True)
        
        return validated[:top_n]
    
    def validate_stock(self, symbol):
        """
        Check if stock meets basic criteria
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Criteria checks
            if info.get('marketCap', 0) < 500_000_000:  # $500M min
                return False
            
            if info.get('averageVolume', 0) < 500_000:  # 500k shares/day
                return False
            
            if info.get('currentPrice', 0) < 0.50:  # $0.50 min price
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to validate {symbol}: {e}")
            return False
    
    def get_stock_metrics(self, symbol):
        """
        Get comprehensive stock metrics for screening
        """
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period='3mo')
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'Unknown'),
            'price': info.get('currentPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'volume': info.get('averageVolume', 0),
            'beta': info.get('beta', 1.0),
            'pe_ratio': info.get('trailingPE', 0),
            'screening_score': self.calculate_screening_score(hist, info)
        }
    
    def calculate_screening_score(self, hist, info):
        """
        Calculate composite screening score (0-100)
        """
        score = 50  # Base score
        
        # Volume score
        if info.get('averageVolume', 0) > 1_000_000:
            score += 10
        
        # Volatility score
        beta = info.get('beta', 1.0)
        if 0.8 <= beta <= 1.5:
            score += 15
        
        # Price momentum
        if len(hist) > 20:
            ma_20 = hist['Close'].rolling(20).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            if current_price > ma_20:
                score += 10
        
        # Market cap weight
        market_cap = info.get('marketCap', 0)
        if market_cap > 10_000_000_000:  # $10B+
            score += 15
        
        return min(score, 100)
```

**2. models/screening/spi_monitor.py**
```python
"""
SPI 200 Futures Monitor
Tracks overnight futures movement to predict ASX opening
"""

import yfinance as yf
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SPIMonitor:
    def __init__(self):
        self.spi_symbol = '^ASPI'  # SPI 200 Futures
        self.asx200_symbol = '^AXJO'  # ASX 200 Index
    
    def get_overnight_data(self):
        """
        Get SPI 200 data from previous close to current
        """
        try:
            spi = yf.Ticker(self.spi_symbol)
            hist = spi.history(period='5d', interval='1h')
            
            if hist.empty:
                logger.warning("No SPI 200 data available")
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-10]  # ~10 hours ago
            
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            return {
                'current_price': current_price,
                'previous_close': prev_close,
                'change': change,
                'change_pct': change_pct,
                'timestamp': datetime.now(),
                'gap_prediction': self.predict_opening_gap(change_pct)
            }
            
        except Exception as e:
            logger.error(f"Failed to get SPI data: {e}")
            return None
    
    def predict_opening_gap(self, spi_change_pct):
        """
        Predict ASX 200 opening gap based on SPI movement
        """
        # SPI typically leads ASX by 0.8-0.9 correlation
        predicted_gap = spi_change_pct * 0.85
        
        if predicted_gap > 0.3:
            return {
                'direction': 'up',
                'magnitude': predicted_gap,
                'confidence': 'high',
                'description': f'Gap up ~{predicted_gap:.2f}%'
            }
        elif predicted_gap < -0.3:
            return {
                'direction': 'down',
                'magnitude': predicted_gap,
                'confidence': 'high',
                'description': f'Gap down ~{predicted_gap:.2f}%'
            }
        else:
            return {
                'direction': 'flat',
                'magnitude': predicted_gap,
                'confidence': 'medium',
                'description': 'Flat open expected'
            }
    
    def get_us_market_sentiment(self):
        """
        Get US market closing data for context
        """
        try:
            sp500 = yf.Ticker('^GSPC')
            nasdaq = yf.Ticker('^IXIC')
            
            sp_hist = sp500.history(period='2d')
            nq_hist = nasdaq.history(period='2d')
            
            sp_change = ((sp_hist['Close'].iloc[-1] / sp_hist['Close'].iloc[-2]) - 1) * 100
            nq_change = ((nq_hist['Close'].iloc[-1] / nq_hist['Close'].iloc[-2]) - 1) * 100
            
            if sp_change > 0.5 and nq_change > 0.5:
                sentiment = 'bullish'
            elif sp_change < -0.5 and nq_change < -0.5:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
            
            return {
                'sp500_change': sp_change,
                'nasdaq_change': nq_change,
                'sentiment': sentiment
            }
            
        except Exception as e:
            logger.error(f"Failed to get US market data: {e}")
            return None
```

**3. models/screening/overnight_pipeline.py**
```python
"""
Main Overnight Screening Pipeline
Orchestrates the entire overnight process
"""

import sys
import logging
from datetime import datetime
from stock_scanner import StockScanner
from spi_monitor import SPIMonitor
from batch_predictor import BatchPredictor
from opportunity_scorer import OpportunityScorer
from report_generator import ReportGenerator
from progress_tracker import ScreenerProgress

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/screener_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class OvernightPipeline:
    def __init__(self):
        self.scanner = StockScanner()
        self.spi_monitor = SPIMonitor()
        self.predictor = BatchPredictor()
        self.scorer = OpportunityScorer()
        self.report_gen = ReportGenerator()
        self.progress = ScreenerProgress()
    
    def run(self, date=None):
        """
        Main execution function
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info("="*80)
        logger.info(f"OVERNIGHT STOCK SCREENER - {date}")
        logger.info("="*80)
        
        self.progress.start()
        
        try:
            # STAGE 1: Data Collection
            logger.info("Stage 1: Collecting market data...")
            stocks = self.collect_stocks()
            spi_data = self.spi_monitor.get_overnight_data()
            self.progress.update_stage('data_collection', 100, 'complete')
            
            # STAGE 2: LSTM Training (if needed)
            logger.info("Stage 2: Training LSTM models...")
            self.train_priority_models(stocks)
            self.progress.update_stage('lstm_training', 100, 'complete')
            
            # STAGE 3: Generate Predictions
            logger.info("Stage 3: Generating predictions...")
            predictions = self.predictor.predict_batch(stocks)
            self.progress.update_stage('prediction', 100, 'complete')
            
            # STAGE 4: Score Opportunities
            logger.info("Stage 4: Scoring opportunities...")
            scored = self.scorer.score_all(predictions, spi_data)
            self.progress.update_stage('scoring', 100, 'complete')
            
            # STAGE 5: Generate Report
            logger.info("Stage 5: Generating morning report...")
            report = self.report_gen.generate(scored, spi_data, date)
            self.progress.update_stage('report_generation', 100, 'complete')
            
            logger.info("="*80)
            logger.info("SCREENING COMPLETE!")
            logger.info(f"Report saved: {report['file_path']}")
            logger.info(f"Top opportunities: {len(report['top_picks'])}")
            logger.info("="*80)
            
            return report
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            self.progress.mark_failed(str(e))
            raise
    
    def collect_stocks(self):
        """
        Collect stocks from all sectors
        """
        all_stocks = []
        sectors = ['Financials', 'Materials', 'Healthcare', 'Technology', 
                   'Energy', 'Industrials', 'Consumer Staples', 'Real Estate']
        
        for sector in sectors:
            logger.info(f"Scanning {sector} sector...")
            stocks = self.scanner.select_top_stocks(sector, top_n=30)
            all_stocks.extend(stocks)
            logger.info(f"  Found {len(stocks)} stocks in {sector}")
        
        logger.info(f"Total stocks selected: {len(all_stocks)}")
        return all_stocks
    
    def train_priority_models(self, stocks):
        """
        Train LSTM models for stocks with stale models
        """
        # Check which models need updating
        stale_models = self.predictor.identify_stale_models(stocks)
        
        logger.info(f"Found {len(stale_models)} models requiring training")
        
        for i, stock in enumerate(stale_models):
            logger.info(f"Training {stock['symbol']} ({i+1}/{len(stale_models)})...")
            self.predictor.train_lstm(stock['symbol'], epochs=50)
            progress = ((i + 1) / len(stale_models)) * 100
            self.progress.update_stage('lstm_training', progress)

if __name__ == '__main__':
    pipeline = OvernightPipeline()
    pipeline.run()
```

---

## Summary & Timeline

### Total Implementation: 10 Weeks

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | Week 1-2 | Core architecture & file structure |
| Phase 2 | Week 3-4 | ASX stock scanner & SPI monitor |
| Phase 3 | Week 5-6 | Prediction engine & scoring |
| Phase 4 | Week 7 | Morning report generator |
| Phase 5 | Week 8 | Scheduling & automation |
| Phase 6 | Week 9-10 | Multi-market expansion |
| Testing | Week 11 | End-to-end testing |
| Deploy | Week 12 | Production deployment |

### Next Steps

1. **Approve this plan**
2. **Start with Phase 1** - Core architecture
3. **Create ASX sector configuration** - Stock lists
4. **Test overnight scheduling** - Windows Task Scheduler
5. **Build iteratively** - Deploy each phase as it completes

---

**Ready to proceed with implementation?** Let me know if you want me to start creating the actual Python files for Phase 1!
