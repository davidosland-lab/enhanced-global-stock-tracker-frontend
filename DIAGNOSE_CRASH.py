"""
DIAGNOSE_CRASH.py - Event Risk Guard v1.3.20 Pipeline Crash Diagnostics

This script performs a series of tests to identify the cause of pipeline crashes
that occur after PHASE 2.5 (Market Regime Engine).

Tests performed:
1. hmmlearn Package - checks if hmmlearn is installed
2. Regime Detector Import - tests importing regime_detector.py
3. Market Regime Engine Import - tests importing market_regime_engine.py
4. Market Regime Engine Init - tests MarketRegimeEngine() initialization
5. Market Data Fetch - tests yfinance.download('^AXJO')
6. Regime Analysis - tests engine.analyse()
7. Event Risk Guard Init - tests EventRiskGuard() initialization
8. Event Risk Batch Assessment - tests assess_batch(['CBA.AX'])
"""

import sys
import os
from pathlib import Path

# Add models directory to path
models_path = Path(__file__).parent / 'models'
sys.path.insert(0, str(models_path))

print("=" * 80)
print("EVENT RISK GUARD v1.3.20 - CRASH DIAGNOSTICS")
print("=" * 80)
print()

# Test 1: hmmlearn Package
print("TEST 1: Checking hmmlearn package...")
try:
    import hmmlearn
    print(f"✓ hmmlearn installed: version {hmmlearn.__version__}")
except ImportError as e:
    print(f"✗ hmmlearn NOT installed: {e}")
    print("  Install with: pip install hmmlearn>=0.3.0")
except Exception as e:
    print(f"✗ hmmlearn error: {e}")
print()

# Test 2: Regime Detector Import
print("TEST 2: Importing regime_detector...")
try:
    from screening import regime_detector
    print("✓ regime_detector imported successfully")
except ImportError as e:
    print(f"✗ regime_detector import failed: {e}")
except Exception as e:
    print(f"✗ regime_detector error: {e}")
print()

# Test 3: Market Regime Engine Import
print("TEST 3: Importing market_regime_engine...")
try:
    from screening.market_regime_engine import MarketRegimeEngine
    print("✓ MarketRegimeEngine imported successfully")
except ImportError as e:
    print(f"✗ MarketRegimeEngine import failed: {e}")
except Exception as e:
    print(f"✗ MarketRegimeEngine error: {e}")
print()

# Test 4: Market Regime Engine Initialization
print("TEST 4: Initializing MarketRegimeEngine...")
regime_engine = None
try:
    from screening.market_regime_engine import MarketRegimeEngine
    regime_engine = MarketRegimeEngine()
    print("✓ MarketRegimeEngine initialized successfully")
except ImportError as e:
    print(f"✗ MarketRegimeEngine initialization failed (import): {e}")
except Exception as e:
    print(f"✗ MarketRegimeEngine initialization failed: {e}")
print()

# Test 5: Market Data Fetch
print("TEST 5: Fetching market data (^AXJO)...")
try:
    import yfinance as yf
    data = yf.download('^AXJO', period='60d', progress=False)
    print(f"✓ Market data fetched: {len(data)} rows")
except Exception as e:
    print(f"✗ Market data fetch failed: {e}")
print()

# Test 6: Regime Analysis
print("TEST 6: Running regime analysis...")
if regime_engine:
    try:
        result = regime_engine.analyse()
        print(f"✓ Regime analysis successful")
        print(f"  Regime: {result.get('regime_label', 'UNKNOWN')}")
        print(f"  Crash Risk: {result.get('crash_risk_score', 0.0):.3f}")
    except Exception as e:
        print(f"✗ Regime analysis failed: {e}")
else:
    print("✗ Skipped (MarketRegimeEngine not initialized)")
print()

# Test 7: Event Risk Guard Initialization
print("TEST 7: Initializing EventRiskGuard...")
event_risk_guard = None
try:
    from screening.event_risk_guard import EventRiskGuard
    event_risk_guard = EventRiskGuard()
    print("✓ EventRiskGuard initialized successfully")
    
    # Check if regime engine is available
    if hasattr(event_risk_guard, 'regime_available'):
        print(f"  Regime engine available: {event_risk_guard.regime_available}")
    
except ImportError as e:
    print(f"✗ EventRiskGuard initialization failed (import): {e}")
except Exception as e:
    print(f"✗ EventRiskGuard initialization failed: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 8: Event Risk Batch Assessment
print("TEST 8: Running batch event risk assessment...")
if event_risk_guard:
    try:
        test_stocks = ['CBA.AX']  # assess_batch expects list of ticker strings
        result = event_risk_guard.assess_batch(test_stocks)
        print(f"✓ Batch assessment successful")
        print(f"  Market Regime: {result.get('market_regime', 'UNKNOWN')}")
        print(f"  Crash Risk Score: {result.get('crash_risk_score', 0.0):.3f}")
    except Exception as e:
        print(f"✗ Batch assessment failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ Skipped (EventRiskGuard not initialized)")
print()

# Summary
print("=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)
print()
print("If all tests passed, the pipeline should run without crashes.")
print("If any tests failed, review the errors above to identify the issue.")
print()
print("Next steps:")
print("1. If hmmlearn is missing: pip install hmmlearn>=0.3.0")
print("2. If imports fail: check file paths and Python path")
print("3. If initialization fails: review error messages and tracebacks")
print("4. If tests pass but pipeline crashes: run RUN_PIPELINE_TEST_DEBUG.bat")
print()
