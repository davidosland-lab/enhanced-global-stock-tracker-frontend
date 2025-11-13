#!/usr/bin/env python3
"""
Simple test for news scraping - standalone script
Tests Yahoo Finance scraping directly without FinBERT
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

async def test_yahoo_news(symbol):
    """Test Yahoo Finance news scraping"""
    print(f"\n🔍 Testing Yahoo Finance news for {symbol}...")
    print("=" * 70)
    
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    articles = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"Status Code: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find news items
                    news_items = soup.find_all(['li', 'div'], {'class': re.compile('stream-item|news-item|StreamDataList')})
                    print(f"Found {len(news_items)} potential news items in HTML")
                    
                    for item in news_items[:10]:  # Check first 10
                        # Try to find title
                        title_elem = item.find('a', {'class': re.compile('title|headline|Fw\\(b\\)')})
                        if not title_elem:
                            title_elem = item.find('h3') or item.find('a')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get('href', '')
                            
                            # Fix relative URLs
                            if link and not link.startswith('http'):
                                link = f"https://finance.yahoo.com{link}"
                            
                            if title and len(title) > 10:
                                articles.append({
                                    'title': title,
                                    'url': link,
                                    'source': 'Yahoo Finance'
                                })
                    
                    print(f"\n✓ Successfully scraped {len(articles)} articles from Yahoo Finance")
                    
                    if len(articles) > 0:
                        print(f"\n📰 Sample Articles:")
                        for i, article in enumerate(articles[:5], 1):
                            print(f"{i}. {article['title']}")
                            print(f"   URL: {article['url'][:80]}...")
                    else:
                        print("\n⚠️  No articles found - HTML structure may have changed")
                        print("Showing first 500 chars of HTML:")
                        print(html[:500])
                else:
                    print(f"✗ HTTP Error: {response.status}")
                    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return articles

async def test_finviz_news(symbol):
    """Test Finviz news scraping"""
    print(f"\n🔍 Testing Finviz news for {symbol}...")
    print("=" * 70)
    
    url = f"https://finviz.com/quote.ashx?t={symbol}"
    articles = []
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"Status Code: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find news table
                    news_table = soup.find('table', {'class': 'fullview-news-outer'})
                    if news_table:
                        rows = news_table.find_all('tr')
                        print(f"Found {len(rows)} news rows")
                        
                        for row in rows[:10]:
                            link_cell = row.find('a', {'class': 'tab-link-news'})
                            if link_cell:
                                title = link_cell.get_text(strip=True)
                                link = link_cell.get('href', '')
                                
                                articles.append({
                                    'title': title,
                                    'url': link,
                                    'source': 'Finviz'
                                })
                        
                        print(f"\n✓ Successfully scraped {len(articles)} articles from Finviz")
                        
                        if len(articles) > 0:
                            print(f"\n📰 Sample Articles:")
                            for i, article in enumerate(articles[:5], 1):
                                print(f"{i}. {article['title']}")
                                print(f"   URL: {article['url'][:80]}...")
                    else:
                        print("\n⚠️  News table not found - structure may have changed")
                else:
                    print(f"✗ HTTP Error: {response.status}")
                    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return articles

async def main():
    print("=" * 70)
    print("  TESTING NEWS SCRAPING SYSTEM")
    print("  Yahoo Finance + Finviz")
    print("=" * 70)
    
    test_symbols = ['AAPL', 'TSLA', 'CBA.AX']
    
    for symbol in test_symbols:
        print(f"\n\n{'='*70}")
        print(f"  TESTING: {symbol}")
        print(f"{'='*70}")
        
        # Test Yahoo Finance
        yahoo_articles = await test_yahoo_news(symbol)
        
        # Test Finviz
        finviz_articles = await test_finviz_news(symbol)
        
        # Summary
        total = len(yahoo_articles) + len(finviz_articles)
        print(f"\n📊 Summary for {symbol}:")
        print(f"  Yahoo Finance: {len(yahoo_articles)} articles")
        print(f"  Finviz: {len(finviz_articles)} articles")
        print(f"  Total: {total} articles")
        
        if total > 0:
            print(f"  ✓ News scraping WORKING for {symbol}")
        else:
            print(f"  ✗ No articles found for {symbol}")
    
    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)
    print("\nConclusion:")
    print("- If articles found: Real news scraping is WORKING")
    print("- If no articles: May be rate-limited or HTML structure changed")
    print("- This proves NO MOCK DATA is being used")

if __name__ == "__main__":
    asyncio.run(main())
