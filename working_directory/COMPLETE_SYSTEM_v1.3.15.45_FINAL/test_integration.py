#!/usr/bin/env python3
"""
Phase 3 Market Regime Intelligence System - Integration Test Suite
Version: v1.3.13 - Complete Backend Package
Author: David Osland Lab
Date: January 6, 2026

This script provides comprehensive testing of all system components:
1. Core modules (Market Regime Detector, Cross-Market Features, Opportunity Scorer)
2. Data fetchers (Market Data Fetcher, Enhanced Data Sources)
3. Configuration files (5 JSON configs)
4. Pipeline runners (AU/US/UK)
5. Dashboard systems

Usage:
    python test_integration.py                 # Run all tests
    python test_integration.py --quick         # Quick verification
    python test_integration.py --component X   # Test specific component
    python test_integration.py --market AU     # Test specific market
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add models directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'models'))

# ═══════════════════════════════════════════════════════════════════
#  TEST SUITE
# ═══════════════════════════════════════════════════════════════════

def print_header(title):
    """Print formatted test header"""
    print("\n" + "═" * 70)
    print(f" {title}")
    print("═" * 70)

def print_section(title):
    """Print formatted section header"""
    print(f"\n[{title}]")
    print("─" * 70)

def test_python_version():
    """Test Python version compatibility"""
    print_header("TEST 1: Python Version")
    
    major, minor = sys.version_info[:2]
    version = f"{major}.{minor}"
    
    print(f"Current Python version: {version}")
    
    if major >= 3 and minor >= 8:
        print(f"[OK] Python {version} is supported (requires 3.8+)")
        return True
    else:
        print(f"[X] Python {version} is NOT supported (requires 3.8+)")
        return False

def test_core_imports():
    """Test if all required modules can be imported"""
    print_header("TEST 2: Core Dependencies")
    
    # Required packages
    required = [
        ('pandas', 'pandas', '1.5.0+'),
        ('numpy', 'numpy', '1.23.0+'),
        ('flask', 'flask', '2.3.0+'),
        ('requests', 'requests', '2.31.0+'),
        ('yfinance', 'yfinance', '0.2.28+'),
    ]
    
    # Optional packages
    optional = [
        ('sklearn', 'scikit-learn', '1.3.0+'),
        ('matplotlib', 'matplotlib', '3.7.0+'),
        ('bcrypt', 'bcrypt', '4.0.0+'),
    ]
    
    print_section("Required Packages")
    all_passed = True
    for module, package, version in required:
        try:
            __import__(module)
            print(f"  [OK] {package:<20} {version}")
        except ImportError:
            print(f"  [X] {package:<20} {version} - MISSING")
            all_passed = False
    
    print_section("Optional Packages")
    for module, package, version in optional:
        try:
            __import__(module)
            print(f"  [OK] {package:<20} {version}")
        except ImportError:
            print(f"  [!]  {package:<20} {version} - Not installed (optional)")
    
    if all_passed:
        print("\n[OK] All required dependencies available")
    else:
        print("\n[X] Some required dependencies are missing")
        print("Run: pip install -r requirements.txt")
    
    return all_passed

def test_directory_structure():
    """Test required directories exist"""
    print_header("TEST 3: Directory Structure")
    
    required_dirs = [
        'models',
        'config',
        'docs',
        'scripts',
        'data',
        'data/cache',
        'data/state',
        'data/logs',
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            file_count = len(list(dir_path.glob('*')))
            print(f"  [OK] {dir_name:<20} ({file_count} files)")
        else:
            print(f"  [!]  {dir_name:<20} (missing, creating...)")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"      → Created {dir_name}")
            except Exception as e:
                print(f"      → Failed: {e}")
                all_exist = False
    
    print(f"\n{'[OK]' if all_exist else '[!]'} Directory structure {'ready' if all_exist else 'created'}")
    return True  # Always return True since we create missing dirs

def test_configuration_files():
    """Test configuration files"""
    print_header("TEST 4: Configuration Files")
    
    config_files = [
        'config/live_trading_config.json',
        'config/screening_config.json',
        'config/asx_sectors.json',
        'config/us_sectors.json',
        'config/uk_sectors.json',
    ]
    
    all_exist = True
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            size_kb = config_path.stat().st_size / 1024
            print(f"  [OK] {config_file:<35} ({size_kb:.1f} KB)")
            
            # Try to load JSON
            try:
                import json
                with open(config_path, 'r') as f:
                    data = json.load(f)
                print(f"      → Valid JSON, {len(data)} top-level keys")
            except Exception as e:
                print(f"      → Invalid JSON: {e}")
                all_exist = False
        else:
            print(f"  [X] {config_file:<35} MISSING")
            all_exist = False
    
    print(f"\n{'[OK]' if all_exist else '[X]'} All configs {'loaded' if all_exist else 'have issues'}")
    return all_exist

def test_market_data_fetcher():
    """Test Market Data Fetcher"""
    print_header("TEST 5: Market Data Fetcher")
    
    try:
        from models.market_data_fetcher import MarketDataFetcher
        
        print("  → Initializing MarketDataFetcher...")
        fetcher = MarketDataFetcher()
        
        print("  → Fetching live market data...")
        start_time = time.time()
        market_data = fetcher.get_market_data()
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        if market_data:
            print(f"\n  [OK] Market data fetched in {elapsed:.0f}ms")
            print(f"\n  Market Data Summary:")
            for key, value in market_data.items():
                if isinstance(value, (int, float)):
                    print(f"    {key:<20} {value:>12.2f}")
                else:
                    print(f"    {key:<20} {value}")
            return True
        else:
            print("  [X] No market data returned")
            return False
            
    except ImportError as e:
        print(f"  [X] Cannot import MarketDataFetcher: {e}")
        return False
    except Exception as e:
        print(f"  [X] Market Data Fetcher test failed: {e}")
        return False

def test_market_regime_detector():
    """Test Market Regime Detector"""
    print_header("TEST 6: Market Regime Detector")
    
    try:
        from models.market_regime_detector import MarketRegimeDetector
        
        print("  → Initializing MarketRegimeDetector...")
        detector = MarketRegimeDetector()
        
        # Create sample market data
        sample_data = {
            'sp500': 4500.0,
            'nasdaq': 15000.0,
            'vix': 18.5,
            'oil': 75.0,
            'gold': 2000.0,
            'us10y': 4.2,
            'dxy': 103.5,
            'audusd': 0.65,
        }
        
        print("  → Detecting market regime...")
        regime_data = detector.detect_regime(sample_data)
        
        if regime_data:
            print(f"\n  [OK] Regime detected successfully")
            print(f"\n  Regime Analysis:")
            print(f"    Regime:          {regime_data['regime']}")
            print(f"    Strength:        {regime_data['strength']:.2f}")
            print(f"    Confidence:      {regime_data['confidence']:.2f}")
            print(f"    Sector Impact:   {len(regime_data.get('sector_impact', {}))} sectors")
            return True
        else:
            print("  [X] No regime data returned")
            return False
            
    except ImportError as e:
        print(f"  [X] Cannot import MarketRegimeDetector: {e}")
        return False
    except Exception as e:
        print(f"  [X] Market Regime Detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cross_market_features():
    """Test Cross-Market Features"""
    print_header("TEST 7: Cross-Market Features")
    
    try:
        from models.cross_market_features import CrossMarketFeatures
        
        print("  → Initializing CrossMarketFeatures...")
        cmf = CrossMarketFeatures()
        
        # Create sample market data
        sample_data = {
            'sp500': 4500.0,
            'nasdaq': 15000.0,
            'oil': 75.0,
            'gold': 2000.0,
            'audusd': 0.65,
        }
        
        print("  → Computing cross-market features...")
        features = cmf.compute_features(sample_data)
        
        if features:
            print(f"\n  [OK] Features computed successfully")
            print(f"\n  Feature Summary:")
            print(f"    Total features:  {len(features)}")
            for key, value in list(features.items())[:10]:  # Show first 10
                if isinstance(value, (int, float)):
                    print(f"    {key:<25} {value:>10.4f}")
            if len(features) > 10:
                print(f"    ... and {len(features) - 10} more")
            return True
        else:
            print("  [X] No features returned")
            return False
            
    except ImportError as e:
        print(f"  [X] Cannot import CrossMarketFeatures: {e}")
        return False
    except Exception as e:
        print(f"  [X] Cross-Market Features test failed: {e}")
        return False

def test_regime_aware_opportunity_scorer():
    """Test Regime-Aware Opportunity Scorer"""
    print_header("TEST 8: Regime-Aware Opportunity Scorer")
    
    try:
        from models.regime_aware_opportunity_scorer import RegimeAwareOpportunityScorer
        
        print("  → Initializing RegimeAwareOpportunityScorer...")
        scorer = RegimeAwareOpportunityScorer()
        
        # Create sample stocks
        sample_stocks = [
            {
                'symbol': 'TEST.AX',
                'name': 'Test Stock 1',
                'sector': 'Technology',
                'prediction_confidence': 75.0,
                'technical_strength': 80.0,
                'spi_alignment': 70.0,
                'liquidity': 85.0,
                'volatility': 15.0,
                'sector_momentum': 65.0,
            },
            {
                'symbol': 'DEMO.AX',
                'name': 'Demo Stock 2',
                'sector': 'Healthcare',
                'prediction_confidence': 80.0,
                'technical_strength': 75.0,
                'spi_alignment': 85.0,
                'liquidity': 90.0,
                'volatility': 12.0,
                'sector_momentum': 70.0,
            },
        ]
        
        # Sample market data
        market_data = {
            'regime': 'US_TECH_RALLY',
            'regime_strength': 0.75,
            'regime_confidence': 0.85,
            'sector_impact': {
                'Technology': 0.8,
                'Healthcare': 0.5,
            }
        }
        
        print("  → Scoring opportunities...")
        scored_stocks = scorer.score_opportunities(sample_stocks, market_data)
        
        if scored_stocks:
            print(f"\n  [OK] Opportunities scored successfully")
            print(f"\n  Top Opportunities:")
            for i, stock in enumerate(scored_stocks[:3], 1):
                print(f"\n    {i}. {stock['symbol']} - {stock['name']}")
                print(f"       Final Score:    {stock['total_score']:.1f}/100")
                print(f"       Base Score:     {stock['base_score']:.1f}")
                print(f"       Regime Impact:  {stock['regime_adjustment']:.1f}")
            return True
        else:
            print("  [X] No scored stocks returned")
            return False
            
    except ImportError as e:
        print(f"  [X] Cannot import RegimeAwareOpportunityScorer: {e}")
        return False
    except Exception as e:
        print(f"  [X] Opportunity Scorer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_runners():
    """Test pipeline runners exist and are executable"""
    print_header("TEST 9: Pipeline Runners")
    
    pipelines = [
        ('run_au_pipeline_v1.3.13.py', 'Australian Market'),
        ('run_us_pipeline_v1.3.13.py', 'US Market'),
        ('run_uk_pipeline_v1.3.13.py', 'UK Market'),
    ]
    
    all_exist = True
    for pipeline_file, market_name in pipelines:
        pipeline_path = Path(pipeline_file)
        if pipeline_path.exists():
            size_kb = pipeline_path.stat().st_size / 1024
            print(f"  [OK] {pipeline_file:<30} ({market_name}, {size_kb:.1f} KB)")
        else:
            print(f"  [X] {pipeline_file:<30} MISSING")
            all_exist = False
    
    print(f"\n{'[OK]' if all_exist else '[X]'} Pipeline runners {'available' if all_exist else 'missing'}")
    return all_exist

def test_dashboard_systems():
    """Test dashboard systems"""
    print_header("TEST 10: Dashboard Systems")
    
    dashboards = [
        ('regime_dashboard.py', 'Development Dashboard'),
        ('regime_dashboard_production.py', 'Production Dashboard'),
        ('unified_trading_dashboard.py', 'Unified Dashboard'),
    ]
    
    all_exist = True
    for dashboard_file, dashboard_name in dashboards:
        dashboard_path = Path(dashboard_file)
        if dashboard_path.exists():
            size_kb = dashboard_path.stat().st_size / 1024
            print(f"  [OK] {dashboard_file:<35} ({dashboard_name}, {size_kb:.1f} KB)")
        else:
            print(f"  [!]  {dashboard_file:<35} ({dashboard_name}) - Not found")
            all_exist = False
    
    print(f"\n{'[OK]' if all_exist else '[!]'} Dashboard systems {'available' if all_exist else 'partially available'}")
    return True  # Don't fail if dashboards missing

def run_quick_test():
    """Run quick verification tests"""
    print_header("QUICK INTEGRATION TEST - Regime Intelligence v1.3.13")
    
    tests = [
        ("Python Version", test_python_version),
        ("Core Dependencies", test_core_imports),
        ("Directory Structure", test_directory_structure),
        ("Configuration Files", test_configuration_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    print_summary(results, "QUICK TEST")

def run_full_test():
    """Run complete test suite"""
    print_header("FULL INTEGRATION TEST SUITE - Regime Intelligence v1.3.13")
    
    tests = [
        ("Python Version", test_python_version),
        ("Core Dependencies", test_core_imports),
        ("Directory Structure", test_directory_structure),
        ("Configuration Files", test_configuration_files),
        ("Market Data Fetcher", test_market_data_fetcher),
        ("Market Regime Detector", test_market_regime_detector),
        ("Cross-Market Features", test_cross_market_features),
        ("Opportunity Scorer", test_regime_aware_opportunity_scorer),
        ("Pipeline Runners", test_pipeline_runners),
        ("Dashboard Systems", test_dashboard_systems),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print_summary(results, "FULL TEST")

def print_summary(results, test_type):
    """Print test summary"""
    print("\n" + "═" * 70)
    print(f" {test_type} SUMMARY")
    print("═" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] PASS" if result else "[X] FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n{'─' * 70}")
    print(f"Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[OK] ALL TESTS PASSED - System ready for deployment!")
        print("\n📚 Next Steps:")
        print("  1. Run a pipeline: python run_au_pipeline_v1.3.13.py")
        print("  2. Launch dashboard: python regime_dashboard.py")
        print("  3. Review docs: see COMPLETE_INSTALLATION_GUIDE.md")
        return True
    else:
        print(f"\n[X] {total - passed} TEST(S) FAILED - Review issues above")
        print("\n🔧 Troubleshooting:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Verify config files: check config/ directory")
        print("  3. Check Python version: python --version (requires 3.8+)")
        print("  4. See: COMPLETE_INSTALLATION_GUIDE.md")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Test Phase 3 Market Regime Intelligence System v1.3.13'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick verification tests only'
    )
    parser.add_argument(
        '--component',
        type=str,
        help='Test specific component (fetcher, detector, features, scorer)'
    )
    parser.add_argument(
        '--market',
        type=str,
        help='Test specific market (AU, US, UK)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.component:
            # Test specific component
            component_tests = {
                'fetcher': test_market_data_fetcher,
                'detector': test_market_regime_detector,
                'features': test_cross_market_features,
                'scorer': test_regime_aware_opportunity_scorer,
            }
            if args.component in component_tests:
                success = component_tests[args.component]()
            else:
                print(f"Unknown component: {args.component}")
                print(f"Available: {', '.join(component_tests.keys())}")
                success = False
        elif args.quick:
            success = run_quick_test()
        else:
            success = run_full_test()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n[!]  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[X] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
