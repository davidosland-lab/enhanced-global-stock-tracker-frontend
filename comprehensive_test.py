#!/usr/bin/env python3
"""
Comprehensive Test Suite for v193.11.6.5
Tests all critical components before deployment
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "ULTIMATE_v193_COMPLETE"
sys.path.insert(0, str(project_root))

print("=" * 80)
print("COMPREHENSIVE TEST SUITE FOR v193.11.6.5")
print("=" * 80)
print()

test_results = []

def log_test(name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append((name, passed, details))
    print(f"{status} - {name}")
    if details:
        print(f"     {details}")
    print()

# ============================================================================
# TEST 1: Version Check
# ============================================================================
print("TEST 1: VERSION CHECK")
print("-" * 80)
try:
    version_file = project_root / "VERSION.json"
    with open(version_file, 'r', encoding='utf-8') as f:
        version_data = json.load(f)
    
    expected_version = "1.3.15.193.11.6.5"
    actual_version = version_data.get('version', '')
    
    if actual_version == expected_version:
        log_test("Version Check", True, f"Version: {actual_version}")
    else:
        log_test("Version Check", False, f"Expected {expected_version}, got {actual_version}")
except Exception as e:
    log_test("Version Check", False, f"Error: {str(e)}")

# ============================================================================
# TEST 2: SPIMonitor Module Import
# ============================================================================
print("TEST 2: SPIMonitor MODULE IMPORT")
print("-" * 80)
try:
    from pipelines.models.screening.spi_monitor import SPIMonitor
    log_test("SPIMonitor Import", True, "Module imported successfully")
except Exception as e:
    log_test("SPIMonitor Import", False, f"Import error: {str(e)}")
    sys.exit(1)

# ============================================================================
# TEST 3: SPIMonitor Instantiation
# ============================================================================
print("TEST 3: SPIMonitor INSTANTIATION")
print("-" * 80)
try:
    monitor = SPIMonitor()
    log_test("SPIMonitor Instantiation", True, "Instance created successfully")
except Exception as e:
    log_test("SPIMonitor Instantiation", False, f"Error: {str(e)}")
    sys.exit(1)

# ============================================================================
# TEST 4: Bug #1 Fix - Missing Methods
# ============================================================================
print("TEST 4: BUG #1 FIX - MISSING METHODS")
print("-" * 80)
try:
    # Check _get_us_markets exists
    has_get_us_markets = hasattr(monitor, '_get_us_markets')
    # Check _get_default_sentiment exists
    has_get_default_sentiment = hasattr(monitor, '_get_default_sentiment')
    # Check _get_us_market_data exists
    has_get_us_market_data = hasattr(monitor, '_get_us_market_data')
    
    if has_get_us_markets and has_get_default_sentiment and has_get_us_market_data:
        log_test("Bug #1 - Missing Methods", True, 
                "_get_us_markets, _get_default_sentiment, _get_us_market_data all exist")
    else:
        missing = []
        if not has_get_us_markets:
            missing.append("_get_us_markets")
        if not has_get_default_sentiment:
            missing.append("_get_default_sentiment")
        if not has_get_us_market_data:
            missing.append("_get_us_market_data")
        log_test("Bug #1 - Missing Methods", False, f"Missing: {', '.join(missing)}")
except Exception as e:
    log_test("Bug #1 - Missing Methods", False, f"Error: {str(e)}")

# ============================================================================
# TEST 5: Bug #2 Fix - _calculate_sentiment_score Arguments
# ============================================================================
print("TEST 5: BUG #2 FIX - _calculate_sentiment_score ARGUMENTS")
print("-" * 80)
try:
    # Create mock data with correct types
    mock_us_data = {
        'SP500': {'change_pct': -1.33},
        'Nasdaq': {'change_pct': -1.59}
    }
    
    mock_gap_prediction = {
        'predicted_gap_pct': 0.11,
        'confidence': 0.75,
        'direction': 'NEUTRAL'
    }
    
    mock_asx_data = {
        'seven_day_change_pct': 2.5,
        'fourteen_day_change_pct': 3.2
    }
    
    # Test the method with correct argument order
    sentiment_score = monitor._calculate_sentiment_score(
        mock_us_data,
        mock_gap_prediction,
        mock_asx_data
    )
    
    if isinstance(sentiment_score, (int, float)) and 0 <= sentiment_score <= 100:
        log_test("Bug #2 - Sentiment Score Arguments", True, 
                f"Score: {sentiment_score:.1f}/100 (correct argument order)")
    else:
        log_test("Bug #2 - Sentiment Score Arguments", False, 
                f"Invalid score: {sentiment_score}")
except Exception as e:
    log_test("Bug #2 - Sentiment Score Arguments", False, f"Error: {str(e)}")

# ============================================================================
# TEST 6: Bug #3 Fix - _get_recommendation Arguments
# ============================================================================
print("TEST 6: BUG #3 FIX - _get_recommendation ARGUMENTS")
print("-" * 80)
try:
    # Test with correct argument type (Dict, not float)
    mock_sentiment_score = 65.0
    mock_gap_prediction = {
        'predicted_gap_pct': 0.5,
        'confidence': 0.75,
        'direction': 'BULLISH'
    }
    
    recommendation = monitor._get_recommendation(
        mock_sentiment_score,
        mock_gap_prediction  # Passing Dict, not float
    )
    
    if isinstance(recommendation, dict) and 'stance' in recommendation:
        log_test("Bug #3 - Recommendation Arguments", True, 
                f"Stance: {recommendation.get('stance', 'UNKNOWN')}")
    else:
        log_test("Bug #3 - Recommendation Arguments", False, 
                f"Invalid recommendation: {recommendation}")
except Exception as e:
    log_test("Bug #3 - Recommendation Arguments", False, f"Error: {str(e)}")

# ============================================================================
# TEST 7: Bug #4 Fix - Logger Initialization
# ============================================================================
print("TEST 7: BUG #4 FIX - LOGGER INITIALIZATION")
print("-" * 80)
try:
    # Check if logger is defined in the module
    from pipelines.models.screening import spi_monitor
    has_logger = hasattr(spi_monitor, 'logger')
    
    if has_logger:
        log_test("Bug #4 - Logger Initialization", True, 
                "Logger is properly initialized before use")
    else:
        log_test("Bug #4 - Logger Initialization", False, 
                "Logger not found in module")
except Exception as e:
    log_test("Bug #4 - Logger Initialization", False, f"Error: {str(e)}")

# ============================================================================
# TEST 8: _get_default_sentiment Functionality
# ============================================================================
print("TEST 8: _get_default_sentiment FUNCTIONALITY")
print("-" * 80)
try:
    default_sentiment = monitor._get_default_sentiment()
    
    expected_keys = ['sentiment_score', 'predicted_gap_pct', 'confidence', 'direction']
    has_all_keys = all(key in default_sentiment for key in expected_keys)
    
    if has_all_keys:
        log_test("Default Sentiment", True, 
                f"Score: {default_sentiment['sentiment_score']}, "
                f"Gap: {default_sentiment['predicted_gap_pct']}%, "
                f"Direction: {default_sentiment['direction']}")
    else:
        missing_keys = [k for k in expected_keys if k not in default_sentiment]
        log_test("Default Sentiment", False, f"Missing keys: {missing_keys}")
except Exception as e:
    log_test("Default Sentiment", False, f"Error: {str(e)}")

# ============================================================================
# TEST 9: _get_us_markets Alias
# ============================================================================
print("TEST 9: _get_us_markets ALIAS")
print("-" * 80)
try:
    # This should call _get_us_market_data internally
    us_markets = monitor._get_us_markets()
    
    if isinstance(us_markets, dict):
        market_count = len(us_markets)
        log_test("US Markets Alias", True, 
                f"Retrieved {market_count} market(s) data")
    else:
        log_test("US Markets Alias", False, 
                f"Expected dict, got {type(us_markets)}")
except Exception as e:
    log_test("US Markets Alias", False, f"Error: {str(e)}")

# ============================================================================
# TEST 10: Web Control Center Exists
# ============================================================================
print("TEST 10: WEB CONTROL CENTER")
print("-" * 80)
try:
    wcc_file = project_root / "web_control_center.py"
    if wcc_file.exists():
        file_size = wcc_file.stat().st_size
        log_test("Web Control Center", True, 
                f"File exists ({file_size} bytes)")
    else:
        log_test("Web Control Center", False, "File not found")
except Exception as e:
    log_test("Web Control Center", False, f"Error: {str(e)}")

# ============================================================================
# TEST 11: Installation Scripts
# ============================================================================
print("TEST 11: INSTALLATION SCRIPTS")
print("-" * 80)
try:
    install_first = project_root / "INSTALL_FIRST_TIME.bat"
    install_complete = project_root / "INSTALL_COMPLETE_v193.bat"
    
    has_first = install_first.exists()
    has_complete = install_complete.exists()
    
    if has_first and has_complete:
        log_test("Installation Scripts", True, 
                "INSTALL_FIRST_TIME.bat and INSTALL_COMPLETE_v193.bat exist")
    else:
        missing = []
        if not has_first:
            missing.append("INSTALL_FIRST_TIME.bat")
        if not has_complete:
            missing.append("INSTALL_COMPLETE_v193.bat")
        log_test("Installation Scripts", False, f"Missing: {', '.join(missing)}")
except Exception as e:
    log_test("Installation Scripts", False, f"Error: {str(e)}")

# ============================================================================
# TEST 12: Critical Documentation Files
# ============================================================================
print("TEST 12: DOCUMENTATION FILES")
print("-" * 80)
try:
    docs_to_check = [
        "README_DEPLOYMENT_v193.11.6.5.txt",
        "QUICK_START_v193.11.6.5.txt",
        "DEPLOYMENT_READY_v193.11.6.5.txt",
        "FINAL_DEPLOYMENT_SUMMARY_v193.11.6.5.txt"
    ]
    
    # Check in both project root and parent directory
    found_docs = []
    for doc in docs_to_check:
        if (project_root / doc).exists() or (project_root.parent / doc).exists():
            found_docs.append(doc)
    
    if len(found_docs) >= 3:  # At least 3 out of 4 should exist
        log_test("Documentation Files", True, 
                f"Found {len(found_docs)}/{len(docs_to_check)} documentation files")
    else:
        log_test("Documentation Files", False, 
                f"Only found {len(found_docs)}/{len(docs_to_check)} files")
except Exception as e:
    log_test("Documentation Files", False, f"Error: {str(e)}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)

total_tests = len(test_results)
passed_tests = sum(1 for _, passed, _ in test_results if passed)
failed_tests = total_tests - passed_tests

print(f"\nTotal Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print()

if failed_tests > 0:
    print("FAILED TESTS:")
    print("-" * 80)
    for name, passed, details in test_results:
        if not passed:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
    print()

# Overall result
if failed_tests == 0:
    print("=" * 80)
    print("🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT")
    print("=" * 80)
    sys.exit(0)
else:
    print("=" * 80)
    print("⚠️  SOME TESTS FAILED - DO NOT DEPLOY")
    print("=" * 80)
    sys.exit(1)
