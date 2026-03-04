# Market-Specific Pipeline Runners v1.3.11

**Automated trading pipelines for AU, US, and UK markets**

---

## 📋 Overview

Three specialized pipeline runners for automated trading across global markets:

1. **`run_au_pipeline.py`** - Australian (ASX) market
2. **`run_us_pipeline.py`** - US (NYSE/NASDAQ) markets
3. **`run_uk_pipeline.py`** - UK (LSE/London) market

Each pipeline includes:
- ✅ Market-specific trading hours
- ✅ Market calendar integration (holidays)
- ✅ Pre-configured stock presets
- ✅ Timezone-aware scheduling
- ✅ Currency tracking (AUD/USD/GBP)
- ✅ Real-time ML signals
- ✅ Paper trading coordination

---

## 🇦🇺 Australian (ASX) Pipeline

### Trading Hours:
- **Local**: 10:00-16:00 AEDT
- **GMT**: 00:00-06:00 GMT

### Usage:

**Python:**
```bash
# Using preset
python run_au_pipeline.py --preset "ASX Blue Chips" --capital 100000

# Custom symbols
python run_au_pipeline.py --symbols CBA.AX,BHP.AX,RIO.AX --capital 50000

# List presets
python run_au_pipeline.py --list-presets

# Run outside market hours (testing)
python run_au_pipeline.py --preset "ASX Banks" --ignore-market-hours
```

**Windows Batch:**
```batch
RUN_AU_PIPELINE.bat
```

### ASX Stock Presets:

| Preset | Stocks | Count |
|--------|--------|-------|
| **ASX Blue Chips** | CBA, BHP, RIO, WOW, CSL, WES, NAB, ANZ | 8 |
| **ASX Banks** | CBA, NAB, WBC, ANZ, MQG, BOQ | 6 |
| **ASX Mining** | BHP, RIO, FMG, NCM, S32, IGO, MIN | 7 |
| **ASX Tech** | WTC, XRO, CPU, APX, TNE | 5 |
| **ASX Energy** | WDS, STO, ORG, WHC, ALD | 5 |
| **ASX Healthcare** | CSL, COH, RMD, SHL, FPH | 5 |
| **ASX Retail** | WOW, WES, HVN, JBH, SUL | 5 |
| **ASX Top 20** | Top 20 ASX stocks | 20 |

---

## 🇺🇸 US (NYSE/NASDAQ) Pipeline

### Trading Hours:
- **Local**: 09:30-16:00 EST
- **GMT**: 14:30-21:00 GMT

### Usage:

**Python:**
```bash
# Using preset
python run_us_pipeline.py --preset "US Tech Giants" --capital 100000

# Custom symbols
python run_us_pipeline.py --symbols AAPL,MSFT,GOOGL --capital 50000

# List presets
python run_us_pipeline.py --list-presets

# Run outside market hours (testing)
python run_us_pipeline.py --preset "FAANG" --ignore-market-hours
```

**Windows Batch:**
```batch
RUN_US_PIPELINE.bat
```

### US Stock Presets:

| Preset | Stocks | Count |
|--------|--------|-------|
| **US Tech Giants** | AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AMD | 8 |
| **US Blue Chips** | AAPL, MSFT, JPM, JNJ, WMT, PG, UNH, V | 8 |
| **US Growth** | TSLA, NVDA, AMD, PLTR, SQ, COIN, SNOW, NET | 8 |
| **US Financials** | JPM, BAC, WFC, GS, MS, C, USB, PNC | 8 |
| **US Healthcare** | JNJ, UNH, LLY, PFE, ABBV, TMO, ABT, MRK | 8 |
| **US Energy** | XOM, CVX, COP, SLB, EOG, PXD, MPC, VLO | 8 |
| **US Consumer** | AMZN, WMT, HD, MCD, NKE, SBUX, TGT, LOW | 8 |
| **US Dividend** | JNJ, PG, KO, PEP, XOM, CVX, VZ, T | 8 |
| **FAANG** | META, AAPL, AMZN, NFLX, GOOGL | 5 |
| **Magnificent 7** | AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA | 7 |
| **Dow Jones 10** | AAPL, MSFT, UNH, GS, HD, CAT, MCD, V, BA, IBM | 10 |
| **S&P 500 Top 10** | AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, BRK.B, UNH, JNJ | 10 |

---

## 🇬🇧 UK (LSE/London) Pipeline

### Trading Hours:
- **Local**: 08:00-16:30 GMT
- **GMT**: 08:00-16:30 GMT

### Usage:

