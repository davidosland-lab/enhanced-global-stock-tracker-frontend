#!/usr/bin/env python3
"""
Test script for Bank of England RSS scraper
Version: v1.3.15.43
Purpose: Independently test BoE RSS feed scraping without running full pipeline
"""

import sys
from datetime import datetime

def test_feedparser_installation():
    """Test if feedparser is installed"""
    print("\n" + "="*70)
    print("  Bank of England RSS Scraper - Standalone Test")
    print("  Version: v1.3.15.43")
    print("="*70 + "\n")
    
    print("[Test 1/4] Checking feedparser installation...")
    try:
        import feedparser
        print(f"  ✓ feedparser {feedparser.__version__} is installed")
        return True
    except ImportError:
        print("  ✗ feedparser is NOT installed")
        print("\n  To install:")
        print("    pip install feedparser")
        return False

def test_rss_feed_access():
    """Test direct RSS feed access"""
    print("\n[Test 2/4] Testing RSS feed access...")
    try:
        import feedparser
        feed_url = 'https://www.bankofengland.co.uk/news.rss'
        print(f"  Fetching: {feed_url}")
        
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            print("  ✗ No entries found in RSS feed")
            return False
        
        print(f"  ✓ Successfully retrieved {len(feed.entries)} articles")
        return True
        
    except Exception as e:
        print(f"  ✗ Error accessing RSS feed: {e}")
        return False

def test_article_parsing():
    """Test article parsing and filtering"""
    print("\n[Test 3/4] Testing article parsing and filtering...")
    try:
        import feedparser
        feed = feedparser.parse('https://www.bankofengland.co.uk/news.rss')
        
        relevant_keywords = [
            'interest rate', 'bank rate', 'monetary policy', 
            'inflation', 'mpc', 'committee', 'andrew bailey',
            'governor', 'financial stability', 'economic outlook',
            'quantitative', 'gilt', 'forecast', 'decision'
        ]
        
        relevant_articles = []
        for entry in feed.entries[:10]:
            title = entry.get('title', '').strip()
            summary = entry.get('summary', '')
            text = f"{title} {summary}".lower()
            
            is_relevant = any(kw in text for kw in relevant_keywords)
            if is_relevant:
                relevant_articles.append(title)
        
        print(f"  ✓ Found {len(relevant_articles)} relevant articles")
        return len(relevant_articles) > 0
        
    except Exception as e:
        print(f"  ✗ Error parsing articles: {e}")
        return False

def test_display_sample_articles():
    """Display sample articles"""
    print("\n[Test 4/4] Sample articles from BoE RSS feed:")
    try:
        import feedparser
        feed = feedparser.parse('https://www.bankofengland.co.uk/news.rss')
        
        relevant_keywords = [
            'interest rate', 'bank rate', 'monetary policy', 
            'inflation', 'mpc', 'committee', 'andrew bailey',
            'governor', 'financial stability', 'economic outlook',
            'quantitative', 'gilt', 'forecast', 'decision'
        ]
        
        count = 0
        for entry in feed.entries[:10]:
            title = entry.get('title', '').strip()
            url = entry.get('link', '')
            published = entry.get('published', 'N/A')
            summary = entry.get('summary', '')
            
            text = f"{title} {summary}".lower()
            is_relevant = any(kw in text for kw in relevant_keywords)
            
            if is_relevant and count < 5:
                count += 1
                print(f"\n  Article {count}:")
                print(f"    Title: {title[:70]}")
                print(f"    URL: {url}")
                print(f"    Published: {published}")
                if summary:
                    print(f"    Summary: {summary[:100]}...")
        
        if count == 0:
            print("  (No relevant articles found in top 10)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error displaying articles: {e}")
        return False

def main():
    """Run all tests"""
    results = []
    
    # Test 1: feedparser installation
    results.append(("feedparser installation", test_feedparser_installation()))
    
    if not results[0][1]:
        print("\n" + "="*70)
        print("  STOPPED: feedparser is not installed")
        print("  Run: pip install feedparser")
        print("="*70)
        return False
    
    # Test 2: RSS feed access
    results.append(("RSS feed access", test_rss_feed_access()))
    
    # Test 3: Article parsing
    results.append(("Article parsing", test_article_parsing()))
    
    # Test 4: Display samples
    results.append(("Sample articles", test_display_sample_articles()))
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  ✓ ALL TESTS PASSED")
        print("\n  The BoE RSS scraper should work correctly in the pipeline.")
        print("  Run the UK pipeline to see BoE articles in the macro news section.")
    else:
        print("\n  ✗ SOME TESTS FAILED")
        print("\n  Troubleshooting:")
        print("    1. Install feedparser: pip install feedparser")
        print("    2. Check internet connection")
        print("    3. Verify firewall/proxy settings")
    
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
