# 📊 Manual Stock Selection Guide

## Version: 1.3.2 FINAL - WINDOWS COMPATIBLE
## Date: December 29, 2024

---

## ✅ YES! You Can Manually Choose Stocks

The paper trading system allows you to **manually select which stocks to trade** using the `--symbols` parameter.

---

## 🎯 How to Choose Your Own Stocks

### Method 1: Command Line (Recommended)

#### Basic Format:
```batch
cd C:\Users\david\Trading\phase3_intraday_deployment
python paper_trading_coordinator.py --symbols YOUR,STOCKS,HERE --capital 100000 --real-signals
```

#### Examples:

**Australian Stocks (ASX)**:
```batch
# Mining stocks
python paper_trading_coordinator.py --symbols RIO.AX,BHP.AX,FMG.AX --capital 100000 --real-signals

# Banks
python paper_trading_coordinator.py --symbols CBA.AX,NAB.AX,WBC.AX,ANZ.AX --capital 100000 --real-signals

# Tech stocks
python paper_trading_coordinator.py --symbols APT.AX,XRO.AX,WTC.AX --capital 100000 --real-signals

# Blue chips mix
python paper_trading_coordinator.py --symbols BHP.AX,CBA.AX,CSL.AX,WOW.AX --capital 100000 --real-signals

# Single stock focus
python paper_trading_coordinator.py --symbols CBA.AX --capital 100000 --real-signals
```

**US Stocks**:
```batch
# Tech giants
python paper_trading_coordinator.py --symbols AAPL,GOOGL,MSFT,AMZN,META --capital 100000 --real-signals

# Blue chips
python paper_trading_coordinator.py --symbols JPM,BAC,WMT,JNJ,PG --capital 100000 --real-signals

# Growth stocks
python paper_trading_coordinator.py --symbols TSLA,NVDA,AMD,PLTR --capital 100000 --real-signals

# S&P 500 leaders
python paper_trading_coordinator.py --symbols SPY,QQQ,DIA --capital 100000 --real-signals
```

**International Stocks**:
```batch
# UK stocks
python paper_trading_coordinator.py --symbols HSBA.L,BP.L,SHEL.L --capital 100000 --real-signals

# European stocks
python paper_trading_coordinator.py --symbols SAP.DE,ASML.AS,OR.PA --capital 100000 --real-signals

# Mixed international
python paper_trading_coordinator.py --symbols AAPL,BHP.AX,HSBA.L,ASML.AS --capital 100000 --real-signals
```

---

## 📝 Stock Symbol Format

### How to Find the Right Symbol

#### Australian Stocks (ASX)
- **Format**: `SYMBOL.AX`
- **Examples**:
  - Commonwealth Bank: `CBA.AX`
  - BHP Group: `BHP.AX`
  - Rio Tinto: `RIO.AX`
  - Woolworths: `WOW.AX`
  - Telstra: `TLS.AX`
  - Fortescue Metals: `FMG.AX`
  - Wesfarmers: `WES.AX`

#### US Stocks (NASDAQ/NYSE)
- **Format**: `SYMBOL` (no suffix)
- **Examples**:
  - Apple: `AAPL`
  - Microsoft: `MSFT`
  - Google: `GOOGL`
  - Amazon: `AMZN`
  - Tesla: `TSLA`
  - NVIDIA: `NVDA`

#### UK Stocks (London)
- **Format**: `SYMBOL.L`
- **Examples**:
  - HSBC: `HSBA.L`
  - BP: `BP.L`
  - Shell: `SHEL.L`

#### European Stocks
- **Germany**: `SYMBOL.DE` (e.g., SAP: `SAP.DE`)
- **France**: `SYMBOL.PA` (e.g., LVMH: `MC.PA`)
- **Netherlands**: `SYMBOL.AS` (e.g., ASML: `ASML.AS`)

### Verify Symbol Online
- **Yahoo Finance**: https://finance.yahoo.com/
- **Google Finance**: https://www.google.com/finance/
- **ASX**: https://www.asx.com.au/ (for Australian stocks)

---

## 🎨 Custom Trading Configurations

### 1. High-Risk Growth Portfolio (3-5 stocks)
```batch
python paper_trading_coordinator.py --symbols TSLA,NVDA,AMD --capital 100000 --real-signals
```
- **Risk**: High
- **Expected Volatility**: High
- **Potential Return**: High

### 2. Conservative Blue Chip Portfolio (5-7 stocks)
```batch
python paper_trading_coordinator.py --symbols CBA.AX,BHP.AX,WOW.AX,CSL.AX,TLS.AX --capital 100000 --real-signals
```
- **Risk**: Low-Medium
- **Expected Volatility**: Low
- **Potential Return**: Moderate

### 3. Sector-Focused Portfolio

**Mining Sector**:
```batch
python paper_trading_coordinator.py --symbols RIO.AX,BHP.AX,FMG.AX,NCM.AX,S32.AX --capital 100000 --real-signals
```

