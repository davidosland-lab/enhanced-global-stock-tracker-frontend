#!/usr/bin/env python3
"""
Regime Engine Diagnostic Script
================================
Comprehensive diagnostics for the Market Regime Engine to identify
why it might be returning UNKNOWN regime and none method.

Run this to debug regime engine issues.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print a formatted header"""
    print()
    print("=" * 80)
    print(f" {text}")
    print("=" * 80)
    print()

def print_section(text):
    """Print a section divider"""
    print()
    print("-" * 80)
    print(f" {text}")
    print("-" * 80)

def check_imports():
    """Check if all required packages are available"""
    print_header("STEP 1: Package Availability Check")
    
    packages = {
        'pandas': None,
        'numpy': None,
        'yfinance': None,
        'hmmlearn': '(optional - will use GMM fallback)',
        'arch': '(optional - will use EWMA fallback)',
        'xgboost': '(optional - only needed for meta-model)',
    }
    
    for package, note in packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            status = f"✓ {package}: {version}"
            if note:
                status += f" {note}"
            print(status)
        except ImportError:
            if note:
                print(f"  {package}: NOT INSTALLED {note}")
            else:
                print(f"✗ {package}: NOT INSTALLED - REQUIRED!")
                return False
    
    return True

def check_regime_engine_import():
    """Check if regime engine modules can be imported"""
    print_header("STEP 2: Regime Engine Import Check")
    
    try:
        from models.screening.market_regime_engine import MarketRegimeEngine
        print("✓ MarketRegimeEngine imported successfully")
        return MarketRegimeEngine
    except ImportError as e:
        print(f"✗ Failed to import MarketRegimeEngine: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Ensure you're running from the package root directory")
        print("  2. Check that models/screening/market_regime_engine.py exists")
        print("  3. Verify Python path includes current directory")
        return None

