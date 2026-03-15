#!/usr/bin/env python3
"""
Diagnostic: Check why UK stocks aren't trading
Analyzes current market conditions and trading gates
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import yfinance as yf

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*80)
print("UK TRADING CONDITIONS DIAGNOSTIC")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S GMT')}")
print()

# Test 1: Check UK pipeline report
print("Test 1: UK Pipeline Report")
print("-"*80)
report_path = project_root / "reports/screening/uk_morning_report.json"
if report_path.exists():
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    print(f"[OK] Report exists: {report_path}")
    
    if 'opportunities' in report:
        opps = report['opportunities']
        print(f"  Total opportunities: {len(opps)}")
        
        if opps:
            print(f"\n  Top 5 UK stocks from pipeline:")
            for i, opp in enumerate(opps[:5], 1):
                symbol = opp.get('symbol', 'UNKNOWN')
                score = opp.get('opportunity_score', 0)
                conf = opp.get('confidence', 0)
                pred = opp.get('prediction', 'UNKNOWN')
                sentiment = opp.get('finbert_sentiment', {})
                sent_score = sentiment.get('compound', 0) if isinstance(sentiment, dict) else 0
                
                print(f"    {i}. {symbol}: Score={score:.1f}, Confidence={conf:.1f}%, "
                      f"Prediction={pred}, Sentiment={sent_score:.2f}")
        else:
            print("  ⚠ No opportunities in report")
    
    if 'market_sentiment' in report:
        sent = report['market_sentiment']
        print(f"\n  Market Sentiment:")
        print(f"    Overall: {sent.get('overall_sentiment', 'N/A')}")
        print(f"    Sentiment Index: {sent.get('sentiment_index', 0):.1f}")
        print(f"    Recommendation: {sent.get('recommendation', 'N/A')}")
else:
    print(f"✗ Report not found: {report_path}")

print()

# Test 2: Check FTSE market performance
print("Test 2: FTSE Market Performance")
print("-"*80)
try:
    ftse = yf.Ticker("^FTSE")
    hist = ftse.history(period="1d", interval="15m")
    
    if not hist.empty:
        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[0]
        change_pct = ((current_price - open_price) / open_price) * 100
        
        print(f"^FTSE Current Status:")
        print(f"  Open: {open_price:.2f}")
        print(f"  Current: {current_price:.2f}")
        print(f"  Change: {change_pct:+.2f}%")
        
        if change_pct < -0.5:
            print(f"  Status: 🔴 DECLINING (>{change_pct:.2f}%)")
        elif change_pct < 0:
            print(f"  Status: 🟡 SLIGHTLY DOWN ({change_pct:.2f}%)")
        elif change_pct < 0.5:
            print(f"  Status: 🟢 SLIGHTLY UP (+{change_pct:.2f}%)")
        else:
            print(f"  Status: 🟢 RISING (+{change_pct:.2f}%)")
    else:
        print("✗ No FTSE data available")
except Exception as e:
    print(f"✗ Error fetching FTSE: {e}")

print()

# Test 3: Check trading gates
print("Test 3: Trading Gates Analysis")
print("-"*80)

# Load screening config for thresholds
config_path = project_root / "config/screening_config.json"
if config_path.exists():
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Get sentiment thresholds
    sentiment_config = config.get('sentiment_integration', {})
    min_sentiment = sentiment_config.get('min_sentiment_for_trade', 30)
    
    print(f"Sentiment Gate:")
    print(f"  Minimum sentiment required: {min_sentiment}")
    print(f"  Block if sentiment < {min_sentiment}")
    print(f"  Reduce position (50%) if sentiment 30-45")
    print(f"  Normal position if sentiment 45-55")
    print(f"  Increase position if sentiment > 55")
    
    # Get confidence threshold
    min_confidence = sentiment_config.get('min_confidence', 52.0)
    print(f"\nConfidence Gate:")
    print(f"  Minimum confidence required: {min_confidence}%")
    
    # Entry timing gates
    print(f"\nEntry Timing Gates (v1.3.15.163):")
    print(f"  Score 80-100: IMMEDIATE_BUY (full position)")
    print(f"  Score 60-79:  GOOD_ENTRY (full position)")
    print(f"  Score 40-59:  WAIT_FOR_DIP (50% position)")
    print(f"  Score 0-39:   DONT_BUY (blocked)")
    
else:
    print("✗ Config not found")

print()

# Test 4: Simulate a UK stock evaluation
print("Test 4: Example UK Stock Evaluation (LLOY.L)")
print("-"*80)
try:
    ticker = yf.Ticker("LLOY.L")
    hist = ticker.history(period="3mo", interval="1d")
    
    if not hist.empty:
        current = hist['Close'].iloc[-1]
        ma20 = hist['Close'].tail(20).mean()
        ma50 = hist['Close'].tail(50).mean()
        high_20 = hist['High'].tail(20).max()
        
        pullback_pct = ((high_20 - current) / high_20) * 100
        dist_ma20 = ((current - ma20) / ma20) * 100
        dist_ma50 = ((current - ma50) / ma50) * 100
        
        print(f"LLOY.L Technical Analysis:")
        print(f"  Current Price: £{current:.3f}")
        print(f"  20-day MA: £{ma20:.3f} (price is {dist_ma20:+.1f}% from MA20)")
        print(f"  50-day MA: £{ma50:.3f} (price is {dist_ma50:+.1f}% from MA50)")
        print(f"  20-day High: £{high_20:.3f}")
        print(f"  Pullback: {pullback_pct:.1f}% from 20-day high")
        
        # Entry timing assessment
        print(f"\n  Entry Timing Assessment:")
        if pullback_pct > 2.0 and dist_ma20 < 0:
            print(f"    [OK] Good pullback ({pullback_pct:.1f}%)")
            print(f"    [OK] Below MA20 (potential support)")
            print(f"    → Entry Score: ~60-70 (GOOD_ENTRY or WAIT_FOR_DIP)")
        elif pullback_pct < 1.0 and dist_ma20 > 2.0:
            print(f"    ⚠ Small pullback ({pullback_pct:.1f}%)")
            print(f"    ⚠ Extended above MA20 (+{dist_ma20:.1f}%)")
            print(f"    → Entry Score: ~40-50 (WAIT_FOR_DIP)")
        else:
            print(f"    → Entry Score: ~50-60 (NEUTRAL)")
        
except Exception as e:
    print(f"✗ Error analyzing LLOY.L: {e}")

print()

# Test 5: Check if trading is actually running
print("Test 5: Trading System Status")
print("-"*80)
state_path = project_root / "state/paper_trading_state.json"
if state_path.exists():
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    symbols = state.get('symbols', [])
    capital = state.get('capital', {})
    positions = state.get('positions', {})
    
    print(f"[OK] Trading state exists")
    print(f"  Symbols loaded: {len(symbols)} ({', '.join(symbols[:5])}...)")
    print(f"  Total capital: ${capital.get('total', 0):,.2f}")
    print(f"  Open positions: {len(positions)}")
    
    if len(symbols) == 0:
        print(f"\n  ⚠ NO SYMBOLS LOADED - Trading cannot start")
        print(f"    → Use 'Auto-Load Top 50' button or manually enter symbols")
    elif capital.get('total', 0) == 0:
        print(f"\n  ⚠ NO CAPITAL SET - Trading cannot start")
        print(f"    → Set initial capital in dashboard")
    else:
        print(f"\n  [OK] System ready to trade")
else:
    print(f"✗ Trading state not found")
    print(f"  → Trading system not started")
    print(f"  → Start dashboard and click 'Start Trading'")

print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)

print("\nPossible reasons for no UK trades:")
print("  1. Trading system not started (no symbols/capital loaded)")
print("  2. FTSE market declining → waiting for reversal/pullback")
print("  3. UK stocks above entry timing threshold (waiting for dip)")
print("  4. Low market sentiment (< 30) → blocking all trades")
print("  5. Low individual stock confidence (< 52%) → blocking trades")
print("  6. Signal format mismatch (fixed in v1.3.15.165)")

print("\nRecommended actions:")
print("  1. Check if 'Start Trading' was clicked in dashboard")
print("  2. Verify symbols are loaded (use Auto-Load Top 50)")
print("  3. Check dashboard logs for [BLOCK], [REDUCE], [OK] messages")
print("  4. Monitor FTSE - system may be waiting for market reversal")
print("  5. Check Force Buy logs - manually test a UK stock")

print("\n" + "="*80)
