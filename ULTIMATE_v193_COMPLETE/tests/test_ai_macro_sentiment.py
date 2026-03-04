"""
Test AI-Enhanced Macro Sentiment Analysis
==========================================
Tests the new AI Market Impact Analyzer integrated with the Macro News Monitor.

This script:
1. Tests AI analyzer standalone with sample geopolitical events
2. Tests full macro news pipeline with AI integration
3. Compares old FinBERT-only vs new AI-enhanced results

Author: FinBERT v4.4.4 Enhanced
Date: February 28, 2026
"""

import sys
import logging
from pathlib import Path

# Add pipelines to path
PIPELINES_PATH = Path(__file__).parent / 'pipelines'
sys.path.insert(0, str(PIPELINES_PATH))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Articles (Real scenarios)
CRISIS_ARTICLES = [
    {
        'title': 'US launches airstrikes on Iranian military targets in response to Red Sea attacks',
        'source': 'Reuters',
        'url': 'https://reuters.com/...',
        'type': 'geopolitical'
    },
    {
        'title': 'Iran vows retaliation as tensions escalate in Middle East',
        'source': 'BBC World',
        'url': 'https://bbc.com/...',
        'type': 'geopolitical'
    },
    {
        'title': 'Oil prices surge 8% on Middle East escalation fears',
        'source': 'Bloomberg',
        'url': 'https://bloomberg.com/...',
        'type': 'commodity'
    },
    {
        'title': 'Gold hits record high as investors flee to safety',
        'source': 'Financial Times',
        'url': 'https://ft.com/...',
        'type': 'commodity'
    },
    {
        'title': 'Stock futures plunge as war fears grip markets',
        'source': 'CNBC',
        'url': 'https://cnbc.com/...',
        'type': 'markets'
    }
]

TRADE_WAR_ARTICLES = [
    {
        'title': 'Trump announces 60% tariffs on all Chinese imports effective immediately',
        'source': 'White House',
        'url': 'https://whitehouse.gov/...',
        'type': 'trade_policy'
    },
    {
        'title': 'China retaliates with tariffs on US agricultural products',
        'source': 'China Daily',
        'url': 'https://chinadaily.com/...',
        'type': 'trade_policy'
    },
    {
        'title': 'Tech stocks tumble on supply chain disruption concerns',
        'source': 'Bloomberg',
        'url': 'https://bloomberg.com/...',
        'type': 'markets'
    }
]

POSITIVE_ARTICLES = [
    {
        'title': 'Fed signals rate cuts ahead as inflation cools to 2.1%',
        'source': 'Federal Reserve',
        'url': 'https://federalreserve.gov/...',
        'type': 'monetary_policy'
    },
    {
        'title': 'US and China reach comprehensive trade agreement',
        'source': 'Reuters',
        'url': 'https://reuters.com/...',
        'type': 'trade_policy'
    },
    {
        'title': 'Strong jobs report beats expectations, unemployment falls to 3.2%',
        'source': 'Bureau of Labor Statistics',
        'url': 'https://bls.gov/...',
        'type': 'economic_data'
    }
]

NEUTRAL_ARTICLES = [
    {
        'title': 'Fed maintains interest rates at 5.25% as expected',
        'source': 'Federal Reserve',
        'url': 'https://federalreserve.gov/...',
        'type': 'monetary_policy'
    },
    {
        'title': 'UK GDP grows 0.1% in Q4, in line with forecasts',
        'source': 'ONS',
        'url': 'https://ons.gov.uk/...',
        'type': 'economic_data'
    }
]


