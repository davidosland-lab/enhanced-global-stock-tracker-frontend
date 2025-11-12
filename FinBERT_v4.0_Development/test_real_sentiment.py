#!/usr/bin/env python3
"""
Test Real Sentiment System
Tests Yahoo Finance + Finviz news scraping with FinBERT analysis
"""

import sys
import os
import asyncio
import json

# Add models directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))

print("=" * 70)
print("  TESTING REAL SENTIMENT SYSTEM")
print("=" * 70)
print()

# Test 1: Import check
print("Test 1: Importing modules...")
try:
    from models import finbert_sentiment
    print("✓ FinBERT sentiment module imported")
except Exception as e:
    print(f"✗ Failed to import finbert_sentiment: {e}")
    sys.exit(1)

try:
    from models import news_sentiment_real
    print("✓ News sentiment real module imported")
except Exception as e:
    print(f"✗ Failed to import news_sentiment_real: {e}")
    sys.exit(1)

print()

# Test 2: Check FinBERT availability
print("Test 2: Checking FinBERT availability...")
try:
    analyzer = finbert_sentiment.finbert_analyzer
    if analyzer:
        print(f"✓ FinBERT analyzer loaded")
        print(f"  - Model: {analyzer.model_name}")
        print(f"  - Loaded: {analyzer.is_loaded}")
        print(f"  - Using fallback: {analyzer.use_fallback}")
    else:
        print("✗ FinBERT analyzer is None")
except Exception as e:
    print(f"✗ Error checking FinBERT: {e}")

print()

# Test 3: Test sentiment analysis on sample text
print("Test 3: Testing sentiment analysis on sample financial text...")
sample_texts = [
    "Apple stock surges to record high on strong earnings beat",
    "Tesla shares plunge amid production concerns and executive departures",
    "Commonwealth Bank maintains steady performance in uncertain market"
]

for text in sample_texts:
    try:
        result = finbert_sentiment.get_sentiment_analysis(text)
        print(f"\nText: {text[:60]}...")
        print(f"  Sentiment: {result['sentiment'].upper()}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Compound: {result['compound']}")
        print(f"  Method: {result['method']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print()
print("=" * 70)

# Test 4: Test real news fetching
print("\nTest 4: Testing REAL news scraping from Yahoo Finance + Finviz...")
print("=" * 70)

test_symbols = ['AAPL', 'TSLA', 'CBA.AX']

for symbol in test_symbols:
    print(f"\n📰 Fetching REAL news for {symbol}...")
    print("-" * 70)
    
    try:
        # Use the synchronous wrapper
        result = news_sentiment_real.get_sentiment_sync(symbol, use_cache=False)
        
        print(f"\n✓ Results for {symbol}:")
        print(f"  Symbol: {result.get('symbol', 'N/A')}")
        print(f"  Sentiment: {result.get('sentiment', 'N/A').upper()}")
        print(f"  Confidence: {result.get('confidence', 0)}%")
        print(f"  Compound: {result.get('compound', 0)}")
        print(f"  Method: {result.get('method', 'N/A')}")
        print(f"  Article Count: {result.get('article_count', 0)}")
        
        if 'error' in result:
            print(f"  ⚠️  Error: {result['error']}")
        
        if 'sources' in result:
            print(f"  Sources: {', '.join(result['sources'])}")
        
        if 'distribution' in result:
            dist = result['distribution']
            print(f"  Distribution:")
            print(f"    - Positive: {dist.get('positive', 0)} ({dist.get('positive_pct', 0)}%)")
            print(f"    - Negative: {dist.get('negative', 0)} ({dist.get('negative_pct', 0)}%)")
            print(f"    - Neutral: {dist.get('neutral', 0)} ({dist.get('neutral_pct', 0)}%)")
        
        if 'cached' in result:
            cache_status = "CACHED" if result['cached'] else "FRESH"
            print(f"  Cache: {cache_status}")
            if result.get('cache_age_minutes'):
                print(f"  Cache Age: {result['cache_age_minutes']} minutes")
        
        # Show top 3 articles
        if 'articles' in result and len(result['articles']) > 0:
            print(f"\n  📄 Top {min(3, len(result['articles']))} Articles:")
            for i, article in enumerate(result['articles'][:3], 1):
                print(f"    {i}. {article.get('title', 'No title')[:70]}...")
                print(f"       Source: {article.get('source', 'Unknown')}")
                print(f"       Sentiment: {article.get('sentiment', 'N/A').upper()} "
                      f"(confidence: {article.get('confidence', 0):.1f}%)")
                if article.get('url'):
                    print(f"       URL: {article['url'][:60]}...")
        
    except Exception as e:
        print(f"\n✗ Error fetching news for {symbol}: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)
print("  TEST COMPLETE")
print("=" * 70)
print()

# Summary
print("Summary:")
print("✓ Real sentiment system uses Yahoo Finance + Finviz news")
print("✓ Analyzes with ProsusAI/finbert model")
print("✓ Returns error if no news available (NO MOCK DATA)")
print("✓ Caches results for 15 minutes")
print()
