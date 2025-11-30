"""
ChatGPT Research Integration Test Script

This script tests the ChatGPT research functionality with sample stock data.
It verifies:
1. OpenAI API connection
2. Research generation for sample stocks
3. Markdown report creation
4. Integration with pipeline data structures

Usage:
    python TEST_CHATGPT_RESEARCH.py
    
Requirements:
    - OPENAI_API_KEY environment variable must be set
    - pip install openai
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add models to path
sys.path.insert(0, str(Path(__file__).parent / 'models' / 'screening'))

from chatgpt_research import (
    test_chatgpt_connection,
    run_chatgpt_research,
    save_markdown
)


def test_connection():
    """Test OpenAI API connection"""
    print("="*80)
    print("TEST 1: OpenAI API Connection")
    print("="*80)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("   Set it with: $env:OPENAI_API_KEY='your-api-key'")
        return False
    
    print(f"✓ OPENAI_API_KEY found ({len(api_key)} characters)")
    
    # Test connection
    if test_chatgpt_connection():
        print("✅ Connection test PASSED")
        return True
    else:
        print("❌ Connection test FAILED")
        return False


def test_research_generation():
    """Test research generation with sample data"""
    print("\n" + "="*80)
    print("TEST 2: Research Generation")
    print("="*80)
    
    # Create sample opportunities (ASX stocks)
    sample_opportunities_asx = [
        {
            'symbol': 'BHP.AX',
            'company_name': 'BHP Group Limited',
            'sector': 'Materials',
            'opportunity_score': 85.5,
            'prediction': 0.65,
            'confidence': 78.2,
            'technical': {
                'rsi': 55.2,
                'macd_signal': 'bullish',
                'volume_trend': 'increasing'
            },
            'sentiment': {
                'direction': 'positive',
                'confidence': 72.5
            }
        },
        {
            'symbol': 'CBA.AX',
            'company_name': 'Commonwealth Bank of Australia',
            'sector': 'Financials',
            'opportunity_score': 82.3,
            'prediction': 0.58,
            'confidence': 75.8,
            'technical': {
                'rsi': 52.1,
                'macd_signal': 'neutral',
                'volume_trend': 'stable'
            },
            'sentiment': {
                'direction': 'positive',
                'confidence': 68.3
            }
        }
    ]
    
    # Create sample opportunities (US stocks)
    sample_opportunities_us = [
        {
            'symbol': 'AAPL',
            'company_name': 'Apple Inc.',
            'sector': 'Technology',
            'opportunity_score': 88.2,
            'prediction': 0.72,
            'confidence': 81.5,
            'technical': {
                'rsi': 58.3,
                'macd_signal': 'bullish',
                'volume_trend': 'increasing'
            },
            'sentiment': {
                'direction': 'positive',
                'confidence': 75.2
            }
        }
    ]
    
    print("\n📊 Testing ASX Research...")
    asx_results = run_chatgpt_research(
        opportunities=sample_opportunities_asx,
        model='gpt-4o-mini',
        max_stocks=2,
        market='ASX'
    )
    
    if asx_results:
        print(f"✅ ASX Research PASSED: {len(asx_results)} stocks analyzed")
        for symbol, content in asx_results.items():
            print(f"   - {symbol}: {len(content)} characters")
    else:
        print("❌ ASX Research FAILED")
        return False
    
    print("\n📊 Testing US Research...")
    us_results = run_chatgpt_research(
        opportunities=sample_opportunities_us,
        model='gpt-4o-mini',
        max_stocks=1,
        market='US'
    )
    
    if us_results:
        print(f"✅ US Research PASSED: {len(us_results)} stocks analyzed")
        for symbol, content in us_results.items():
            print(f"   - {symbol}: {len(content)} characters")
    else:
        print("❌ US Research FAILED")
        return False
    
    return True, asx_results, us_results


def test_markdown_export(asx_results, us_results):
    """Test markdown report generation"""
    print("\n" + "="*80)
    print("TEST 3: Markdown Export")
    print("="*80)
    
    try:
        # Test ASX markdown export
        asx_path = Path(__file__).parent / 'test_reports' / 'test_asx_research.md'
        asx_metadata = {
            'run_id': datetime.now().strftime("%Y%m%d"),
            'total_opportunities': 100,
            'market': 'ASX'
        }
        
        asx_md_path = save_markdown(
            research_results=asx_results,
            output_path=asx_path,
            market='ASX',
            pipeline_metadata=asx_metadata
        )
        
        print(f"✅ ASX Markdown saved: {asx_md_path}")
        print(f"   Size: {asx_md_path.stat().st_size} bytes")
        
        # Test US markdown export
        us_path = Path(__file__).parent / 'test_reports' / 'test_us_research.md'
        us_metadata = {
            'run_id': datetime.now().strftime("%Y%m%d"),
            'total_opportunities': 240,
            'market': 'US'
        }
        
        us_md_path = save_markdown(
            research_results=us_results,
            output_path=us_path,
            market='US',
            pipeline_metadata=us_metadata
        )
        
        print(f"✅ US Markdown saved: {us_md_path}")
        print(f"   Size: {us_md_path.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Markdown export FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("CHATGPT RESEARCH INTEGRATION TEST SUITE")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    results = []
    
    # Test 1: Connection
    try:
        connection_ok = test_connection()
        results.append(("API Connection", connection_ok))
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        results.append(("API Connection", False))
        connection_ok = False
    
    if not connection_ok:
        print("\n⚠️  Cannot proceed without API connection")
        print_summary(results)
        return
    
    # Test 2: Research Generation
    try:
        research_ok, asx_results, us_results = test_research_generation()
        results.append(("Research Generation", research_ok))
    except Exception as e:
        print(f"❌ Research generation error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Research Generation", False))
        research_ok = False
        asx_results = {}
        us_results = {}
    
    # Test 3: Markdown Export
    if research_ok and asx_results and us_results:
        try:
            markdown_ok = test_markdown_export(asx_results, us_results)
            results.append(("Markdown Export", markdown_ok))
        except Exception as e:
            print(f"❌ Markdown export error: {e}")
            import traceback
            traceback.print_exc()
            results.append(("Markdown Export", False))
    else:
        print("\n⚠️  Skipping markdown export test (no research results)")
        results.append(("Markdown Export", False))
    
    # Print summary
    print_summary(results)


def print_summary(results):
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - ChatGPT Research is ready!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - please review errors above")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
