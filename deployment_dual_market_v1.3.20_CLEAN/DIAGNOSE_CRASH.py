"""
Diagnostic Script to Identify Pipeline Crash
=============================================

This script tests each component that could cause a crash during pipeline execution.
Run this BEFORE running the full pipeline to identify the issue.

Usage:
    python DIAGNOSE_CRASH.py
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def test_hmmlearn():
    """Test if hmmlearn is installed"""
    print_header("TEST 1: hmmlearn Package")
    try:
        import hmmlearn
        print(f"✓ hmmlearn installed: version {hmmlearn.__version__}")
        return True
    except ImportError as e:
        print(f"✗ hmmlearn NOT installed: {e}")
        print(f"  Install with: pip install hmmlearn>=0.3.0")
        return False

def test_regime_detector():
    """Test if regime_detector can be imported"""
    print_header("TEST 2: Regime Detector Import")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from models.screening.regime_detector import RegimeDetector
        print(f"✓ RegimeDetector imported successfully")
        print(f"  Module: {RegimeDetector.__module__}")
        return True
    except Exception as e:
        print(f"✗ RegimeDetector import failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_market_regime_engine():
    """Test if MarketRegimeEngine can be imported"""
    print_header("TEST 3: Market Regime Engine Import")
    try:
        from models.screening.market_regime_engine import MarketRegimeEngine
        print(f"✓ MarketRegimeEngine imported successfully")
        return True
    except Exception as e:
        print(f"✗ MarketRegimeEngine import failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_market_regime_init():
    """Test if MarketRegimeEngine can be initialized"""
    print_header("TEST 4: Market Regime Engine Initialization")
    try:
        from models.screening.market_regime_engine import MarketRegimeEngine
        engine = MarketRegimeEngine()
        print(f"✓ MarketRegimeEngine initialized successfully")
        print(f"  Config: {engine.config}")
        return True
    except Exception as e:
        print(f"✗ MarketRegimeEngine initialization failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_market_data_fetch():
    """Test if market data can be fetched"""
    print_header("TEST 5: Market Data Fetch (yfinance)")
    try:
        import yfinance as yf
        from datetime import datetime, timedelta
        
        print("Testing yfinance download...")
        end = datetime.now().date()
        start = end - timedelta(days=30)
        
        data = yf.download(
            tickers=["^AXJO"],  # ASX 200 index
            start=start.isoformat(),
            end=end.isoformat(),
            interval="1d",
            auto_adjust=True,
            progress=False
        )
        
        if data.empty:
            print(f"✗ yfinance returned empty data for ^AXJO")
            return False
        else:
            print(f"✓ Market data fetched successfully")
            print(f"  Shape: {data.shape}")
            print(f"  Date range: {data.index[0]} to {data.index[-1]}")
            return True
            
    except Exception as e:
        print(f"✗ Market data fetch failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_regime_analysis():
    """Test if regime analysis can run"""
    print_header("TEST 6: Full Regime Analysis")
    try:
        from models.screening.market_regime_engine import MarketRegimeEngine
        
        print("Creating engine...")
        engine = MarketRegimeEngine()
        
        print("Running analysis...")
        result = engine.analyse()
        
        print(f"✓ Regime analysis completed successfully")
        print(f"  Regime: {result.get('regime_label', 'UNKNOWN')}")
        print(f"  Crash Risk: {result.get('crash_risk_score', 0.0):.3f}")
        print(f"  Volatility: {result.get('vol_annual', 'N/A')}")
        
        if 'error' in result:
            print(f"  ⚠ Analysis returned error: {result['error']}")
        if 'warning' in result:
            print(f"  ⚠ Analysis returned warning: {result['warning']}")
            
        return True
        
    except Exception as e:
        print(f"✗ Regime analysis failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_event_risk_guard():
    """Test if EventRiskGuard can be initialized"""
    print_header("TEST 7: Event Risk Guard Initialization")
    try:
        from models.screening.event_risk_guard import EventRiskGuard
        
        print("Initializing EventRiskGuard...")
        guard = EventRiskGuard()
        
        print(f"✓ EventRiskGuard initialized successfully")
        print(f"  Regime available: {guard.regime_available}")
        print(f"  Regime engine: {type(guard.regime_engine).__name__ if guard.regime_engine else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"✗ EventRiskGuard initialization failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_event_risk_batch():
    """Test if EventRiskGuard.assess_batch works"""
    print_header("TEST 8: Event Risk Batch Assessment")
    try:
        from models.screening.event_risk_guard import EventRiskGuard
        
        print("Initializing EventRiskGuard...")
        guard = EventRiskGuard()
        
        print("Running batch assessment on test ticker...")
        results = guard.assess_batch(['CBA.AX'])
        
        print(f"✓ Batch assessment completed successfully")
        print(f"  Results: {len(results)} ticker(s)")
        
        for ticker, result in results.items():
            print(f"    {ticker}: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Batch assessment failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("\n" + "="*80)
    print("  EVENT RISK GUARD - CRASH DIAGNOSTIC")
    print("="*80)
    print("\nThis script will test each component to identify what's causing the crash.\n")
    
    tests = [
        ("hmmlearn Package", test_hmmlearn),
        ("Regime Detector Import", test_regime_detector),
        ("Market Regime Engine Import", test_market_regime_engine),
        ("Market Regime Engine Init", test_market_regime_init),
        ("Market Data Fetch", test_market_data_fetch),
        ("Regime Analysis", test_regime_analysis),
        ("Event Risk Guard Init", test_event_risk_guard),
        ("Event Risk Batch Assessment", test_event_risk_batch),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{len(results)} tests passed")
    
    if failed > 0:
        print(f"\n⚠ {failed} test(s) failed - pipeline will likely crash")
        print(f"\nRECOMMENDATIONS:")
        
        if not results.get("hmmlearn Package"):
            print(f"  1. Install hmmlearn: pip install hmmlearn>=0.3.0")
        
        if not results.get("Market Data Fetch"):
            print(f"  2. Check internet connection")
            print(f"  3. Try running: pip install --upgrade yfinance")
        
        if not results.get("Regime Analysis") and results.get("Market Data Fetch"):
            print(f"  4. The crash is likely in regime detection logic")
            print(f"     - Check models/screening/regime_detector.py")
            print(f"     - Check models/screening/market_regime_engine.py")
    else:
        print(f"\n✓ All tests passed - pipeline should work!")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
