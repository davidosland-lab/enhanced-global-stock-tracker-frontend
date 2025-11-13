# SSS Scanner - Yahoo Finance Blocking Avoidance Analysis

## Repository Information
- **GitHub**: https://github.com/asafravid/sss
- **Description**: Stock Screener & Scanner focusing on fundamental analysis
- **Key Feature**: Dual data fetching strategy with **yfinance** AND **yahooquery**

---

## Critical Discovery: Dual Library Approach

### Strategy Overview
The SSS scanner uses **TWO DIFFERENT LIBRARIES** to fetch Yahoo Finance data:

1. **yfinance** (default mode) - Uses `.get_info()` and other methods
2. **yahooquery** (fallback mode) - Uses direct property access

This is controlled by a **`yq_mode`** flag throughout the codebase.

---

## Code Analysis

### Data Fetching Pattern (Lines 1540-1565)

#### When `yq_mode = False` (yfinance):
```python
info                     = symbol.get_info()
cash_flows_yearly        = symbol.get_cashflow(as_dict=True, freq="yearly")
cash_flows_quarterly     = symbol.get_cashflow(as_dict=True, freq="quarterly")
balance_sheets_yearly    = symbol.get_balance_sheet(as_dict=True, freq="yearly")
balance_sheets_quarterly = symbol.get_balance_sheet(as_dict=True, freq="quarterly")
earnings_yearly          = symbol.get_earnings(as_dict=True, freq="yearly")
earnings_quarterly       = symbol.get_earnings(as_dict=True, freq="quarterly")
```

**CRITICAL OBSERVATION**: They use `.get_info()`, `.get_cashflow()`, etc. - NOT `.info`, `.history()`, etc.

#### When `yq_mode = True` (yahooquery):
```python
if 'financialCurrency' in symbol.financial_data[stock_data.symbol]:
    stock_data.financial_currency = symbol.financial_data[stock_data.symbol]['financialCurrency']

if 'currency' in symbol.price[stock_data.symbol]:
    stock_data.summary_currency = symbol.price[stock_data.symbol]['currency']

# Later in code (lines 1615-1637):
balanceSheetHistoryYearly         = symbol.balance_sheet(frequency='a')
balanceSheetHistoryQuarterly      = symbol.balance_sheet(frequency='q')
cashflowStatementHistoryYearly    = symbol.cash_flow(frequency='a')
cashflowStatementHistoryQuarterly = symbol.cash_flow(frequency='q')
defaultKeyStatistics              = symbol.all_modules[symbol_key]['defaultKeyStatistics']
summaryDetail                     = symbol.all_modules[symbol_key]['summaryDetail']
assetProfile                      = symbol.all_modules[symbol_key]['assetProfile']
quoteType                         = symbol.all_modules[symbol_key]['quoteType']
earningsYearly                    = symbol.earnings[symbol_key]['financialsChart']['yearly']
earningsQuarterly                 = symbol.earnings[symbol_key]['financialsChart']['quarterly']
financialData                     = symbol.financial_data[symbol_key]
```

---

## Ticker Creation Function (Lines 2840-2849)

```python
def get_yfinance_ticker_wrapper(yq_mode, tase_mode, symb, read_all_country_symbols):
    if tase_mode:
        symbol = Ticker(symb) if yq_mode else yf.Ticker(symb)
    else:
        if read_all_country_symbols not in [sss_config.ALL_COUNTRY_SYMBOLS_SIX, 
                                             sss_config.ALL_COUNTRY_SYMBOLS_ST]:
            # Handle special characters in symbols
            symbol = Ticker(symb.replace('.U', '-UN').replace('.W', '-WT').replace('.', '-')) \
                     if yq_mode else \
                     yf.Ticker(symb.replace('.U', '-UN').replace('.W', '-WT').replace('.', '-'))
        else:
            symbol = Ticker(symb) if yq_mode else yf.Ticker(symb)
    return symbol
```

**Key Pattern**: Based on `yq_mode`, returns either `yahooquery.Ticker` or `yfinance.Ticker` object.

---

## Error Handling (Line 1911)

```python
try:
    # ... all data fetching code ...
except Exception as e:
    if not research_mode: 
        print("Exception in {} symbol.get_info(): {} -> {}".format(
            stock_data.symbol, e, traceback.format_exc()
        ))
    pass
```

**IMPORTANT FINDINGS**:
- ❌ **NO retry logic**
- ❌ **NO rate limiting / sleep delays**
- ❌ **NO exponential backoff**
- ✅ **Simple try/except with print and pass**
- ✅ **Dual library approach provides redundancy**

---

## Key Differences from Our Implementation

### 1. **yfinance Method Calls**
| SSS Scanner | Our Implementation |
|-------------|-------------------|
| `symbol.get_info()` | `stock.info` (property) |
| `symbol.get_cashflow()` | Not used |
| `symbol.get_balance_sheet()` | Not used |
| `symbol.get_earnings()` | Not used |
| ❌ No `.history()` | ✅ `ticker.history()` |

### 2. **Blocking Avoidance Strategy**
| SSS Scanner | Our Implementation |
|-------------|-------------------|
| Dual library (yfinance + yahooquery) | Single library (yfinance only) |
| No rate limiting | Added delays between requests |
| No retry logic | No retry logic |
| Fallback to different API | No fallback |

### 3. **Data Requirements**
| SSS Scanner | Our Implementation |
|-------------|-------------------|
| Fundamental analysis (balance sheets, cash flow, earnings) | Technical analysis (OHLCV data) |
| Needs `.get_info()`, `.get_cashflow()`, etc. | Only needs `.history()` |
| Uses metadata extensively | Avoids metadata |

---

## Why SSS Scanner Might Avoid Blocking

