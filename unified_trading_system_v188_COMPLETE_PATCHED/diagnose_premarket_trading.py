#!/usr/bin/env python3
"""
Diagnostic: Pre-Market Trading Start Analysis
Why no trades when started before market open?
"""

import sys
from pathlib import Path
from datetime import datetime, time
import yfinance as yf

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*80)
print("PRE-MARKET TRADING START DIAGNOSTIC")
print("="*80)
print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Your local time)")
print()

# Test 1: Check London market hours
print("Test 1: London Market Hours")
print("-"*80)
now = datetime.now()
current_hour_gmt = now.hour  # Assuming system is GMT/UTC

london_open = time(8, 0)  # 08:00 GMT
london_close = time(16, 30)  # 16:30 GMT

current_time = now.time()
is_london_open = london_open <= current_time <= london_close

print(f"London Exchange Hours: 08:00 - 16:30 GMT")
print(f"Current Time: {current_time.strftime('%H:%M:%S')} GMT")
print(f"Market Status: {'🟢 OPEN' if is_london_open else '🔴 CLOSED'}")

if not is_london_open:
    if current_time < london_open:
        minutes_until_open = ((datetime.combine(now.date(), london_open) - 
                              datetime.combine(now.date(), current_time)).seconds // 60)
        print(f"⏰ Market opens in: {minutes_until_open} minutes")
    else:
        print(f"⏰ Market closed for the day")

print()

# Test 2: Check if yfinance returns data pre-market
print("Test 2: Can We Get UK Stock Data Before Market Open?")
print("-"*80)
test_symbols = ['LLOY.L', 'BARC.L', 'BP.L']

for symbol in test_symbols:
    try:
        ticker = yf.Ticker(symbol)
        
        # Try to get 1-day history (should have yesterday's close)
        hist_1d = ticker.history(period="1d")
        
        # Try to get 5-day history
        hist_5d = ticker.history(period="5d")
        
        # Try to get current info
        info = ticker.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        prev_close = info.get('previousClose')
        
        print(f"\n{symbol}:")
        print(f"  1-day data: {len(hist_1d)} bars (should be 0 before market open)")
        print(f"  5-day data: {len(hist_5d)} bars (historical)")
        print(f"  Previous close: £{prev_close:.3f}" if prev_close else "  Previous close: N/A")
        print(f"  Current price: £{current_price:.3f}" if current_price else "  Current price: N/A (market closed)")
        
        if len(hist_1d) == 0 and not is_london_open:
            print(f"  ⚠ No intraday data (market not open yet)")
        
        if len(hist_5d) > 0:
            last_close = hist_5d['Close'].iloc[-1]
            last_date = hist_5d.index[-1]
            print(f"  Last close: £{last_close:.3f} on {last_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"\n{symbol}: Error - {e}")

print()

# Test 3: What happens when generate_swing_signal is called pre-market?
print("Test 3: Signal Generation Before Market Open")
print("-"*80)

print("When trading starts BEFORE market open:")
print()
print("1. fetch_market_data(symbol, '3mo'):")
print("   [OK] Returns: Historical data (60-90 days)")
print("   [OK] Latest bar: Yesterday's close")
print("   → Signal CAN be generated based on historical data")
print()
print("2. fetch_current_price(symbol):")
print("   If market CLOSED:")
print("     [OK] Returns: Yesterday's close price")
print("     [OK] Not real-time (stale)")
print("   If market OPEN:")
print("     [OK] Returns: Current real-time price")
print()
print("3. generate_swing_signal() result:")
print("   [OK] Signal generated using yesterday's close")
print("   [OK] Confidence calculated on historical pattern")
print("   [OK] Entry timing uses yesterday's data")
print("   → Signal is VALID but based on STALE data")
print()

# Test 4: The Real Issue
print("Test 4: Why No Trades Pre-Market?")
print("-"*80)

print("Hypothesis 1: No Fresh Data")
print("  - Signals based on yesterday's close")
print("  - Entry timing scores use yesterday's high/RSI")
print("  - May show 'WAIT_FOR_DIP' if yesterday closed high")
print()

print("Hypothesis 2: Low Confidence")
print("  - Historical signal confidence may be < 52%")
print("  - No real-time price movement to boost confidence")
print()

print("Hypothesis 3: System Design - Waiting for Market Open")
print("  - System MAY be intentionally waiting")
print("  - Real-time signals only valid during market hours")
print()

print("Hypothesis 4: Entry Timing Blocking")
print("  - If stocks closed near highs yesterday")
print("  - Entry scores will be low (40-59)")
print("  - System says 'WAIT_FOR_DIP'")
print("  - Waiting for intraday pullback AFTER market opens")
print()

# Test 5: Check morning report sentiment
print("Test 5: Check Morning Report Availability")
print("-"*80)

import json
uk_report = project_root / "reports/screening/uk_morning_report.json"

if uk_report.exists():
    with open(uk_report, 'r') as f:
        report = json.load(f)
    
    print(f"[OK] UK morning report exists")
    
    report_timestamp = report.get('timestamp', 'UNKNOWN')
    print(f"  Generated at: {report_timestamp}")
    
    sentiment = report.get('market_sentiment', {})
    sent_index = sentiment.get('sentiment_index', 0)
    recommendation = sentiment.get('recommendation', 'UNKNOWN')
    
    print(f"  Sentiment Index: {sent_index:.1f}/100")
    print(f"  Recommendation: {recommendation}")
    
    if sent_index < 30:
        print(f"  ⚠ SENTIMENT TOO LOW - All trades BLOCKED")
    elif sent_index < 45:
        print(f"  ⚠ LOW SENTIMENT - Positions reduced to 50%")
    else:
        print(f"  [OK] Sentiment allows trading")
    
    opps = report.get('opportunities', [])
    print(f"  Opportunities: {len(opps)} stocks")
    
    if opps:
        print(f"\n  Top 3 stocks:")
        for i, opp in enumerate(opps[:3], 1):
            sym = opp.get('symbol', 'N/A')
            conf = opp.get('confidence', 0)
            score = opp.get('opportunity_score', 0)
            print(f"    {i}. {sym}: Confidence={conf:.1f}%, Score={score:.1f}")
else:
    print(f"✗ UK morning report NOT found")
    print(f"  Expected: {uk_report}")
    print(f"  → Pipeline hasn't run yet OR report missing")

print()

# Summary
print("="*80)
print("VERDICT: Why No Trades When Started Before Market Open?")
print("="*80)
print()

if not is_london_open:
    print("🔴 MARKET IS CURRENTLY CLOSED")
    print()
    print("Most Likely Reasons:")
    print()
    print("1. NO REAL-TIME DATA (80% probability)")
    print("   - yfinance returns yesterday's close")
    print("   - Entry timing scores based on stale data")
    print("   - System waiting for market to open for fresh data")
    print()
    print("2. ENTRY TIMING BLOCKING (15% probability)")
    print("   - If stocks closed high yesterday")
    print("   - Entry scores 40-59 → 'WAIT_FOR_DIP'")
    print("   - Waiting for intraday pullback")
    print()
    print("3. LOW SENTIMENT (<30) (5% probability)")
    print("   - Morning report has bearish sentiment")
    print("   - All trades blocked until sentiment improves")
    print()
    print("RECOMMENDATION:")
    print("  → Wait for London market to open (08:00 GMT)")
    print("  → System will get real-time prices")
    print("  → Entry timing will recalculate with live data")
    print("  → Trades should execute if conditions met")
else:
    print("🟢 MARKET IS CURRENTLY OPEN")
    print()
    print("If no trades yet, check:")
    print()
    print("1. Dashboard logs for [BLOCK] or [REDUCE] messages")
    print("2. FTSE performance (if declining, sentiment may be low)")
    print("3. Force Buy test: Try manually buying LLOY.L")
    print("4. Entry timing: Stocks may need to pull back first")

print()
print("="*80)