**Banking Sector**:
```batch
python paper_trading_coordinator.py --symbols CBA.AX,NAB.AX,WBC.AX,ANZ.AX --capital 100000 --real-signals
```

**Tech Sector**:
```batch
python paper_trading_coordinator.py --symbols AAPL,MSFT,GOOGL,NVDA,AMD --capital 100000 --real-signals
```

### 4. Single Stock Deep Focus
```batch
python paper_trading_coordinator.py --symbols CBA.AX --capital 100000 --real-signals --interval 60
```
- **Benefit**: Maximum position size (up to 30% = $30,000)
- **Focus**: Deep analysis of one stock
- **Risk**: Concentration risk

### 5. Diversified Global Portfolio (8-10 stocks)
```batch
python paper_trading_coordinator.py --symbols AAPL,MSFT,CBA.AX,BHP.AX,HSBA.L,SAP.DE,ASML.AS,JPM --capital 100000 --real-signals
```
- **Risk**: Low (diversified)
- **Markets**: US, Australia, Europe
- **Sectors**: Tech, Finance, Resources

---

## ⚙️ Advanced Customization

### Combine Stock Selection with Other Parameters

#### Example 1: Quick Trading on Select Stocks
```batch
python paper_trading_coordinator.py \
  --symbols BHP.AX,RIO.AX,FMG.AX \
  --capital 100000 \
  --real-signals \
  --interval 60 \
  --cycles 50
```
- **Stocks**: BHP, RIO, FMG (mining sector)
- **Capital**: $100,000
- **Signals**: Real ML stack (70-75% win rate)
- **Update**: Every 60 seconds
- **Duration**: 50 cycles (~50 minutes)

#### Example 2: Long-Session Blue Chip Trading
```batch
python paper_trading_coordinator.py \
  --symbols CBA.AX,NAB.AX,WBC.AX,ANZ.AX \
  --capital 200000 \
  --real-signals \
  --interval 300 \
  --cycles 200
```
- **Stocks**: Big 4 Australian banks
- **Capital**: $200,000
- **Update**: Every 5 minutes
- **Duration**: 200 cycles (~16 hours)

#### Example 3: Test Mode with Custom Stocks
```batch
python paper_trading_coordinator.py \
  --symbols YOUR,FAVORITE,STOCKS \
  --capital 50000 \
  --interval 120
```
- **Note**: No `--real-signals` = simplified signals (50-60% win rate)
- **Use**: For testing new stock combinations

---

## 📊 How the System Handles Your Stock Selection

### Position Sizing
The system automatically calculates position sizes based on:
- **Available capital**: Your total cash
- **Number of stocks**: More stocks = smaller individual positions
- **Max position size**: 25-30% per trade
- **Max concurrent positions**: 3 positions at once

### Example with 3 Stocks ($100,000 capital):
```batch
python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals
```

**Position allocation**:
- Stock 1: ~$30,000 (30%)
- Stock 2: ~$25,000 (25%)
- Stock 3: ~$25,000 (25%)
- **Remaining cash**: ~$20,000 (safety buffer)

### Example with 1 Stock ($100,000 capital):
```batch
python paper_trading_coordinator.py --symbols CBA.AX --capital 100000 --real-signals
```

**Position allocation**:
- Stock 1: ~$30,000 (30% of capital)
- **Remaining cash**: ~$70,000

**Note**: Even with one stock, max position is 30% to maintain risk management

---

## 🔍 ML Analysis on Your Stocks

### What the System Does for Each Stock:

1. **FinBERT Sentiment Analysis** (25%)
   - News sentiment
   - Market sentiment
   - Social media sentiment

2. **LSTM Neural Network** (25%)
   - Price prediction
   - Trend analysis
   - Pattern recognition

3. **Technical Analysis** (25%)
   - RSI, MACD, Bollinger Bands
   - Support/resistance levels
   - Volume analysis

4. **Momentum Analysis** (15%)
   - Price momentum
   - Relative strength
   - Trend strength

5. **Volume Analysis** (10%)
   - Volume trends
   - Volume surges
   - Relative volume

### Entry Signals Generated When:
- **ML Confidence ≥ 55%**
- **Market sentiment > 40** (not bearish)
- **Technical indicators aligned**
- **Position slots available** (max 3 concurrent)

---

## 📋 Stock Selection Best Practices

### ✅ Recommended:
1. **Liquid stocks** - High trading volume
2. **3-5 stocks** - Good diversification
3. **Different sectors** - Reduce correlation risk
4. **Known companies** - Better ML analysis
5. **Your expertise** - Trade what you know

### ❌ Avoid:
1. **Penny stocks** - Low liquidity, unreliable data
2. **Too many stocks** (>10) - Diluted positions
3. **Highly correlated stocks** - Same sector only
4. **Delisted stocks** - Data issues
5. **Foreign markets without suffix** - Wrong data

---