### Theory 1: yahooquery Uses Different Endpoints
**yahooquery** may use Yahoo's official API endpoints rather than scraping HTML, which would:
- Bypass HTML scraping detection (Layer 2)
- Use different authentication mechanisms
- Have different rate limit buckets

### Theory 2: `.get_*()` Methods vs Properties
The yfinance `.get_*()` methods might:
- Use different HTTP endpoints than `.info` property
- Have different caching behavior
- Trigger different Yahoo Finance monitoring systems

### Theory 3: Fundamental Data Less Frequently Requested
- Balance sheets, cash flows update quarterly
- Less real-time demand = less aggressive rate limiting
- Our technical screening hits real-time price data repeatedly

---

## Recommendations for Our Implementation

### ✅ **Already Implemented Correctly**
1. **Using `.history()` only** - This is the RIGHT approach for technical screening
2. **Avoiding `.info` property** - Correct to bypass HTML scraping

### 🔄 **Consider Adding**

#### 1. **yahooquery as Fallback** (HIGHEST PRIORITY)
```python
try:
    # Try yfinance first
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='1mo')
except Exception as e:
    # Fall back to yahooquery
    from yahooquery import Ticker
    ticker = Ticker(symbol)
    hist = ticker.history(period='1mo')
```

#### 2. **Alpha Vantage Integration** (ALREADY PROVIDED IN CRUMB FIX)
```python
import alpha_vantage
# Use Alpha Vantage when Yahoo blocks
```

#### 3. **Request Spacing** (ALREADY PARTIALLY IMPLEMENTED)
```python
import time
time.sleep(random.uniform(1.0, 3.0))  # Random delays between stocks
```

---

## Comparison: yfinance Version Differences

### yfinance 0.1.96 (Old - What SSS might use)
- No crumb authentication system
- Simpler HTTP requests
- Less likely to trigger blocking

### yfinance 0.2.x (Current - What we're using)
- **Crumb authentication** via `/v1/test/getcrumb`
- More complex request patterns
- curl_cffi for browser impersonation
- **More aggressive blocking detection by Yahoo**

---

## Critical Insight: Why `.history()` Gets Blocked But `.get_info()` Might Not

### Different Backend Endpoints

| Method | Likely Endpoint | Data Format | Blocking Risk |
|--------|----------------|-------------|---------------|
| `.info` | HTML scraping | HTML/CSS parsing | **HIGH** |
| `.get_info()` | JSON API | Structured JSON | **MEDIUM** |
| `.history()` | JSON API (query1.finance) | Time series JSON | **MEDIUM** |
| `yahooquery` | Official API | JSON modules | **LOW** |

### Our Current Issue
**User's error**: `/v1/test/getcrumb` authentication failures
- **Root cause**: yfinance 0.2.x requires authentication BEFORE any data requests
- **Why now**: Yahoo tightened authentication requirements
- **Why SSS might work**: They may be using older yfinance or yahooquery exclusively

---

## Actionable Next Steps

### 🔴 **Immediate (User Must Do)**
```cmd
# Clear cache to reset authentication
FIX_YFINANCE_CRUMB.bat

# OR downgrade to old yfinance version
pip uninstall yfinance -y
pip install yfinance==0.1.96
```

### 🟡 **Short Term (If Crumb Fix Fails)**
Add yahooquery as fallback in `stock_scanner.py`:
```python
def fetch_data_with_fallback(symbol):
    try:
        # Primary: yfinance
        ticker = yf.Ticker(symbol)
        return ticker.history(period='1mo')
    except Exception as e:
        # Fallback: yahooquery
        from yahooquery import Ticker
        ticker = Ticker(symbol)
        return ticker.history(period='1mo')
```

### 🟢 **Long Term (Future Enhancement)**
Implement multi-source data fetching:
1. **yfinance** (primary)
2. **yahooquery** (fallback 1)
3. **Alpha Vantage** (fallback 2)
4. **Local cache** (offline mode)

---

## Summary: What SSS Does Differently

| Feature | SSS Scanner | Our Implementation |
|---------|-------------|-------------------|
| **Library Strategy** | Dual (yfinance + yahooquery) | Single (yfinance) |
| **yfinance Methods** | `.get_info()`, `.get_cashflow()` | `.history()` only |
| **Data Focus** | Fundamental (quarterly data) | Technical (real-time OHLCV) |
| **Retry Logic** | None | None |
| **Rate Limiting** | None | Basic delays |
| **Error Handling** | Try/except/pass | Try/except/pass |
| **Fallback Strategy** | Switch to yahooquery mode | None (should add) |

---

## Key Takeaway

**SSS Scanner's secret weapon is NOT superior error handling or rate limiting.**

**It's the DUAL LIBRARY STRATEGY:**
- When yfinance gets blocked → switch to yahooquery
- Different libraries use different Yahoo Finance endpoints
- Provides built-in redundancy without complex retry logic

**For our technical screener**, the best approach is:
1. ✅ Keep `.history()` only (correct for OHLCV data)
2. ✅ Fix crumb authentication (clear cache or downgrade)
3. 🔄 ADD yahooquery as fallback option
4. 🔄 ADD Alpha Vantage for critical cases

---

## Testing yahooquery as Fallback

```python
# Test if yahooquery works when yfinance is blocked
from yahooquery import Ticker

ticker = Ticker("AAPL")
hist = ticker.history(period="1mo")
print(hist)
```

If this works while yfinance fails, we have our solution.

---

**Analysis Date**: 2025-11-10  
**Analysis By**: Claude (AI Assistant)  
**Repository Analyzed**: https://github.com/asafravid/sss  
**Files Examined**: `sss.py` (primary), `sss_run.py`, `sss_config.py`
