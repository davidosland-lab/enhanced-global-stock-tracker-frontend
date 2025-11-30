"""
Simple Macro News Test
Quick test to see if macro news scraping works
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("TESTING MACRO NEWS MONITOR")
print("="*80)

# Test import
print("\n1. Importing MacroNewsMonitor...")
try:
    from models.screening.macro_news_monitor import MacroNewsMonitor
    print("   ✓ SUCCESS")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# Test US market
print("\n2. Testing US Federal Reserve news scraping...")
print("   (This takes 10-15 seconds due to respectful delays)")
try:
    monitor = MacroNewsMonitor(market='US')
    news = monitor.get_macro_sentiment()
    
    print(f"\n   Results:")
    print(f"   - Articles found: {news['article_count']}")
    print(f"   - Sentiment score: {news['sentiment_score']:.3f}")
    print(f"   - Sentiment label: {news['sentiment_label']}")
    
    if news['article_count'] > 0:
        print(f"\n   ✓ MACRO NEWS IS WORKING!")
        print(f"\n   Recent headlines:")
        for i, article in enumerate(news['articles'][:3], 1):
            title = article['title'][:70]
            print(f"   {i}. {title}")
    else:
        print(f"\n   ⚠ No articles found (check network connection)")
        
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
print("\nWhat this means:")
print("- If articles found: Macro news IS working in your system")
print("- If no articles: Check your internet/firewall")
print("\nTo see this in your pipeline:")
print("- Look for 'MACRO NEWS ANALYSIS' in pipeline logs")
print("- Should appear during Phase 1 (Market Sentiment)")