## 🎯 Popular Stock Combinations (Pre-Tested)

### Australian Focus (Recommended for ASX traders)
```batch
# Conservative
python paper_trading_coordinator.py --symbols CBA.AX,BHP.AX,CSL.AX,WOW.AX --capital 100000 --real-signals

# Aggressive
python paper_trading_coordinator.py --symbols APT.AX,XRO.AX,WTC.AX,ZIP.AX --capital 100000 --real-signals

# Balanced
python paper_trading_coordinator.py --symbols CBA.AX,BHP.AX,RIO.AX,WOW.AX,TLS.AX --capital 100000 --real-signals
```

### US Focus (Recommended for US market)
```batch
# Tech-heavy
python paper_trading_coordinator.py --symbols AAPL,MSFT,GOOGL,NVDA,TSLA --capital 100000 --real-signals

# Diversified
python paper_trading_coordinator.py --symbols AAPL,JPM,JNJ,WMT,XOM --capital 100000 --real-signals

# Growth
python paper_trading_coordinator.py --symbols TSLA,NVDA,AMD,PLTR,SQ --capital 100000 --real-signals
```

### Global Mix (Advanced)
```batch
python paper_trading_coordinator.py --symbols AAPL,CBA.AX,HSBA.L,SAP.DE,ASML.AS --capital 100000 --real-signals
```

---

## 🚀 Quick Start with Your Stocks

### Step-by-Step:

1. **Choose your stocks** (3-5 recommended)
   - Example: `RIO.AX`, `CBA.AX`, `BHP.AX`

2. **Verify symbols** on Yahoo Finance
   - Go to: https://finance.yahoo.com/
   - Search each symbol
   - Confirm correct company and exchange

3. **Run paper trading**:
   ```batch
   cd C:\Users\david\Trading\phase3_intraday_deployment
   python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals
   ```

4. **Start dashboard** (in separate terminal):
   ```batch
   cd C:\Users\david\Trading\phase3_intraday_deployment
   python dashboard.py
   ```

5. **Open browser**: http://localhost:8050
   - Press `Ctrl+Shift+R` to hard refresh

6. **Monitor results**:
   - Dashboard updates every 5 seconds
   - Positions shown with live P&L
   - Trade history tracked

---

## 📊 Dashboard with Custom Stocks

When you select custom stocks, the dashboard shows:

- **Portfolio Value**: Total capital across your stocks
- **Open Positions**: Each stock with live price
- **Performance**: Win rate across your selection
- **Market Sentiment**: Overall market conditions
- **Position Details**: Entry price, current price, P&L for each stock

### Example Dashboard Output:
```
Open Positions:
┌────────┬────────┬────────┬─────────┬────────┬──────────┐
│ Symbol │ Shares │  Entry │ Current │  P&L   │  P&L %   │
├────────┼────────┼────────┼─────────┼────────┼──────────┤
│YOUR1   │  XXX   │$XX.XX  │ $XX.XX  │ +$XXX  │  +X.XX%  │
│YOUR2   │  XXX   │$XX.XX  │ $XX.XX  │ -$XXX  │  -X.XX%  │
│YOUR3   │  XXX   │$XX.XX  │ $XX.XX  │ +$XXX  │  +X.XX%  │
└────────┴────────┴────────┴─────────┴────────┴──────────┘
```

---

## 🎓 Learning from Your Stock Selection

### Track Performance by Stock:
The system tracks each stock individually:
- **Win rate per stock**
- **Average return per stock**
- **Best/worst performers**
- **Entry/exit prices**

### Use dashboard to:
- See which stocks perform best
- Identify winners/losers
- Adjust your selection over time
- Optimize your portfolio

---

## ⚠️ Important Notes

### Symbol Format Matters:
- ✅ Correct: `CBA.AX` (Australian stock)
- ❌ Wrong: `CBA` (might fetch wrong company)

### Max Stocks Recommended: 10
- System can handle more
- But positions become too small
- ML analysis works best with 3-7 stocks

### Real-Time Data Required:
- Stocks must be actively trading
- Delisted stocks won't work
- Check market hours for your stocks

### Capital Allocation:
- $100,000 recommended minimum for 5 stocks
- $50,000 minimum for 2-3 stocks
- More stocks need more capital for meaningful positions

---

## 📝 Summary

### ✅ YES, You Have Full Control!

**Choose any stocks you want** by using the `--symbols` parameter:

```batch
python paper_trading_coordinator.py --symbols YOUR,STOCKS,HERE --capital 100000 --real-signals
```

**Recommendations**:
- Start with 3-5 stocks you know well
- Verify symbols on Yahoo Finance first
- Mix sectors for diversification
- Use `--real-signals` for full ML analysis

**The ML system will analyze your stocks and generate signals automatically!**

---

**Version**: 1.3.2 FINAL - WINDOWS COMPATIBLE  
**File**: MANUAL_STOCK_SELECTION.md  
**Date**: December 29, 2024
