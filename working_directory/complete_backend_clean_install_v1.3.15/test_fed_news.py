#!/usr/bin/env python3
"""
Test Fed News Monitoring Integration
Verify that MacroNewsMonitor fetches and analyzes Fed announcements
"""

import sys
from pathlib import Path

# Add project root to path
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH))

print("="*80)
print("FED NEWS MONITORING TEST")
print("="*80)
print()

# Test 1: Import MacroNewsMonitor
print("[1/4] Testing MacroNewsMonitor import...")
try:
    from models.screening.macro_news_monitor import MacroNewsMonitor
    print("  [OK] MacroNewsMonitor imported successfully")
except ImportError as e:
    print(f"  [ERROR] Failed to import: {e}")
    sys.exit(1)

# Test 2: Initialize for US market
print()
print("[2/4] Initializing MacroNewsMonitor for US market...")
try:
    monitor = MacroNewsMonitor(market='US')
    print("  [OK] Monitor initialized")
    print(f"  Market: {monitor.market}")
    print(f"  Fed sources configured: {len([s for s in monitor.sources if 'federal' in s.lower()])}")
except Exception as e:
    print(f"  [ERROR] Initialization failed: {e}")
    sys.exit(1)

# Test 3: Fetch Fed news
print()
print("[3/4] Fetching Fed news and announcements...")
print("  (This may take 10-15 seconds...)")
try:
    macro_sentiment = monitor.get_macro_sentiment()
    print(f"  [OK] Fed news retrieved")
    print(f"  Articles analyzed: {macro_sentiment['article_count']}")
    print(f"  Sentiment score: {macro_sentiment['sentiment_score']:.3f} (-1 to +1)")
    print(f"  Sentiment label: {macro_sentiment['sentiment_label']}")
    print(f"  Summary: {macro_sentiment['summary']}")
except Exception as e:
    print(f"  [ERROR] Failed to fetch: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Display recent Fed articles
print()
print("[4/4] Recent Fed News Articles:")
print("-" * 80)
if macro_sentiment['top_articles']:
    for i, article in enumerate(macro_sentiment['top_articles'][:5], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Date: {article['date']}")
        print(f"   Sentiment: {article['sentiment']:.3f}")
        print(f"   URL: {article['url'][:80]}...")
else:
    print("  [WARNING] No articles found")

print()
print("="*80)
print("FED NEWS MONITORING TEST COMPLETE")
print("="*80)
print()
print("Next Steps:")
print("1. Run US Overnight Pipeline: LAUNCH_COMPLETE_SYSTEM.bat → Option 2")
print("2. Check logs for 'PHASE 1.3: MACRO NEWS MONITORING'")
print("3. Verify Fed news appears in terminal output")
print("4. Check HTML report for macro news section")
