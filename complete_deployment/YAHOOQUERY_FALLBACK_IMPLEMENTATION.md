# Adding yahooquery Fallback to Stock Scanner

## Overview
Based on analysis of the SSS scanner (https://github.com/asafravid/sss), their key blocking-avoidance strategy is using **yahooquery as a fallback** when yfinance fails.

---

## Installation

```cmd
pip install yahooquery
```

---

## Implementation Plan

### Phase 1: Test yahooquery Compatibility

**Create test script**: `test_yahooquery.py`

```python
#!/usr/bin/env python3
"""Test if yahooquery works as yfinance alternative"""

from yahooquery import Ticker
import pandas as pd

def test_yahooquery():
    """Test basic yahooquery functionality"""
    
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"Testing {symbol} with yahooquery")
        print(f"{'='*60}")
        
        try:
            ticker = Ticker(symbol)
            
            # Get price data
            hist = ticker.history(period='1mo')
            
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                print(f"✅ History data retrieved: {len(hist)} rows")
                print(f"   Columns: {list(hist.columns)}")
                print(f"   Date range: {hist.index[0]} to {hist.index[-1]}")
                print(f"   Latest close: ${hist['close'].iloc[-1]:.2f}")
                print(f"   Avg volume: {hist['volume'].mean():.0f}")
            else:
                print(f"❌ No history data retrieved")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(traceback.format_exc())
    
    print(f"\n{'='*60}")
    print("Test Complete")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_yahooquery()
```

---

### Phase 2: Modify `stock_scanner.py`

#### Location: `models/screening/stock_scanner.py`

#### Change 1: Add Import at Top

```python
import yfinance as yf
from yahooquery import Ticker as YQTicker  # Add this line
import pandas as pd
```

#### Change 2: Create Fallback Function (Add after imports)

```python
def fetch_history_with_fallback(symbol, start_date=None, end_date=None, period='1mo'):
    """
    Fetch stock history with yfinance, fallback to yahooquery if blocked.
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date for history (if using date range)
        end_date: End date for history (if using date range)
        period: Period string like '1mo', '3mo' (if not using dates)
        
    Returns:
        pandas.DataFrame with OHLCV data
        
    Raises:
        Exception if both methods fail
    """
    
    # Try yfinance first (primary method)
    try:
        ticker = yf.Ticker(symbol)
        
        if start_date and end_date:
            hist = ticker.history(start=start_date, end=end_date)
        else:
            hist = ticker.history(period=period)
            
        if not hist.empty:
            return hist, 'yfinance'
            
    except Exception as e:
        print(f"[FALLBACK] yfinance failed for {symbol}: {e}")
    
    # Fallback to yahooquery
    try:
        print(f"[FALLBACK] Trying yahooquery for {symbol}...")
        ticker = YQTicker(symbol)
        
        if start_date and end_date:
            # yahooquery uses different parameter names
            hist = ticker.history(start=start_date, end=end_date)
        else:
            hist = ticker.history(period=period)
        
        if isinstance(hist, pd.DataFrame) and not hist.empty:
            # yahooquery returns lowercase column names, normalize them
            hist.columns = [col.capitalize() for col in hist.columns]
            print(f"[FALLBACK] ✅ yahooquery succeeded for {symbol}")
            return hist, 'yahooquery'
            
    except Exception as e:
        print(f"[FALLBACK] yahooquery also failed for {symbol}: {e}")
    
    # Both methods failed
    raise Exception(f"Both yfinance and yahooquery failed to fetch data for {symbol}")
```

#### Change 3: Update `validate_stock()` Method

**Find (around line 150)**:
```python
def validate_stock(self, symbol: str) -> bool:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1mo')
```

**Replace with**:
```python
def validate_stock(self, symbol: str) -> bool:
    try:
        hist, source = fetch_history_with_fallback(symbol, period='1mo')
        if source == 'yahooquery':
            self.logger.info(f"Using yahooquery fallback for {symbol}")
```

#### Change 4: Update `analyze_stock()` Method

**Find (around line 210)**:
```python
def analyze_stock(self, symbol: str, start_date: str, end_date: str) -> Optional[Dict]:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
```

**Replace with**:
```python
def analyze_stock(self, symbol: str, start_date: str, end_date: str) -> Optional[Dict]:
    try:
        hist, source = fetch_history_with_fallback(
            symbol, 
            start_date=start_date, 
            end_date=end_date
        )
        
        if source == 'yahooquery':
            self.logger.info(f"Using yahooquery fallback for {symbol}")
```

---

### Phase 3: Update Other Files

#### `models/screening/spi_monitor.py` (Line 157)

**Find**:
```python
df = yf.Ticker(symbol).history(period="6mo", interval="1d")
```

**Replace with**:
```python
df, source = fetch_history_with_fallback(symbol, period="6mo")
if source == 'yahooquery':
    logger.info(f"Using yahooquery fallback for {symbol}")
```

**Note**: You'll need to import the fallback function:
```python
from models.screening.stock_scanner import fetch_history_with_fallback
```

---

### Phase 4: Configuration Flag (Optional)

#### Add to `config.yaml` or `settings.py`

```python
# Data Source Configuration
DATA_SOURCE_PRIMARY = 'yfinance'      # Primary data source
DATA_SOURCE_FALLBACK = 'yahooquery'   # Fallback when primary fails
ENABLE_FALLBACK = True                # Enable/disable fallback
```

#### Enhanced Fallback Function with Config

```python
def fetch_history_with_fallback(symbol, start_date=None, end_date=None, period='1mo'):
    """Fetch with configurable fallback"""
    
    from config import ENABLE_FALLBACK, DATA_SOURCE_PRIMARY, DATA_SOURCE_FALLBACK
    
    sources = [DATA_SOURCE_PRIMARY]
    if ENABLE_FALLBACK:
        sources.append(DATA_SOURCE_FALLBACK)
    
    for source in sources:
        try:
            if source == 'yfinance':
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date) if start_date else ticker.history(period=period)
            elif source == 'yahooquery':
                ticker = YQTicker(symbol)
                hist = ticker.history(start=start_date, end=end_date) if start_date else ticker.history(period=period)
                # Normalize column names
                hist.columns = [col.capitalize() for col in hist.columns]
            else:
                continue
                
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                return hist, source
                
        except Exception as e:
            print(f"[FALLBACK] {source} failed for {symbol}: {e}")
            continue
    
    raise Exception(f"All data sources failed for {symbol}")
```

---

## Testing Plan

### Test 1: Normal Operation (yfinance works)
```cmd
python test_yahooquery.py
python test_scanner_direct.py
```

Expected: yfinance should be used, yahooquery not called

### Test 2: Simulated yfinance Failure
Create `test_fallback_simulation.py`:
```python
# Temporarily break yfinance to test fallback
import sys
import yfinance as yf

# Mock yfinance to always fail
original_ticker = yf.Ticker
def failing_ticker(*args, **kwargs):
    raise Exception("Simulated yfinance failure")
yf.Ticker = failing_ticker

# Now test scanner
from models.screening.stock_scanner import fetch_history_with_fallback

symbol = "AAPL"
hist, source = fetch_history_with_fallback(symbol, period='1mo')
print(f"Source: {source}")
print(f"Data shape: {hist.shape}")
assert source == 'yahooquery', "Should have fallen back to yahooquery"
```

### Test 3: Production Test with Real Blocking
```cmd
# When yfinance is actually blocked by Yahoo
python RUN_STOCK_SCREENER.bat
```

Expected: Scanner should continue working using yahooquery

---

## Deployment Steps

### Step 1: Backup Current Version
```cmd
cd C:\Users\david\AOSS
mkdir backup_before_yahooquery
copy models\screening\stock_scanner.py backup_before_yahooquery\
copy models\screening\spi_monitor.py backup_before_yahooquery\
```

### Step 2: Install yahooquery
```cmd
pip install yahooquery
```

### Step 3: Apply Code Changes
1. Update `stock_scanner.py` with fallback function
2. Update `validate_stock()` method
3. Update `analyze_stock()` method
4. Update `spi_monitor.py` if needed

### Step 4: Test
```cmd
python test_yahooquery.py
python test_scanner_direct.py
```

### Step 5: Deploy
```cmd
python RUN_STOCK_SCREENER.bat
```

---

## Monitoring and Logging

### Add Logging to Track Data Source Usage

```python
import logging

class DataSourceMonitor:
    def __init__(self):
        self.stats = {
            'yfinance_success': 0,
            'yfinance_failure': 0,
            'yahooquery_success': 0,
            'yahooquery_failure': 0,
            'total_attempts': 0
        }
    
    def record_success(self, source):
        self.stats[f'{source}_success'] += 1
        self.stats['total_attempts'] += 1
    
    def record_failure(self, source):
        self.stats[f'{source}_failure'] += 1
    
    def print_stats(self):
        print("\n" + "="*60)
        print("DATA SOURCE STATISTICS")
        print("="*60)
        for key, value in self.stats.items():
            print(f"{key:25s}: {value:5d}")
        
        yf_total = self.stats['yfinance_success'] + self.stats['yfinance_failure']
        yq_total = self.stats['yahooquery_success'] + self.stats['yahooquery_failure']
        
        if yf_total > 0:
            yf_rate = (self.stats['yfinance_success'] / yf_total) * 100
            print(f"\nyfinance success rate: {yf_rate:.1f}%")
        
        if yq_total > 0:
            yq_rate = (self.stats['yahooquery_success'] / yq_total) * 100
            print(f"yahooquery success rate: {yq_rate:.1f}%")
        
        print("="*60)

# Global monitor instance
data_source_monitor = DataSourceMonitor()
```

---

## Comparison: Before vs After

### BEFORE (Current Implementation)
```
yfinance fails → Scanner stops → Manual intervention required
```

### AFTER (With yahooquery Fallback)
```
yfinance fails → yahooquery tries → Scanner continues → Success
```

---

## Cost-Benefit Analysis

### Benefits
✅ **Automatic failover** when yfinance is blocked  
✅ **No manual intervention** required  
✅ **Same data quality** (both use Yahoo Finance backend)  
✅ **Proven strategy** (used by SSS scanner successfully)  
✅ **Minimal code changes** (mostly in `stock_scanner.py`)  

### Costs
❌ Additional dependency (yahooquery)  
❌ Slightly slower (fallback adds delay)  
❌ More complex debugging (two codepaths)  

### Verdict
**Highly recommended** - The benefits far outweigh the costs.

---

## Alternative: Alpha Vantage Integration

If **both yfinance AND yahooquery fail**, fall back to Alpha Vantage:

```python
def fetch_history_triple_fallback(symbol, start_date=None, end_date=None, period='1mo'):
    """Try yfinance → yahooquery → Alpha Vantage"""
    
    # Try yfinance
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date) if start_date else ticker.history(period=period)
        if not hist.empty:
            return hist, 'yfinance'
    except Exception as e:
        print(f"[FALLBACK] yfinance failed: {e}")
    
    # Try yahooquery
    try:
        ticker = YQTicker(symbol)
        hist = ticker.history(start=start_date, end=end_date) if start_date else ticker.history(period=period)
        if isinstance(hist, pd.DataFrame) and not hist.empty:
            hist.columns = [col.capitalize() for col in hist.columns]
            return hist, 'yahooquery'
    except Exception as e:
        print(f"[FALLBACK] yahooquery failed: {e}")
    
    # Try Alpha Vantage (requires API key)
    try:
        from alpha_vantage.timeseries import TimeSeries
        ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
        hist, _ = ts.get_daily(symbol=symbol, outputsize='full')
        hist.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return hist, 'alphavantage'
    except Exception as e:
        print(f"[FALLBACK] Alpha Vantage failed: {e}")
    
    raise Exception(f"All data sources failed for {symbol}")
```

---

## Next Steps

1. **User Action Required**: Try the crumb fix first
   ```cmd
   cd C:\Users\david\AOSS
   FIX_YFINANCE_CRUMB.bat
   ```

2. **If crumb fix doesn't work**: Implement yahooquery fallback
   - Follow Phase 1-4 above
   - Test thoroughly
   - Deploy

3. **Long-term**: Consider Alpha Vantage as third fallback

---

**Document Created**: 2025-11-10  
**Based On**: SSS Scanner analysis (https://github.com/asafravid/sss)  
**Priority**: HIGH (if crumb fix fails)  
**Effort**: 2-3 hours implementation + testing
