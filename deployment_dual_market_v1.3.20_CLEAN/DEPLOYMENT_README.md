# Dual Market Screening System Deployment Package

**Version**: Event Risk Guard v1.3.20 + US Market Pipeline v1.0.0  
**Package**: Dual_Market_Screening_v1.3.20_20251121.zip  
**Date**: 2025-11-21  
**Status**: ✅ PRODUCTION READY

---

## 📦 Package Contents

This deployment package includes:

### ✅ ASX Market Pipeline (Event Risk Guard v1.3.20)
- 240 ASX stocks across 8 sectors
- SPI (^AXJO) market sentiment analysis
- Market regime engine with crash risk detection
- Event risk guard (Basel III, earnings protection)
- Complete overnight screening workflow

### ✅ US Market Pipeline (v1.0.0) 
- 240 US stocks across 8 sectors
- S&P 500 (^GSPC) and VIX (^VIX) analysis
- US market regime engine (HMM-based)
- NYSE/NASDAQ screening infrastructure
- Complete overnight screening workflow

### ✅ Unified System
- Single launcher for both markets
- Parallel and sequential execution modes
- Shared prediction and scoring engines
- Comprehensive reporting system

---

## 🚀 Quick Start

### Installation

```bash
# Extract package
unzip Dual_Market_Screening_v1.3.20_20251121.zip
cd deployment_dual_market_v1.3.20

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from models.screening.us_stock_scanner import USStockScanner; print('✓ Ready')"
```

### Usage

```bash
# Run US market only
python run_screening.py --market us

# Run ASX market only
python run_screening.py --market asx

# Run both markets
python run_screening.py --market both

# Run both in parallel (faster)
python run_screening.py --market both --parallel
```

---

## 📊 System Coverage

| Market | Stocks | Sectors | Primary Index | Volatility Index |
|--------|--------|---------|---------------|------------------|
| **ASX** | 240 | 8 | ^AXJO (ASX 200) | N/A |
| **US** | 240 | 8 | ^GSPC (S&P 500) | ^VIX |
| **TOTAL** | 480 | 16 | Dual coverage | Complete |

---

## 📁 Directory Structure

```
deployment_dual_market_v1.3.20/
├── models/
│   ├── config/
│   │   ├── asx_sectors.json          # ASX configuration
│   │   ├── us_sectors.json           # US configuration
│   │   └── us_market_config.py       # US parameters
│   └── screening/
│       ├── overnight_pipeline.py     # ASX pipeline
│       ├── us_overnight_pipeline.py  # US pipeline
│       ├── spi_monitor.py            # ASX sentiment
│       ├── us_market_monitor.py      # US sentiment
│       ├── market_regime_engine.py   # ASX regime
│       ├── us_market_regime_engine.py # US regime
│       ├── stock_scanner.py          # ASX scanner
│       ├── us_stock_scanner.py       # US scanner
│       └── [shared modules...]       # Common components
├── run_screening.py                  # Unified launcher
├── requirements.txt                  # Dependencies
├── DEPLOYMENT_README.md              # This file
├── US_MARKET_PIPELINE_README.md      # US documentation
├── US_PIPELINE_DEPLOYMENT_SUMMARY.md # Deployment guide
├── QUICK_START_US_PIPELINE.txt       # Quick reference
└── ROLLBACK_POINT_v1.3.20_REGIME_FINAL.md # ASX docs
```

---

## ⚙️ Configuration

### ASX Market
- Config: `models/config/asx_sectors.json`
- Min Market Cap: $500M AUD
- Min Volume: 500K shares/day
- Price Range: $0.50 - $500

### US Market
- Config: `models/config/us_sectors.json`
- Min Market Cap: $2B USD
- Min Volume: 1M shares/day
- Price Range: $5 - $1,000

---

## 🔧 Requirements

### System Requirements
- Python 3.8+
- 4GB+ RAM
- 2GB+ disk space
- Internet connection

### Python Dependencies
```
yahooquery>=2.3.0
pandas>=1.3.0
numpy>=1.21.0
hmmlearn>=0.2.7
scikit-learn>=1.0.0
```

Install all: `pip install -r requirements.txt`

---

## 📈 Execution Times

| Configuration | Duration |
|---------------|----------|
| US market (30 stocks/sector) | 15-20 min |
| ASX market (30 stocks/sector) | 15-20 min |
| Both markets (sequential) | 30-40 min |
| Both markets (parallel) | 20-25 min |
| Quick test (5 stocks/sector) | 2-3 min |

---

## 📊 Output Locations

### Reports
- ASX: `reports/morning_report_YYYYMMDD.html`
- US: `reports/us/us_morning_report_YYYYMMDD.html`

### Data
- ASX: `data/pipeline_results_YYYYMMDD.json`
- US: `data/us/us_pipeline_results_YYYYMMDD.json`

### Logs
- ASX: `logs/screening/overnight_pipeline.log`
- US: `logs/screening/us/us_overnight_pipeline.log`

---

## ✅ Verification

### Test Individual Components

```bash
# Test US market monitor
python models/screening/us_market_monitor.py

# Test US stock scanner
python models/screening/us_stock_scanner.py

# Test US regime engine
python models/screening/us_market_regime_engine.py
```

### Run Quick Test

```bash
# Test with 5 stocks per sector
python run_screening.py --market both --stocks 5
```

---

## 🔄 Scheduling

### Daily Execution (Before Market Open)

```bash
# Cron job (6 AM ET for both markets)
0 6 * * 1-5 cd /path/to/deployment_dual_market_v1.3.20 && python run_screening.py --market both

# Or run separately
0 6 * * 1-5 cd /path/to/deployment_dual_market_v1.3.20 && python run_screening.py --market asx
0 7 * * 1-5 cd /path/to/deployment_dual_market_v1.3.20 && python run_screening.py --market us
```

---

## 🆘 Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Data Fetch Issues
- Check internet connection
- Verify yahooquery service status
- Check logs in `logs/screening/`

### Memory Issues
- Reduce stocks per sector: `--stocks 20`
- Run markets separately
- Close other applications

---

## 📚 Documentation

- **US Pipeline Guide**: US_MARKET_PIPELINE_README.md
- **US Quick Start**: QUICK_START_US_PIPELINE.txt
- **US Deployment**: US_PIPELINE_DEPLOYMENT_SUMMARY.md
- **ASX Rollback Point**: ROLLBACK_POINT_v1.3.20_REGIME_FINAL.md

---

## 🔐 Important Notes

⚠️ **NOT FINANCIAL ADVICE** - Educational/research use only  
⚠️ **No Guarantees** - Past performance ≠ future results  
⚠️ **User Responsibility** - All trading decisions at own risk  

---

## 📝 Version Information

| Component | Version | Status |
|-----------|---------|--------|
| ASX Pipeline | Event Risk Guard v1.3.20 | ✅ Stable |
| US Pipeline | v1.0.0 | ✅ Production Ready |
| Market Regime Engine | ASX + US | ✅ Complete |
| Unified Launcher | v1.0.0 | ✅ Operational |

---

## 🎉 Ready to Deploy

This package is **production-ready** and can be deployed immediately.

Start with a test run:
```bash
python run_screening.py --market both --stocks 10
```

Then scale to full production:
```bash
python run_screening.py --market both --parallel
```

---

**Package Date**: 2025-11-21  
**Maintainer**: Event Risk Guard Team  
**Support**: Check logs and documentation files
