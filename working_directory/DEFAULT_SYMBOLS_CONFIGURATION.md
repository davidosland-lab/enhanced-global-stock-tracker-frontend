# 📋 Default Symbols Configuration

## ❓ **Are There Hardcoded Stocks?**

Yes, there are **default symbols** configured, but they are **easily customizable**!

---

## 🔍 **Where Are the Default Symbols?**

### 1. **Enhanced Unified Platform** (Recommended Entry Point)

**File:** `enhanced_unified_platform.py`  
**Line:** 281  
**Default Symbols:** `AAPL,GOOGL,MSFT,NVDA`

```python
parser.add_argument(
    '--symbols',
    type=str,
    default='AAPL,GOOGL,MSFT,NVDA',  # <-- DEFAULT HERE
    help='Comma-separated list of symbols (default: AAPL,GOOGL,MSFT,NVDA)'
)
```

### 2. **Paper Trading Coordinator**

**File:** `phase3_intraday_deployment/paper_trading_coordinator.py`  
**Line:** 1271  
**Default Symbols:** `AAPL,GOOGL,MSFT`

```python
parser.add_argument('--symbols', type=str, default='AAPL,GOOGL,MSFT',
                   help='Comma-separated list of symbols to trade')
```

### 3. **Unified Trading Platform** (Dashboard Only)

**File:** `unified_trading_platform.py`  
**Default Symbols:** `AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, NFLX`

---

## 🎯 **How to Change Default Symbols**

### **Option 1: Command Line (NO CODE CHANGES NEEDED)** ✅ Recommended

You can override defaults when launching:

```bash
# Use YOUR symbols (Australian stocks like CBA)
python enhanced_unified_platform.py --symbols CBA.AX,BHP.AX,NAB.AX,WBC.AX --real-signals

# Or any stocks you want
python enhanced_unified_platform.py --symbols TSLA,NVDA,AMD,META --real-signals

# Single stock
python enhanced_unified_platform.py --symbols CBA.AX --real-signals --capital 50000
```

### **Option 2: Edit the Default** (Permanent Change)

If you want CBA.AX and other Australian stocks as the **permanent default**:

#### **File:** `enhanced_unified_platform.py` (Line 281)

**Change from:**
```python
default='AAPL,GOOGL,MSFT,NVDA',
```

**To:**
```python
default='CBA.AX,BHP.AX,NAB.AX,WBC.AX',  # Australian stocks
```

#### **File:** `paper_trading_coordinator.py` (Line 1271)

**Change from:**
```python
default='AAPL,GOOGL,MSFT',
```

**To:**
```python
default='CBA.AX,BHP.AX,NAB.AX',  # Australian stocks
```

---

## 🌏 **Examples for Different Markets**

### **Australian Stocks (ASX)**
```bash
python enhanced_unified_platform.py --symbols CBA.AX,BHP.AX,NAB.AX,WBC.AX,CSL.AX --real-signals
```

**Popular ASX Stocks:**
- `CBA.AX` - Commonwealth Bank
- `BHP.AX` - BHP Group
- `NAB.AX` - National Australia Bank
- `WBC.AX` - Westpac Banking
- `CSL.AX` - CSL Limited
- `WES.AX` - Wesfarmers
- `WOW.AX` - Woolworths
- `ANZ.AX` - ANZ Banking

### **US Tech Stocks**
```bash
python enhanced_unified_platform.py --symbols AAPL,GOOGL,MSFT,NVDA,TSLA,META,AMD --real-signals
```

### **European Stocks**
```bash
python enhanced_unified_platform.py --symbols SAP.DE,SIE.DE,VOW3.DE,DAI.DE --real-signals
```

### **Mixed Markets**
```bash
python enhanced_unified_platform.py --symbols AAPL,CBA.AX,SAP.DE,TSLA --real-signals
```

---

## ⚙️ **Configuration File Method** (Advanced)

For more permanent configuration, you can edit:

**File:** `phase3_intraday_deployment/config/live_trading_config.json`