**Python:**
```bash
# Using preset
python run_uk_pipeline.py --preset "FTSE 100 Top 10" --capital 100000

# Custom symbols
python run_uk_pipeline.py --symbols HSBA.L,BP.L,SHEL.L --capital 50000

# List presets
python run_uk_pipeline.py --list-presets

# Run outside market hours (testing)
python run_uk_pipeline.py --preset "UK Blue Chips" --ignore-market-hours
```

**Windows Batch:**
```batch
RUN_UK_PIPELINE.bat
```

### UK/LSE Stock Presets:

| Preset | Stocks | Count |
|--------|--------|-------|
| **FTSE 100 Top 10** | SHEL, AZN, HSBA, ULVR, BP, GSK, DGE, RIO, REL, NG | 10 |
| **FTSE 100 Banks** | HSBA, LLOY, BARC, NWG, STAN | 5 |
| **FTSE 100 Energy** | SHEL, BP, SSE, CNA, NG | 5 |
| **FTSE 100 Miners** | RIO, AAL, GLEN, ANTO | 4 |
| **FTSE 100 Pharma** | AZN, GSK, HLMA | 3 |
| **FTSE 100 Consumer** | ULVR, DGE, ABF, SBRY, TSCO, OCDO | 6 |
| **FTSE 100 Tech** | SMIN, AUTO, BT, WEIR | 4 |
| **FTSE 100 Utilities** | SSE, NG, SGRO, UU, SVT | 5 |
| **FTSE 100 Industrials** | RR, BAE, REL, IMB, EXPN | 5 |
| **FTSE 100 Telecoms** | VOD, BT | 2 |
| **FTSE 100 REITs** | LAND, SGRO, BLND, PSN | 4 |
| **UK Blue Chips** | HSBA, SHEL, BP, AZN, ULVR, GSK, DGE, RIO | 8 |
| **UK Dividend** | SHEL, BP, HSBA, GSK, VOD, IMB, SSE, NG | 8 |
| **UK Growth** | AZN, AUTO, OCDO, RR, WEIR, EXPN | 6 |

---

## 🌍 Global Market Coverage

### 24-Hour Trading Window:

```
Time (GMT)    | Market    | Status
--------------|-----------|--------
00:00-06:00   | ASX       | OPEN ✅
06:00-08:00   | -         | All closed
08:00-16:30   | LSE       | OPEN ✅
14:30-16:30   | LSE + US  | BOTH OPEN ✅✅
16:30-21:00   | US        | OPEN ✅
21:00-00:00   | -         | All closed
```

**Overlap Periods:**
- **LSE + US**: 14:30-16:30 GMT (2 hours)
- **ASX + LSE**: No overlap
- **ASX + US**: No overlap

---

## 🚀 Quick Start

### 1. Windows Users:

**ASX:**
```batch
cd C:\path\to\phase3_intraday_deployment
RUN_AU_PIPELINE.bat
```

**US:**
```batch
cd C:\path\to\phase3_intraday_deployment
RUN_US_PIPELINE.bat
```

**UK:**
```batch
cd C:\path\to\phase3_intraday_deployment
RUN_UK_PIPELINE.bat
```

### 2. Python Users:

**ASX:**
```bash
cd /path/to/phase3_intraday_deployment
python run_au_pipeline.py --preset "ASX Blue Chips"
```

**US:**
```bash
cd /path/to/phase3_intraday_deployment
python run_us_pipeline.py --preset "US Tech Giants"
```

**UK:**
```bash
cd /path/to/phase3_intraday_deployment
python run_uk_pipeline.py --preset "FTSE 100 Top 10"
```

---

## 📊 Features

### Market Hours Checking:
- ✅ Automatic market open/close detection
- ✅ Holiday calendar integration
- ✅ Timezone-aware scheduling
- ✅ Next market open notification

### Stock Presets:
- ✅ Pre-configured lists for each market
- ✅ Blue chips, sectors, indices
- ✅ Easy selection via command line
- ✅ Custom symbol support

### Trading Features:
- ✅ Real-time price data (yfinance)
- ✅ ML signal generation
- ✅ Paper trading coordination
- ✅ Risk management
- ✅ Portfolio tracking
- ✅ Performance analytics

### Logging:
- ✅ Separate log file per market
- ✅ `logs/au_pipeline.log`
- ✅ `logs/us_pipeline.log`
- ✅ `logs/uk_pipeline.log`

---

## 🛠️ Configuration

### Market-Specific Config:

Each pipeline uses the same configuration file:
```
config/live_trading_config.json
```

But applies market-specific settings:
- Trading hours
- Holiday calendars
- Currency (AUD/USD/GBP)
- Tax rules (ATO/IRS/HMRC)

### Custom Configuration:

