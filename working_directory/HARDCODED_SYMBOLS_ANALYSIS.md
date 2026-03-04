# 🔍 HARDCODED SYMBOLS ANALYSIS & REMOVAL PLAN

**Date**: December 25, 2024  
**Version**: 1.2.4  
**Status**: ANALYSIS COMPLETE - FIXING IN PROGRESS

---

## 📊 CURRENT HARDCODED SYMBOLS FOUND

### ✅ **Command-Line Defaults (Acceptable - User Configurable)**

These are CLI argument defaults that users can override:

| File | Line | Default Symbols | Override Method |
|------|------|-----------------|-----------------|
| `enhanced_unified_platform.py` | 281 | `AAPL,GOOGL,MSFT,NVDA` | `--symbols TSLA,AMZN` |
| `phase3_intraday_deployment/paper_trading_coordinator.py` | 1271 | `AAPL,GOOGL,MSFT` | `--symbols CBA.AX` |

**Assessment**: ✅ **ACCEPTABLE** - These are proper default values with clear override mechanisms.

---

### ⚠️ **Demo/Test Code (Should Be Configurable)**

These are embedded in demo functions and tests:

| File | Line | Hardcoded Symbols | Purpose | Issue |
|------|------|-------------------|---------|-------|
| `ml_pipeline/prediction_engine.py` | 794 | `["AAPL", "GOOGL", "MSFT"]` | Demo function | Demo only, not production |
| `unified_trading_platform.py` | 661 | `['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX']` | Simulation | Used in find_opportunity() |
| `test_integration.py` | 66 | `['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'TSLA']` | Test suite | Test data |
| `test_backtest.py` | 411 | `['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']` | Backtest test | Test data |

**Assessment**: ⚠️ **NEEDS FIXING** - Should use configurable symbols from CLI args or config files.

---

## 🔧 RECOMMENDED FIXES

### **Priority 1: Production Code** 

#### Fix #1: `unified_trading_platform.py` - Line 661
**Current Code:**
```python
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX']
```

**Fixed Code:**
```python
# Use symbols from engine configuration instead of hardcoded list
symbols = self.engine.watchlist if hasattr(self.engine, 'watchlist') and self.engine.watchlist else self.symbols
```

---

#### Fix #2: `ml_pipeline/prediction_engine.py` - Line 794
**Current Code:**
```python
symbols = ["AAPL", "GOOGL", "MSFT"]
```

**Fixed Code:**
```python
# Accept symbols as argument or use environment variable
import os
default_symbols = os.getenv('DEMO_SYMBOLS', 'AAPL,GOOGL,MSFT')
symbols = default_symbols.split(',')
```

---

### **Priority 2: Test Code**

#### Fix #3: `test_integration.py` - Line 66
**Current Code:**
```python
self.test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'TSLA']
```

**Fixed Code:**
```python
# Allow test symbols via environment variable
import os
test_symbols_env = os.getenv('TEST_SYMBOLS', 'AAPL,GOOGL,MSFT,NVDA,TSLA')
self.test_symbols = test_symbols_env.split(',')
```

---

#### Fix #4: `test_backtest.py` - Line 411
**Current Code:**
```python
symbols = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']
```

**Fixed Code:**
```python
# Parse from command line or environment
import os
import sys
symbols_arg = next((arg.split('=')[1] for arg in sys.argv if arg.startswith('--symbols=')), None)
symbols_env = os.getenv('BACKTEST_SYMBOLS', 'AAPL,GOOGL,MSFT,NVDA,AMD')
symbols = (symbols_arg or symbols_env).split(',')
```

---

## 📝 IMPLEMENTATION PLAN

### Step 1: Create Symbol Configuration Module
Create `symbol_config.py`:
```python
"""
Centralized symbol configuration for the trading platform
"""
import os
from typing import List

class SymbolConfig:
    """Manages symbol configuration across the platform"""
    
    @staticmethod
    def get_default_symbols() -> List[str]:
        """Get default trading symbols from environment or hardcoded defaults"""
        env_symbols = os.getenv('DEFAULT_SYMBOLS', 'AAPL,GOOGL,MSFT,NVDA')
        return [s.strip().upper() for s in env_symbols.split(',')]
    
    @staticmethod
    def get_test_symbols() -> List[str]:
        """Get test symbols from environment or defaults"""
        env_symbols = os.getenv('TEST_SYMBOLS', 'AAPL,GOOGL,MSFT,NVDA,TSLA')
        return [s.strip().upper() for s in env_symbols.split(',')]
    
    @staticmethod
    def get_backtest_symbols() -> List[str]:
        """Get backtest symbols from environment or defaults"""
        env_symbols = os.getenv('BACKTEST_SYMBOLS', 'AAPL,GOOGL,MSFT,NVDA,AMD')
        return [s.strip().upper() for s in env_symbols.split(',')]
```

### Step 2: Update All Files
- Replace hardcoded lists with `SymbolConfig.get_*()` calls
- Add environment variable documentation
- Update all docstrings

### Step 3: Update Documentation
- Add to `WINDOWS_INSTALLATION_GUIDE.md`
- Add to `README_V1.2_DEPLOYMENT.md`
- Create `.env.example` file

---

## 🎯 USAGE AFTER FIX

### Set Custom Symbols via Environment Variables:
```bash
# Windows PowerShell
$env:DEFAULT_SYMBOLS="CBA.AX,BHP.AX,RIO.AX"
$env:TEST_SYMBOLS="CBA.AX,NAB.AX"
$env:BACKTEST_SYMBOLS="CBA.AX,ANZ.AX,WBC.AX"

# Windows CMD
set DEFAULT_SYMBOLS=CBA.AX,BHP.AX,RIO.AX
set TEST_SYMBOLS=CBA.AX,NAB.AX
set BACKTEST_SYMBOLS=CBA.AX,ANZ.AX,WBC.AX

# Linux/Mac
export DEFAULT_SYMBOLS="CBA.AX,BHP.AX,RIO.AX"
export TEST_SYMBOLS="CBA.AX,NAB.AX"
export BACKTEST_SYMBOLS="CBA.AX,ANZ.AX,WBC.AX"
```

### Create .env File:
```bash
# .env
DEFAULT_SYMBOLS=CBA.AX,BHP.AX,RIO.AX
TEST_SYMBOLS=CBA.AX,NAB.AX
BACKTEST_SYMBOLS=CBA.AX,ANZ.AX,WBC.AX
```

### Or Use Command-Line Args (Already Supported):
```bash
python enhanced_unified_platform.py --symbols CBA.AX,BHP.AX
python phase3_intraday_deployment/paper_trading_coordinator.py --symbols CBA.AX
```

---

## ✅ SUMMARY

| Category | Count | Status | Action |
|----------|-------|--------|--------|
| CLI Defaults | 2 | ✅ OK | Already configurable |
| Production Code | 2 | ⚠️ FIX | Replace with SymbolConfig |
| Test Code | 2 | ⚠️ FIX | Replace with SymbolConfig |
| **Total** | **6** | **4 Need Fixing** | **Implement fixes** |

---

## 🚀 NEXT STEPS

1. ✅ Create `symbol_config.py` module
2. ⏳ Update `unified_trading_platform.py`
3. ⏳ Update `ml_pipeline/prediction_engine.py`
4. ⏳ Update `test_integration.py`
5. ⏳ Update `test_backtest.py`
6. ⏳ Create `.env.example`
7. ⏳ Update documentation
8. ⏳ Test with CBA.AX symbols
9. ⏳ Package V1.2.4

**Status**: Ready to implement fixes  
**ETA**: 15 minutes