```json
{
  "symbols": ["CBA.AX", "BHP.AX", "NAB.AX", "WBC.AX"],
  "initial_capital": 100000,
  "swing_trading": {
    "enabled": true,
    "max_position_size": 0.20
  }
}
```

Then launch with:
```bash
python enhanced_unified_platform.py --config config/live_trading_config.json
```

---

## 🔄 **Dynamic Symbol Management**

The system also supports **adding/removing symbols dynamically** through the dashboard!

### **In the Dashboard:**

1. **Manual Trading Section**
   - Type any symbol (e.g., `CBA.AX`)
   - It will automatically fetch real-time data
   - No need to restart

2. **Via API** (for automation)
```python
# Add new symbol
POST /api/manual/add_symbol
{
    "symbol": "CBA.AX"
}

# Remove symbol
POST /api/manual/remove_symbol
{
    "symbol": "AAPL"
}
```

---

## 📊 **Market Data Support**

The system uses **yfinance** which supports:

- ✅ **US Stocks** - AAPL, GOOGL, TSLA, etc.
- ✅ **Australian Stocks** - *.AX (ASX)
- ✅ **European Stocks** - *.DE (Germany), *.L (London), etc.
- ✅ **Asian Markets** - *.HK (Hong Kong), *.T (Tokyo), etc.
- ✅ **Canadian Stocks** - *.TO (Toronto)
- ✅ **ETFs** - SPY, QQQ, VOO, etc.
- ✅ **Cryptocurrencies** - BTC-USD, ETH-USD, etc.

### **Symbol Format Examples:**

| Market | Symbol Format | Example |
|--------|---------------|---------|
| US | SYMBOL | AAPL, GOOGL, TSLA |
| Australia | SYMBOL.AX | CBA.AX, BHP.AX |
| Germany | SYMBOL.DE | SAP.DE, SIE.DE |
| London | SYMBOL.L | HSBA.L, BP.L |
| Hong Kong | SYMBOL.HK | 0700.HK, 0941.HK |
| Tokyo | SYMBOL.T | 7203.T, 6758.T |
| Canada | SYMBOL.TO | RY.TO, TD.TO |
| Crypto | SYMBOL-USD | BTC-USD, ETH-USD |

---

## 🎯 **Recommended Setup for Your Use Case**

Since you're trading **CBA.AX** (Commonwealth Bank of Australia), I recommend:

### **Permanent Change** (Edit defaults)

**File:** `enhanced_unified_platform.py` (Line 281)

```python
default='CBA.AX,BHP.AX,NAB.AX,WBC.AX,CSL.AX',
```

### **Or Launch Command** (No code changes)

```bash
# For CBA focus
python enhanced_unified_platform.py --symbols CBA.AX --real-signals --capital 100000

# For multiple Australian banks
python enhanced_unified_platform.py --symbols CBA.AX,NAB.AX,WBC.AX,ANZ.AX --real-signals

# For diversified Australian portfolio
python enhanced_unified_platform.py --symbols CBA.AX,BHP.AX,CSL.AX,WES.AX,WOW.AX --real-signals
```

---

## ✅ **Summary**

**Are there hardcoded stocks?**  
Yes - `AAPL,GOOGL,MSFT,NVDA` are defaults

**Can you change them?**  
YES! Three ways:
1. **Command line** (easiest) - `--symbols CBA.AX,BHP.AX`
2. **Edit default** (permanent) - Change line 281 in `enhanced_unified_platform.py`
3. **Config file** (advanced) - Edit `config/live_trading_config.json`

**Can you trade Australian stocks?**  
YES! Use `.AX` suffix: `CBA.AX`, `BHP.AX`, etc.

**Can you trade multiple markets?**  
YES! Mix any markets: `AAPL,CBA.AX,SAP.DE`

---

## 🚀 **Quick Start for CBA.AX Trading**

```bash
cd C:\Users\david\AATelS

# Launch with CBA.AX
python enhanced_unified_platform.py --symbols CBA.AX --real-signals --capital 100000

# Access dashboard
# http://localhost:5000

# Start trading!
```

---

**Updated: December 25, 2024**  
**Version: 1.2.3**  
**All Markets Supported!** 🌏