```bash
python run_au_pipeline.py --preset "ASX Banks" --config custom_config.json
python run_us_pipeline.py --preset "FAANG" --config custom_config.json
python run_uk_pipeline.py --preset "UK Blue Chips" --config custom_config.json
```

---

## 📈 Example Workflows

### Workflow 1: ASX Day Trading
```bash
# Morning: Start ASX pipeline (10:00 AEDT)
python run_au_pipeline.py --preset "ASX Blue Chips" --capital 100000

# Monitor until close (16:00 AEDT)
# Ctrl+C to stop

# Evening: Review logs
cat logs/au_pipeline.log
```

### Workflow 2: US Evening Trading (from AU)
```bash
# Evening: Start US pipeline (00:30 AEDT / 09:30 EST)
python run_us_pipeline.py --preset "US Tech Giants" --capital 100000

# Monitor until close (07:00 AEDT / 16:00 EST)
# Ctrl+C to stop
```

### Workflow 3: UK + US Overlap
```bash
# Start UK pipeline at 19:00 AEDT (08:00 GMT)
python run_uk_pipeline.py --preset "FTSE 100 Top 10" --capital 100000 &

# Start US pipeline at 01:30 AEDT (14:30 GMT)
python run_us_pipeline.py --preset "US Blue Chips" --capital 100000 &

# Trade both markets simultaneously during overlap
# Stop both: Ctrl+C or pkill -f "run_.*_pipeline"
```

### Workflow 4: Multi-Market Portfolio
```bash
# Terminal 1: ASX
python run_au_pipeline.py --preset "ASX Banks" --capital 50000

# Terminal 2: US
python run_us_pipeline.py --preset "US Financials" --capital 50000

# Terminal 3: UK
python run_uk_pipeline.py --preset "FTSE 100 Banks" --capital 50000
```

---

## 🔧 Troubleshooting

### Issue: Market hours check fails

**Solution:**
```bash
# Ignore market hours for testing
python run_au_pipeline.py --preset "ASX Blue Chips" --ignore-market-hours
python run_us_pipeline.py --preset "FAANG" --ignore-market-hours
python run_uk_pipeline.py --preset "UK Blue Chips" --ignore-market-hours
```

### Issue: Symbol format errors

**ASX symbols must end with `.AX`:**
```python
# Correct
CBA.AX, BHP.AX, RIO.AX

# Wrong
CBA, BHP, RIO
```

**US symbols have no suffix:**
```python
# Correct
AAPL, MSFT, GOOGL

# Wrong
AAPL.US, MSFT.NYSE
```

**UK symbols must end with `.L`:**
```python
# Correct
HSBA.L, BP.L, SHEL.L

# Wrong
HSBA, BP, SHEL
```

### Issue: Import errors

**Solution:**
```bash
# Install dependencies
cd phase3_intraday_deployment
pip install -r requirements.txt

# Verify imports
python -c "from paper_trading_coordinator import PaperTradingCoordinator"
python -c "from ml_pipeline.market_calendar import MarketCalendar"
```

---

## 📚 Command Reference

### Common Arguments:

| Argument | Description | Example |
|----------|-------------|---------|
| `--symbols` | Custom stock list | `--symbols CBA.AX,BHP.AX` |
| `--preset` | Use predefined preset | `--preset "ASX Blue Chips"` |
| `--capital` | Initial capital | `--capital 50000` |
| `--config` | Config file path | `--config my_config.json` |
| `--ignore-market-hours` | Skip market hours check | `--ignore-market-hours` |
| `--list-presets` | Show all presets | `--list-presets` |

---

## ✅ Summary

### What You Get:

✅ **3 market-specific pipelines** (AU, US, UK)  
✅ **50+ stock presets** across all markets  
✅ **Market hours automation** with calendars  
✅ **24-hour global coverage** (with scheduling)  
✅ **Easy Windows launchers** (.bat files)  
✅ **Flexible Python CLI** (command line)  
✅ **Paper trading integration** (ML signals)  
✅ **Real-time monitoring** (portfolio tracking)

### Files Included:

- `run_au_pipeline.py` - ASX pipeline
- `run_us_pipeline.py` - US pipeline
- `run_uk_pipeline.py` - UK pipeline
- `RUN_AU_PIPELINE.bat` - Windows launcher (ASX)
- `RUN_US_PIPELINE.bat` - Windows launcher (US)
- `RUN_UK_PIPELINE.bat` - Windows launcher (UK)
- `MARKET_PIPELINES_README.md` - This file

---

**Created:** January 3, 2026  
**Version:** v1.3.11  
**Status:** Production Ready ✅

**Trade the world, 24 hours a day!** 🌍📈
