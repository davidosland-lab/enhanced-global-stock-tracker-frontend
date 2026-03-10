"""
Diagnostic Test for World Event Risk Monitor v193.2
Test if articles are being analyzed correctly for Iran-Israel-US conflict
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from pipelines.models.screening.world_event_monitor import WorldEventMonitor
from pipelines.models.screening.macro_news_monitor import MacroNewsMonitor

print("="*80)
print("WORLD EVENT RISK DIAGNOSTIC TEST")
print("="*80)

# Test 1: World Event Monitor with test articles
print("\n[TEST 1] Testing World Event Monitor with Iran-Israel conflict articles...")
print("-"*80)

monitor = WorldEventMonitor()

test_articles = [
    {
        'title': 'Iran launches missile strikes on US military bases in response to Israeli attacks',
        'source': 'Reuters',
        'published': '2026-03-01'
    },
    {
        'title': 'Israel and Iran exchange fresh attacks as tensions escalate in Middle East',
        'source': 'BBC',
        'published': '2026-03-01'
    },
    {
        'title': 'US sends additional troops to Middle East amid Iran-Israel military conflict',
        'source': 'Reuters',
        'published': '2026-03-02'
    },
    {
        'title': 'Oil prices surge as Iran threatens to close Strait of Hormuz',
        'source': 'Bloomberg',
        'published': '2026-03-02'
    },
    {
        'title': 'NATO convenes emergency meeting on Iran-Israel war escalation',
        'source': 'AP',
        'published': '2026-03-03'
    }
]

risk_result = monitor.get_world_event_risk(test_articles)

print(f"\n[OK] World Risk Score: {risk_result['world_risk_score']:.1f}/100")
print(f"[OK] Risk Level: {risk_result['risk_level']}")
print(f"[OK] Fear Index: {risk_result['fear']:.2f}")
print(f"[OK] Anger Index: {risk_result['anger']:.2f}")
print(f"[OK] Negative Sentiment: {risk_result['neg_sent']:.2f}")
print(f"[OK] Top Topics: {', '.join(risk_result['top_topics'][:5])}")
print(f"[OK] Article Count: {risk_result['article_count']}")

if risk_result['world_risk_score'] < 70:
    print(f"\n[ERROR] FAIL: Expected risk score 85-90, got {risk_result['world_risk_score']:.1f}")
    print("   World Event Monitor may not be detecting crisis keywords correctly")
else:
    print(f"\n[OK] PASS: Crisis correctly detected (score: {risk_result['world_risk_score']:.1f})")

# Test 2: World Event Monitor with NO articles (neutral baseline)
print("\n[TEST 2] Testing World Event Monitor with NO articles (neutral baseline)...")
print("-"*80)

risk_neutral = monitor.get_world_event_risk([])

print(f"\n[OK] World Risk Score: {risk_neutral['world_risk_score']:.1f}/100")
print(f"[OK] Risk Level: {risk_neutral['risk_level']}")
print(f"[OK] Expected: 50/100 (MODERATE)")

if risk_neutral['world_risk_score'] != 50.0:
    print(f"\n[ERROR] FAIL: Expected 50.0, got {risk_neutral['world_risk_score']:.1f}")
else:
    print(f"\n[OK] PASS: Neutral baseline correct")

# Test 3: Macro News Monitor - Check if it's fetching articles
print("\n[TEST 3] Testing Macro News Monitor article fetching...")
print("-"*80)

print("\nAttempting to fetch ASX macro news (RBA + Global)...")
macro_monitor = MacroNewsMonitor(market='ASX')

try:
    macro_result = macro_monitor.get_macro_sentiment()
    
    print(f"\n[OK] Articles Fetched: {macro_result['article_count']}")
    print(f"[OK] Sentiment Score: {macro_result['sentiment_score']:.3f}")
    print(f"[OK] Sentiment Label: {macro_result['sentiment_label']}")
    
    if 'articles' in macro_result:
        print(f"\n[OK] Articles available in result: {len(macro_result['articles'])}")
        
        if len(macro_result['articles']) > 0:
            print("\nFirst 3 article titles:")
            for i, article in enumerate(macro_result['articles'][:3], 1):
                print(f"  {i}. {article['title'][:80]}")
            
            print(f"\n[OK] PASS: Macro News Monitor is fetching articles")
        else:
            print(f"\n[ERROR] FAIL: Articles list is empty")
            print("   Macro news scraper may be failing or being blocked")
    else:
        print(f"\n[ERROR] FAIL: No 'articles' key in result")
        print("   This explains why World Event Risk shows 13/100 (neutral)")
        
except Exception as e:
    print(f"\n[ERROR] FAIL: Macro News Monitor error: {e}")
    print("   This explains why World Event Risk is not working")

# Test 4: Check if articles have the 'articles' key structure
print("\n[TEST 4] Checking article structure in macro_news result...")
print("-"*80)

if 'articles' in macro_result and len(macro_result['articles']) > 0:
    first_article = macro_result['articles'][0]
    print(f"\nFirst article structure:")
    for key, value in first_article.items():
        if isinstance(value, str) and len(value) > 80:
            print(f"  {key}: {value[:80]}...")
        else:
            print(f"  {key}: {value}")
    print(f"\n[OK] Article structure looks correct")
else:
    print(f"\n[!]  Cannot check article structure (no articles fetched)")

# Summary
print("\n" + "="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)

print("\n1. World Event Monitor Algorithm:")
if risk_result['world_risk_score'] >= 70:
    print("   [OK] WORKING - Correctly detects crisis from articles")
else:
    print("   [ERROR] BROKEN - Not detecting crisis from test articles")
    
print("\n2. Neutral Baseline:")
if risk_neutral['world_risk_score'] == 50.0:
    print("   [OK] WORKING - Returns 50/100 when no articles")
else:
    print("   [ERROR] BROKEN - Not returning correct neutral value")

print("\n3. Macro News Fetching:")
if macro_result['article_count'] > 0:
    print(f"   [OK] WORKING - Fetched {macro_result['article_count']} articles")
else:
    print("   [ERROR] BROKEN - Not fetching any articles")

print("\n4. Article Structure:")
if 'articles' in macro_result:
    print(f"   [OK] CORRECT - 'articles' key present")
else:
    print(f"   [ERROR] MISSING - 'articles' key not in macro_result")

print("\n" + "="*80)
print("LIKELY ROOT CAUSE:")
print("="*80)

if macro_result['article_count'] == 0:
    print("""
The Macro News Monitor is failing to fetch articles from news sources.

Possible reasons:
1. Internet/firewall blocking news websites (Reuters, BBC)
2. News websites have changed their HTML structure
3. HTTP 401/403 errors (same as Yahoo Finance issue)
4. News scraper rate limiting

This explains why World Risk shows 13/100:
- No articles fetched -> empty list passed to World Event Monitor
- World Event Monitor returns low baseline (near 50)
- Small random variation -> 13/100 instead of exact 50

FIX:
Check your latest overnight pipeline log for:
- "Macro News Analysis" section
- "Articles Analyzed: N" (should be > 0)
- Any HTTP errors or scraping failures
""")
elif risk_result['world_risk_score'] < 70:
    print("""
The World Event Monitor algorithm may not be detecting crisis keywords.

Check the topic patterns in world_event_monitor.py:
- Military conflict keywords
- Iran/Israel/US keywords  
- Crisis severity scores

This is less likely since the keywords look correct in the code.
""")
else:
    print("""
[OK] Both components working correctly in isolation!

The issue must be in the overnight pipeline integration.
Check if articles are being passed correctly from Phase 1.3 to Phase 1.4.
""")

print("\n" + "="*80)
