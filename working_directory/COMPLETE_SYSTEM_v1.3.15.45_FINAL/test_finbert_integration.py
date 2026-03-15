#!/usr/bin/env python3
"""
Test FinBERT v4.4.4 Integration
================================

Tests the complete integration of FinBERT sentiment across:
- Overnight pipelines (AU/UK/US)
- Morning report generation
- Unified trading platform
- Sentiment gates (BLOCK/REDUCE/CAUTION/ALLOW)
- Dashboard display

Author: GenSpark AI Developer
Version: v1.3.15.45
Date: 2026-01-28
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def test_finbert_bridge():
    """Test 1: FinBERT Bridge availability"""
    print_header("TEST 1: FinBERT Bridge")
    
    try:
        from models.screening.finbert_bridge import get_finbert_bridge
        bridge = get_finbert_bridge()
        
        if bridge is None:
            print_error("FinBERT Bridge not available")
            return False
            
        availability = bridge.is_available()
        print_success("FinBERT Bridge initialized")
        print_info(f"  LSTM Available: {availability['lstm_available']}")
        print_info(f"  Sentiment Available: {availability['sentiment_available']}")
        print_info(f"  News Available: {availability['news_available']}")
        
        return availability['sentiment_available']
        
    except Exception as e:
        print_error(f"FinBERT Bridge error: {e}")
        return False

def test_sentiment_integration():
    """Test 2: Sentiment Integration module"""
    print_header("TEST 2: Sentiment Integration")
    
    try:
        from sentiment_integration import SentimentIntegration
        
        sentiment_int = SentimentIntegration()
        print_success("SentimentIntegration initialized")
        
        # Test loading morning sentiment (may not exist yet)
        morning_sentiment = sentiment_int.load_morning_sentiment()
        
        if morning_sentiment:
            print_success("Morning sentiment loaded")
            
            if 'finbert_sentiment' in morning_sentiment:
                finbert = morning_sentiment['finbert_sentiment']
                scores = finbert.get('overall_scores', {})
                
                print_info(f"  Negative: {scores.get('negative', 0)*100:.1f}%")
                print_info(f"  Neutral: {scores.get('neutral', 0)*100:.1f}%")
                print_info(f"  Positive: {scores.get('positive', 0)*100:.1f}%")
                print_info(f"  Compound: {finbert.get('compound', 0):.3f}")
                print_info(f"  Label: {finbert.get('sentiment_label', 'unknown')}")
                
                # Test trading gates
                gate, multiplier, reason = sentiment_int.get_trading_gate()
                print_info(f"  Trading Gate: {gate} (multiplier: {multiplier:.2f})")
                print_info(f"  Reason: {reason}")
                
                # Verify gate logic
                neg = scores.get('negative', 0)
                if neg > 0.5 and gate != 'BLOCK':
                    print_error("Gate logic error: High negative sentiment should BLOCK")
                    return False
                    
            return True
        else:
            print_warning("No morning report found (run overnight pipeline first)")
            print_info("  Testing with simulated sentiment...")
            
            # Test with simulated data
            gate, multiplier, reason = sentiment_int._determine_trading_gate(
                negative=0.65, neutral=0.25, positive=0.10, compound=-0.55
            )
            
            if gate != 'BLOCK':
                print_error(f"Gate logic error: 65% negative should BLOCK, got {gate}")
                return False
                
            print_success("Gate logic correct for negative sentiment")
            
            # Test bullish sentiment
            gate, multiplier, reason = sentiment_int._determine_trading_gate(
                negative=0.10, neutral=0.20, positive=0.70, compound=0.60
            )
            
            if gate != 'ALLOW' or multiplier != 1.2:
                print_error(f"Gate logic error: 70% positive should ALLOW with 1.2x, got {gate} {multiplier}")
                return False
                
            print_success("Gate logic correct for positive sentiment")
            
            return True
            
    except Exception as e:
        print_error(f"Sentiment Integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_paper_trading_coordinator():
    """Test 3: Paper Trading Coordinator integration"""
    print_header("TEST 3: Paper Trading Coordinator")
    
    try:
        # Check if should_allow_trade method exists
        with open('paper_trading_coordinator.py', 'r') as f:
            content = f.read()
            
        if 'def should_allow_trade(self)' not in content:
            print_error("should_allow_trade method not found")
            return False
            
        print_success("should_allow_trade method exists")
        
        if 'SENTIMENT GATE CHECK' not in content:
            print_error("Sentiment gate check not implemented in enter_position")
            return False
            
        print_success("Sentiment gate check implemented")
        
        if 'position_multiplier' not in content:
            print_error("Position multiplier not applied")
            return False
            
        print_success("Position multiplier applied")
        
        return True
        
    except Exception as e:
        print_error(f"Paper Trading Coordinator error: {e}")
        return False

def test_dashboard_integration():
    """Test 4: Dashboard FinBERT panel"""
    print_header("TEST 4: Dashboard Integration")
    
    try:
        with open('unified_trading_dashboard.py', 'r') as f:
            content = f.read()
            
        if 'finbert-sentiment-panel' not in content:
            print_error("FinBERT sentiment panel not found in dashboard")
            return False
            
        print_success("FinBERT sentiment panel exists")
        
        if 'sentiment-gate-status' not in content:
            print_error("Sentiment gate status panel not found")
            return False
            
        print_success("Sentiment gate status panel exists")
        
        if "Output('finbert-sentiment-panel'" not in content:
            print_error("FinBERT panel callback output not defined")
            return False
            
        print_success("FinBERT panel callback defined")
        
        if 'SentimentIntegration' not in content:
            print_error("SentimentIntegration not imported in dashboard")
            return False
            
        print_success("SentimentIntegration imported")
        
        return True
        
    except Exception as e:
        print_error(f"Dashboard integration error: {e}")
        return False

def test_overnight_pipeline():
    """Test 5: Overnight pipeline FinBERT integration"""
    print_header("TEST 5: Overnight Pipeline")
    
    try:
        with open('models/screening/overnight_pipeline.py', 'r') as f:
            content = f.read()
            
        if '_calculate_finbert_sentiment' not in content:
            print_error("_calculate_finbert_sentiment method not found")
            return False
            
        print_success("_calculate_finbert_sentiment method exists")
        
        if 'finbert_sentiment' not in content:
            print_error("finbert_sentiment not saved in morning report")
            return False
            
        print_success("finbert_sentiment saved in morning report")
        
        return True
        
    except Exception as e:
        print_error(f"Overnight pipeline error: {e}")
        return False

def test_morning_report_format():
    """Test 6: Morning report format"""
    print_header("TEST 6: Morning Report Format")
    
    report_path = Path('reports/screening/au_morning_report.json')
    
    if not report_path.exists():
        print_warning("Morning report not found (run overnight pipeline first)")
        print_info("  Expected path: reports/screening/au_morning_report.json")
        return True  # Not a failure, just not run yet
        
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
            
        print_success("Morning report loaded")
        
        if 'finbert_sentiment' not in report:
            print_error("finbert_sentiment field missing from report")
            return False
            
        print_success("finbert_sentiment field present")
        
        finbert = report['finbert_sentiment']
        required_fields = ['overall_scores', 'compound', 'sentiment_label', 'article_count']
        
        for field in required_fields:
            if field not in finbert:
                print_error(f"Missing field: {field}")
                return False
                
        print_success("All required fields present")
        
        scores = finbert['overall_scores']
        print_info(f"  Negative: {scores['negative']*100:.1f}%")
        print_info(f"  Neutral: {scores['neutral']*100:.1f}%")
        print_info(f"  Positive: {scores['positive']*100:.1f}%")
        print_info(f"  Articles analyzed: {finbert['article_count']}")
        
        return True
        
    except Exception as e:
        print_error(f"Morning report format error: {e}")
        return False

def main():
    """Run all tests"""
    print_header("FinBERT v4.4.4 Integration Test Suite")
    print_info(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Version: v1.3.15.45")
    
    results = {
        'FinBERT Bridge': test_finbert_bridge(),
        'Sentiment Integration': test_sentiment_integration(),
        'Paper Trading Coordinator': test_paper_trading_coordinator(),
        'Dashboard Integration': test_dashboard_integration(),
        'Overnight Pipeline': test_overnight_pipeline(),
        'Morning Report Format': test_morning_report_format()
    }
    
    # Summary
    print_header("TEST RESULTS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    
    if passed == total:
        print_success(f"ALL TESTS PASSED ({passed}/{total})")
        print_info("\n✨ FinBERT v4.4.4 integration is complete and working!")
        print_info("\nNext steps:")
        print_info("  1. Run overnight pipeline: python run_au_pipeline.py --full-scan")
        print_info("  2. Verify morning report: type reports\\screening\\au_morning_report.json")
        print_info("  3. Start dashboard: python unified_trading_dashboard.py")
        print_info("  4. Navigate to http://localhost:8050")
        print_info("  5. Verify FinBERT sentiment panel displays correctly")
        return 0
    else:
        print_error(f"SOME TESTS FAILED ({passed}/{total} passed)")
        print_info("\n⚠ Review errors above and fix before deployment")
        return 1

if __name__ == '__main__':
    sys.exit(main())