def test_yfinance_single_ticker():
    """Test fetching a single ticker with yfinance"""
    print_header("STEP 3: yfinance Single Ticker Test")
    
    try:
        import yfinance as yf
        
        end = datetime.now().date()
        start = end - timedelta(days=180)
        
        print(f"Fetching ^AXJO from {start} to {end}...")
        data = yf.download('^AXJO', start=start, end=end, progress=False, show_errors=False)
        
        print(f"✓ Received data: {len(data)} rows")
        if len(data) > 0:
            print(f"  Columns: {list(data.columns)}")
            print(f"  Date range: {data.index[0]} to {data.index[-1]}")
            print(f"  Data shape: {data.shape}")
            return True
        else:
            print("✗ Received empty dataframe")
            print()
            print("Possible causes:")
            print("  - Internet connection issue")
            print("  - yfinance rate limiting")
            print("  - Invalid ticker symbol")
            print("  - Yahoo Finance API issue")
            return False
            
    except Exception as e:
        print(f"✗ Fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_yfinance_multiple_tickers():
    """Test fetching multiple tickers and MultiIndex handling"""
    print_header("STEP 4: yfinance Multiple Tickers Test (MultiIndex)")
    
    try:
        import yfinance as yf
        import pandas as pd
        
        end = datetime.now().date()
        start = end - timedelta(days=180)
        
        symbols = ['^AXJO', 'AUDUSD=X']
        print(f"Fetching {symbols} from {start} to {end}...")
        data = yf.download(symbols, start=start, end=end, progress=False, show_errors=False, group_by='ticker')
        
        print(f"✓ Received data: {len(data)} rows")
        print(f"  DataFrame shape: {data.shape}")
        print(f"  Column type: {type(data.columns).__name__}")
        
        if isinstance(data.columns, pd.MultiIndex):
            print(f"  ✓ MultiIndex detected with {data.columns.nlevels} levels")
            print(f"  Level 0 values: {list(data.columns.get_level_values(0).unique())}")
            print(f"  Level 1 values: {list(data.columns.get_level_values(1).unique())}")
            
            # Test extraction
            print()
            print("Testing Close price extraction...")
            level_1_values = data.columns.get_level_values(1).unique()
            
            if 'Close' in level_1_values:
                close = data.xs('Close', level=1, axis=1)
                print(f"  ✓ Extracted Close prices: shape={close.shape}, columns={list(close.columns)}")
                return True, data
            elif 'Adj Close' in level_1_values:
                close = data.xs('Adj Close', level=1, axis=1)
                print(f"  ✓ Extracted Adj Close prices: shape={close.shape}, columns={list(close.columns)}")
                return True, data
            else:
                print(f"  ✗ Cannot find 'Close' or 'Adj Close' in level 1")
                print(f"  Available: {list(level_1_values)}")
                return False, None
        else:
            print("  ⚠ Not a MultiIndex (single ticker?)")
            print(f"  Columns: {list(data.columns)}")
            return True, data
            
    except Exception as e:
        print(f"✗ Fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_regime_engine():
    """Test the complete regime engine"""
    print_header("STEP 5: Complete Regime Engine Test")
    
    try:
        from models.screening.market_regime_engine import MarketRegimeEngine
        
        print("Creating MarketRegimeEngine instance...")
        engine = MarketRegimeEngine()
        print("✓ Instance created")
        print(f"  Config: index={engine.config.index_symbol}, vix={engine.config.vol_symbol}, fx={engine.config.fx_symbol}")
        print(f"  Lookback: {engine.config.lookback_days} days")
        
        print()
        print("Running analysis (this may take 10-30 seconds)...")
        print()
        
        result = engine.analyse()
        
        print_section("ANALYSIS RESULTS")
        print()
        
        # Display all result fields
        for key, value in result.items():
            if key == 'regime_probabilities' and value:
                print(f"  {key}:")
                for state, prob in value.items():
                    print(f"    State {state}: {prob:.3f}")
            elif key == 'data_window' and value:
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
        
        print()
        print_section("INTERPRETATION")
        print()
        
        regime = result.get('regime_label', 'unknown')
        method = result.get('vol_method', 'none')
        
        if regime == 'unknown' and method == 'none':
            print("❌ REGIME ENGINE NOT WORKING")
            print()
            print("The regime engine returned UNKNOWN regime and none method.")
            print()
            
            if result.get('error'):
                print(f"Error message: {result['error']}")
            if result.get('warning'):
                print(f"Warning: {result['warning']}")
            
            print()
            print("Common causes:")
            print("  1. Data fetch failed (check internet connection)")
            print("  2. Insufficient data rows (need 50+ before features, 40+ after)")
            print("  3. Column extraction failed (MultiIndex issue)")
            print("  4. Feature engineering removed too many rows (rolling windows)")
            print()
            print("Check the detailed logs above for specific errors.")
            return False
            
        else:
            print("✅ REGIME ENGINE WORKING!")
            print()
            print(f"  Detected Regime: {regime.upper()}")
            
            if regime == 'calm':
                print("    Meaning: Low volatility, stable market conditions")
            elif regime == 'normal':
                print("    Meaning: Standard market behavior")
            elif regime == 'high_vol':
                print("    Meaning: Elevated volatility, turbulent market")
            
            print()
            print(f"  Volatility Method: {method.upper()}")
            
            if result.get('vol_1d'):
                vol_pct = result['vol_1d'] * 100
                print(f"  Daily Volatility: {vol_pct:.2f}%")
            
            if result.get('vol_annual'):
                vol_annual_pct = result['vol_annual'] * 100
                print(f"  Annual Volatility: {vol_annual_pct:.1f}%")
            
            crash_risk = result.get('crash_risk_score', 0)
            print(f"  Crash Risk Score: {crash_risk:.2f}/1.0", end='')
            
            if crash_risk > 0.6:
                print(" (HIGH RISK ⚠️)")
            elif crash_risk > 0.4:
                print(" (MODERATE RISK ⚡)")
            else:
                print(" (LOW RISK ✓)")
            
            return True
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        print()
        print("Full traceback:")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostics"""
    print()
    print("=" * 80)
    print(" MARKET REGIME ENGINE - COMPREHENSIVE DIAGNOSTICS")
    print("=" * 80)
    print()
    print(f" Script: {__file__}")
    print(f" Working Directory: {os.getcwd()}")
    print(f" Python: {sys.version}")
    print()
    
    # Run diagnostics in order
    results = []
    
    # 1. Check packages
    if not check_imports():
        print()
        print("❌ Missing required packages. Please run: pip install -r requirements.txt")
        return False
    results.append(True)
    
    # 2. Check imports
    engine_class = check_regime_engine_import()
    if engine_class is None:
        print()
        print("❌ Cannot import regime engine modules.")
        return False
    results.append(True)
    
    # 3. Test single ticker
    if not test_yfinance_single_ticker():
        print()
        print("❌ Cannot fetch single ticker data. Check internet connection.")
        return False
    results.append(True)
    
    # 4. Test multiple tickers
    success, data = test_yfinance_multiple_tickers()
    if not success:
        print()
        print("❌ Cannot fetch multiple tickers or extract Close prices.")
        print("   This is the likely cause of UNKNOWN regime.")
        return False
    results.append(True)
    
    # 5. Test complete engine
    if not test_regime_engine():
        print()
        print("❌ Regime engine test failed.")
        return False
    results.append(True)
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    print()
    print("✅ All checks passed!")
    print()
    print("The regime engine should be working correctly.")
    print("If you're still seeing UNKNOWN regime in the pipeline, check:")
    print()
    print("  1. The pipeline is using the same code version")
    print("  2. The file has the latest fix (commit 91783bb)")
    print("  3. Run this diagnostic vs running the pipeline in the same directory")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print()
        print("Diagnostic interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
