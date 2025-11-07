#!/usr/bin/env python3
"""
Comprehensive Diagnostic Tool for Stock Analysis with Sentiment
Run this to identify and fix installation issues
"""

import sys
import os
import platform
from datetime import datetime

print("=" * 70)
print("STOCK ANALYSIS WITH SENTIMENT - FULL DIAGNOSTIC")
print("=" * 70)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Python Path: {sys.executable}")
print("=" * 70)
print()

# Track results
results = {
    'core': {},
    'optional': {},
    'features': {}
}

print("CHECKING CORE DEPENDENCIES")
print("-" * 40)

# Core dependencies
core_packages = [
    ('flask', 'Flask', None),
    ('flask_cors', 'Flask-CORS', 'CORS'),
    ('yfinance', 'yfinance', 'Ticker'),
    ('pandas', 'pandas', 'DataFrame'),
    ('numpy', 'numpy', 'array'),
    ('requests', 'requests', 'get')
]

for module_name, display_name, test_attr in core_packages:
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        
        # Test specific functionality if provided
        if test_attr:
            test_obj = getattr(module, test_attr, None)
            if test_obj is None:
                raise AttributeError(f"Cannot access {test_attr}")
        
        print(f"✓ {display_name:<15} {version:<15} OK")
        results['core'][module_name] = True
    except ImportError as e:
        print(f"✗ {display_name:<15} NOT INSTALLED   {str(e)}")
        results['core'][module_name] = False
    except Exception as e:
        print(f"⚠ {display_name:<15} ERROR           {str(e)}")
        results['core'][module_name] = False

print()
print("CHECKING ML DEPENDENCIES")
print("-" * 40)

# ML dependencies
ml_packages = [
    ('sklearn', 'scikit-learn', 'sklearn'),
    ('sklearn.ensemble', 'RandomForest', 'RandomForestRegressor'),
    ('sklearn.preprocessing', 'Preprocessing', 'StandardScaler'),
    ('sklearn.model_selection', 'Model Selection', 'train_test_split')
]

sklearn_available = False
for module_name, display_name, test_class in ml_packages:
    try:
        if module_name == 'sklearn':
            import sklearn
            version = sklearn.__version__
            print(f"✓ {display_name:<20} {version:<15} OK")
            sklearn_available = True
        else:
            # For submodules
            parts = module_name.split('.')
            if len(parts) == 2:
                parent = __import__(parts[0])
                module = getattr(parent, parts[1])
                test_obj = getattr(module, test_class)
                print(f"✓ {display_name:<20} Available")
        results['optional'][module_name] = True
    except ImportError:
        print(f"✗ {display_name:<20} NOT AVAILABLE")
        results['optional'][module_name] = False
    except Exception as e:
        print(f"⚠ {display_name:<20} ERROR: {str(e)}")
        results['optional'][module_name] = False

print()
print("TESTING YAHOO FINANCE CONNECTION")
print("-" * 40)

try:
    import yfinance as yf
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="1d")
    if not hist.empty:
        price = hist['Close'].iloc[-1]
        print(f"✓ Yahoo Finance working - AAPL: ${price:.2f}")
        results['features']['yahoo_finance'] = True
    else:
        print("✗ Yahoo Finance returned empty data")
        results['features']['yahoo_finance'] = False
except Exception as e:
    print(f"✗ Yahoo Finance error: {e}")
    results['features']['yahoo_finance'] = False

print()
print("TESTING MARKET SENTIMENT INDICATORS")
print("-" * 40)

# Test each sentiment indicator
indicators = {
    '^VIX': 'VIX Fear Index',
    '^GSPC': 'S&P 500',
    '^TNX': '10Y Treasury Yield',
    'DX-Y.NYB': 'Dollar Index',
    'XLK': 'Technology Sector ETF'
}

for symbol, name in indicators.items():
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            value = hist['Close'].iloc[-1]
            print(f"✓ {name:<25} {value:.2f}")
            results['features'][symbol] = True
        else:
            print(f"✗ {name:<25} No data")
            results['features'][symbol] = False
    except Exception as e:
        print(f"✗ {name:<25} Error: {str(e)[:30]}")
        results['features'][symbol] = False