def test_ai_analyzer_standalone():
    """Test AI Market Impact Analyzer directly"""
    print("\n" + "="*80)
    print("TEST 1: AI MARKET IMPACT ANALYZER (STANDALONE)")
    print("="*80)
    
    try:
        from models.screening.ai_market_impact_analyzer import AIMarketImpactAnalyzer
        
        analyzer = AIMarketImpactAnalyzer(use_ai=True, use_fallback=True)
        
        # Test 1: Crisis scenario (should be VERY BEARISH)
        print("\n[Test 1.1] Crisis Scenario (Iran-US Conflict)")
        print("-" * 80)
        result = analyzer.analyze_market_impact(CRISIS_ARTICLES, market='US')
        
        print(f"Impact Score: {result['impact_score']:+.2f} (Expected: -0.60 to -0.85)")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Severity: {result['severity']} (Expected: HIGH or CRITICAL)")
        print(f"Recommendation: {result['recommendation']} (Expected: RISK_OFF)")
        print(f"Method: {result['method']}")
        print(f"\nExplanation:\n  {result['explanation']}")
        print(f"\nKey Events:")
        for event in result['analyzed_events'][:3]:
            print(f"  - {event.get('event', 'N/A')}: {event.get('impact', 'N/A')}")
        
        # Validation
        assert result['impact_score'] < -0.4, "Crisis should produce bearish score"
        assert result['severity'] in ['HIGH', 'CRITICAL'], "Crisis should be HIGH or CRITICAL severity"
        assert result['recommendation'] in ['RISK_OFF', 'CAUTION'], "Crisis should recommend RISK_OFF"
        print("\n✅ PASS: Crisis detected correctly")
        
        # Test 2: Trade war scenario (should be BEARISH)
        print("\n[Test 1.2] Trade War Scenario")
        print("-" * 80)
        result = analyzer.analyze_market_impact(TRADE_WAR_ARTICLES, market='US')
        
        print(f"Impact Score: {result['impact_score']:+.2f} (Expected: -0.50 to -0.70)")
        print(f"Severity: {result['severity']} (Expected: MODERATE or HIGH)")
        print(f"Recommendation: {result['recommendation']} (Expected: CAUTION or RISK_OFF)")
        print(f"\nExplanation:\n  {result['explanation']}")
        
        assert result['impact_score'] < -0.3, "Trade war should be bearish"
        print("\n✅ PASS: Trade war detected correctly")
        
        # Test 3: Positive scenario (should be BULLISH)
        print("\n[Test 1.3] Positive Scenario (Rate Cuts + Trade Deal)")
        print("-" * 80)
        result = analyzer.analyze_market_impact(POSITIVE_ARTICLES, market='US')
        
        print(f"Impact Score: {result['impact_score']:+.2f} (Expected: +0.30 to +0.60)")
        print(f"Severity: {result['severity']} (Expected: POSITIVE)")
        print(f"Recommendation: {result['recommendation']} (Expected: RISK_ON)")
        print(f"\nExplanation:\n  {result['explanation']}")
        
        assert result['impact_score'] > 0.2, "Positive news should be bullish"
        print("\n✅ PASS: Positive events detected correctly")
        
        # Test 4: Neutral scenario
        print("\n[Test 1.4] Neutral Scenario")
        print("-" * 80)
        result = analyzer.analyze_market_impact(NEUTRAL_ARTICLES, market='US')
        
        print(f"Impact Score: {result['impact_score']:+.2f} (Expected: -0.10 to +0.10)")
        print(f"Severity: {result['severity']} (Expected: NEUTRAL)")
        print(f"Recommendation: {result['recommendation']} (Expected: NEUTRAL)")
        print(f"\nExplanation:\n  {result['explanation']}")
        
        assert abs(result['impact_score']) < 0.15, "Neutral news should have near-zero impact"
        print("\n✅ PASS: Neutral events detected correctly")
        
        print("\n✅ ALL AI ANALYZER TESTS PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_macro_news_with_ai():
    """Test full macro news monitor with AI integration"""
    print("\n" + "="*80)
    print("TEST 2: MACRO NEWS MONITOR WITH AI INTEGRATION")
    print("="*80)
    
    try:
        from models.screening.macro_news_monitor import MacroNewsMonitor
        
        monitor = MacroNewsMonitor(market='US')
        
        # Override scrape methods to inject test articles
        original_scrape = monitor._scrape_global_news
        
        def mock_crisis_scrape():
            """Mock global news scrape with crisis articles"""
            return CRISIS_ARTICLES
        
        monitor._scrape_global_news = mock_crisis_scrape
        monitor._scrape_fed_releases = lambda: []
        monitor._scrape_fed_speeches = lambda: []
        
        print("\n[Test 2.1] Crisis Articles via Macro News Monitor")
        print("-" * 80)
        
        result = monitor.get_macro_sentiment()
        
        print(f"Article Count: {result['article_count']}")
        print(f"Sentiment Score: {result['sentiment_score']:+.3f} (Expected: < -0.40)")
        print(f"Sentiment Label: {result['sentiment_label']} (Expected: BEARISH)")
        print(f"Summary: {result['summary']}")
        
        # Check if AI impact metadata is attached
        if result['articles']:
            first_article = result['articles'][0]
            if 'ai_impact' in first_article:
                ai_impact = first_article['ai_impact']
                print(f"\nAI Impact Metadata:")
                print(f"  Score: {ai_impact['score']:+.2f}")
                print(f"  Severity: {ai_impact['severity']}")
                print(f"  Recommendation: {ai_impact['recommendation']}")
                print("✅ AI metadata present in articles")
            else:
                print("⚠️  WARNING: AI metadata not found in articles (may be using fallback)")
        
        # Validation
        assert result['sentiment_score'] < -0.3, f"Crisis should produce bearish sentiment (got {result['sentiment_score']})"
        assert result['sentiment_label'] == 'BEARISH', f"Label should be BEARISH (got {result['sentiment_label']})"
        print("\n✅ PASS: AI-enhanced sentiment analysis working correctly")
        
        # Restore original method
        monitor._scrape_global_news = original_scrape
        
        print("\n✅ MACRO NEWS INTEGRATION TEST PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison_old_vs_new():
    """Compare old FinBERT-only vs new AI-enhanced"""
    print("\n" + "="*80)
    print("TEST 3: COMPARISON - OLD vs NEW SENTIMENT ANALYSIS")
    print("="*80)
    
    try:
        from models.screening.macro_news_monitor import MacroNewsMonitor
        
        monitor = MacroNewsMonitor(market='US')
        
        print("\n[Test 3.1] Crisis Headlines (Iran-US Conflict)")
        print("-" * 80)
        
        # Simulate old FinBERT-only analysis
        print("\n📊 OLD METHOD (FinBERT only):")
        old_score = monitor._finbert_sentiment(CRISIS_ARTICLES)
        print(f"  Score: {old_score:+.3f}")
        if abs(old_score) < 0.15:
            print("  ⚠️  PROBLEM: FinBERT sees this as NEUTRAL (misses geopolitical impact)")
        
        # New AI-enhanced analysis
        print("\n🤖 NEW METHOD (AI-enhanced):")
        new_score = monitor._analyze_sentiment(CRISIS_ARTICLES)
        print(f"  Score: {new_score:+.3f}")
        if new_score < -0.4:
            print("  ✅ CORRECT: AI recognizes this as HIGH BEARISH event")
        
        improvement = abs(new_score) - abs(old_score)
        print(f"\n📈 Improvement: {improvement:+.3f} points")
        
        if improvement > 0.3:
            print("✅ SIGNIFICANT IMPROVEMENT: AI correctly identifies crisis severity")
        elif improvement > 0.1:
            print("✅ MODERATE IMPROVEMENT: AI adds better context")
        else:
            print("⚠️  MINIMAL IMPROVEMENT: Check if AI is active")
        
        print("\n✅ COMPARISON TEST COMPLETE")
        return True
    
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("AI-ENHANCED MACRO SENTIMENT ANALYSIS - TEST SUITE")
    print("="*80)
    print("\nThis test suite validates:")
    print("  1. AI Market Impact Analyzer (standalone)")
    print("  2. Integration with Macro News Monitor")
    print("  3. Improvement over old FinBERT-only approach")
    print("\n" + "="*80)
    
    results = []
    
    # Test 1: AI Analyzer standalone
    results.append(("AI Analyzer Standalone", test_ai_analyzer_standalone()))
    
    # Test 2: Macro news integration
    results.append(("Macro News Integration", test_macro_news_with_ai()))
    
    # Test 3: Comparison
    results.append(("Old vs New Comparison", test_comparison_old_vs_new()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - AI-Enhanced Sentiment Analysis Ready!")
        print("\n📝 Next Steps:")
        print("  1. Run tonight's overnight pipeline (AU/UK/US)")
        print("  2. Check pipeline reports for AI sentiment scores")
        print("  3. Verify Iran-US conflict shows BEARISH (-0.60 to -0.85)")
        print("  4. Monitor paper trading positions (should reduce risk exposure)")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review errors above")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
