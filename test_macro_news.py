"""
Macro News Monitor Test Script
Tests if macro news scraping and analysis is working
"""

import sys
import logging
from pathlib import Path

# Add models to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("="*80)
print("MACRO NEWS MONITOR DIAGNOSTIC TEST")
print("="*80)

# Test 1: Check if module can be imported
print("\n[TEST 1] Checking if MacroNewsMonitor can be imported...")
try:
    from models.screening.macro_news_monitor import MacroNewsMonitor
    print("✓ MacroNewsMonitor imported successfully")
except ImportError as e:
    print(f"✗ Failed to import MacroNewsMonitor: {e}")
    print("\nPossible issues:")
    print("  - models/screening/macro_news_monitor.py doesn't exist")
    print("  - Missing dependencies (requests, beautifulsoup4)")
    sys.exit(1)

# Test 2: Check dependencies
print("\n[TEST 2] Checking dependencies...")
try:
    import requests
    print("✓ requests library available")
except ImportError:
    print("✗ requests library missing")
    print("  Install with: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print("✓ beautifulsoup4 library available")
except ImportError:
    print("✗ beautifulsoup4 library missing")
    print("  Install with: pip install beautifulsoup4")
    sys.exit(1)

# Test 3: Initialize monitor for US market
print("\n[TEST 3] Initializing MacroNewsMonitor for US market...")
try:
    us_monitor = MacroNewsMonitor(market='US')
    print("✓ US MacroNewsMonitor initialized")
except Exception as e:
    print(f"✗ Failed to initialize US monitor: {e}")
    sys.exit(1)

# Test 4: Test US macro news fetching
print("\n[TEST 4] Fetching US macro news (Federal Reserve)...")
print("This may take 10-20 seconds due to respectful scraping delays...\n")
try:
    us_news = us_monitor.get_macro_sentiment()
    
    print("\n" + "="*80)
    print("US MACRO NEWS RESULTS")
    print("="*80)
    print(f"Articles Found: {us_news['article_count']}")
    print(f"Sentiment Score: {us_news['sentiment_score']:.3f} (-1=bearish, +1=bullish)")
    print(f"Sentiment Label: {us_news['sentiment_label']}")
    
    if us_news['article_count'] > 0:
        print(f"\nRecent Headlines:")
        for i, article in enumerate(us_news['articles'][:5], 1):
            print(f"  {i}. {article['title'][:80]}")
            print(f"     Source: {article['source']} | Date: {article['date']}")
            print(f"     Sentiment: {article.get('sentiment', 'N/A')}")
    else:
        print("\n⚠ No articles found!")
        print("Possible reasons:")
        print("  - Network connectivity issues")
        print("  - Website structure changed")
        print("  - Rate limiting")
    
    print(f"\n✓ US macro news fetch {'SUCCESSFUL' if us_news['article_count'] > 0 else 'COMPLETED (no articles)'}")
    
except Exception as e:
    print(f"\n✗ US macro news fetch FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Initialize monitor for ASX market
print("\n[TEST 5] Initializing MacroNewsMonitor for ASX market...")
try:
    asx_monitor = MacroNewsMonitor(market='ASX')
    print("✓ ASX MacroNewsMonitor initialized")
except Exception as e:
    print(f"✗ Failed to initialize ASX monitor: {e}")
    sys.exit(1)

# Test 6: Test ASX macro news fetching
print("\n[TEST 6] Fetching ASX macro news (RBA)...")
print("This may take 10-20 seconds due to respectful scraping delays...\n")
try:
    asx_news = asx_monitor.get_macro_sentiment()
    
    print("\n" + "="*80)
    print("ASX MACRO NEWS RESULTS")
    print("="*80)
    print(f"Articles Found: {asx_news['article_count']}")
    print(f"Sentiment Score: {asx_news['sentiment_score']:.3f} (-1=bearish, +1=bullish)")
    print(f"Sentiment Label: {asx_news['sentiment_label']}")
    
    if asx_news['article_count'] > 0:
        print(f"\nRecent Headlines:")
        for i, article in enumerate(asx_news['articles'][:5], 1):
            print(f"  {i}. {article['title'][:80]}")
            print(f"     Source: {article['source']} | Date: {article['date']}")
            print(f"     Sentiment: {article.get('sentiment', 'N/A')}")
    else:
        print("\n⚠ No articles found!")
        print("Possible reasons:")
        print("  - Network connectivity issues")
        print("  - Website structure changed")
        print("  - Rate limiting")
    
    print(f"\n✓ ASX macro news fetch {'SUCCESSFUL' if asx_news['article_count'] > 0 else 'COMPLETED (no articles)'}")
    
except Exception as e:
    print(f"\n✗ ASX macro news fetch FAILED: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)

if 'us_news' in locals() and 'asx_news' in locals():
    total_articles = us_news['article_count'] + asx_news['article_count']
    if total_articles > 0:
        print("✓ Macro news monitoring is WORKING")
        print(f"  US articles: {us_news['article_count']}")
        print(f"  ASX articles: {asx_news['article_count']}")
        print(f"  Total: {total_articles}")
        print("\nThe pipelines should show macro news data!")
    else:
        print("⚠ Macro news monitoring is NOT WORKING")
        print("  No articles fetched from any source")
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Try accessing federalreserve.gov and rba.gov.au in your browser")
        print("  3. Check if you're behind a firewall/proxy")
        print("  4. Look for error messages above")
else:
    print("✗ Tests failed before completion")
    print("  Check error messages above")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