print()
print("TESTING APPLICATION COMPONENTS")
print("-" * 40)

# Test if we can import and use the app components
try:
    # Try to import from the enhanced version
    print("Testing enhanced sentiment app components...")
    
    # Check if the file exists
    if os.path.exists('app_enhanced_sentiment_fixed.py'):
        print("✓ app_enhanced_sentiment_fixed.py found")
        
        # Try to import key components
        try:
            exec("""
import sys
sys.path.insert(0, '.')
from app_enhanced_sentiment_fixed import MarketSentimentAnalyzer, UnifiedDataFetcher, TechnicalAnalyzer
print('✓ MarketSentimentAnalyzer imported')
print('✓ UnifiedDataFetcher imported')
print('✓ TechnicalAnalyzer imported')

# Test instantiation
analyzer = MarketSentimentAnalyzer()
print('✓ MarketSentimentAnalyzer instantiated')

# Test a simple call
vix = analyzer.get_vix_fear_gauge()
if vix and 'value' in vix:
    print(f'✓ VIX test successful: {vix["value"]:.2f if vix["value"] else "N/A"}')
""")
            results['features']['app_components'] = True
        except Exception as e:
            print(f"⚠ Import error: {str(e)[:100]}")
            results['features']['app_components'] = False
    else:
        print("✗ app_enhanced_sentiment_fixed.py not found")
        results['features']['app_components'] = False
        
    # Also check for the no-sklearn version
    if os.path.exists('app_sentiment_no_sklearn.py'):
        print("✓ app_sentiment_no_sklearn.py found (fallback available)")
    
except Exception as e:
    print(f"✗ Component test failed: {e}")
    results['features']['app_components'] = False

print()
print("=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

# Calculate scores
core_ok = sum(1 for v in results['core'].values() if v)
core_total = len(results['core'])
ml_ok = sum(1 for v in results['optional'].values() if v)
ml_total = len(results['optional'])
features_ok = sum(1 for v in results['features'].values() if v)
features_total = len(results['features'])

print(f"Core Dependencies:    {core_ok}/{core_total} working")
print(f"ML Dependencies:      {ml_ok}/{ml_total} working")
print(f"Features Tested:      {features_ok}/{features_total} working")
print()

# Recommendations
print("RECOMMENDATIONS")
print("-" * 40)

if core_ok < core_total:
    print("⚠ CORE DEPENDENCIES MISSING")
    print("  Run: pip install flask flask-cors yfinance pandas numpy requests")
    print()

if ml_ok < ml_total:
    print("⚠ SCIKIT-LEARN NOT AVAILABLE")
    print("  Options:")
    print("  1. Install with pre-compiled wheels:")
    print("     pip install scikit-learn --only-binary :all:")
    print("  2. Use Anaconda/Miniconda:")
    print("     conda install scikit-learn")
    print("  3. Install Visual C++ Build Tools:")
    print("     https://visualstudio.microsoft.com/downloads/")
    print("  4. Use the no-sklearn version:")
    print("     python app_sentiment_no_sklearn.py")
    print()
else:
    print("✓ All ML dependencies available!")
    print("  You can use the full version: app_enhanced_sentiment_fixed.py")
    print()

if not results['features'].get('yahoo_finance'):
    print("⚠ YAHOO FINANCE CONNECTION ISSUES")
    print("  - Check internet connection")
    print("  - May be rate limited, wait a few minutes")
    print()

print("=" * 70)
print("WHICH VERSION TO USE?")
print("=" * 70)

if sklearn_available and ml_ok == ml_total:
    print("✓ USE FULL VERSION (with ML predictions)")
    print("  File: app_enhanced_sentiment_fixed.py")
    print("  Run:  python app_enhanced_sentiment_fixed.py")
    print("  Features: Full ML predictions with RandomForest")
else:
    print("✓ USE NO-SKLEARN VERSION (simplified predictions)")
    print("  File: app_sentiment_no_sklearn.py")
    print("  Run:  python app_sentiment_no_sklearn.py")
    print("  Features: Trend-based predictions, all sentiment features work")

print()
print("=" * 70)
print("Diagnostic complete!")
print("=" * 70)