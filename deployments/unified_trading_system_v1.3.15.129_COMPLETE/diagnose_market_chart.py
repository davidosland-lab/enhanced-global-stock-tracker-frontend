"""
Market Performance Chart Diagnostic

Tests why the 24hr market performance graph is not showing data
during UK market hours (London has been open 35+ minutes).

Checks:
1. yfinance data fetch for ^FTSE
2. Timezone handling
3. Market hours filtering
4. Data point generation

Date: 2026-02-19
Issue: No plot on 24hr market performance graph during UK open
"""

import yfinance as yf
from datetime import datetime, timedelta
import pytz
import pandas as pd

def diagnose_market_chart():
    """Diagnose market performance chart issues"""
    
    print("\n" + "="*80)
    print("MARKET PERFORMANCE CHART DIAGNOSTIC")
    print("="*80 + "\n")
    
    # Setup
    gmt = pytz.timezone('GMT')
    current_time_gmt = datetime.now(gmt)
    
    print(f"Current Time (GMT): {current_time_gmt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Day of week: {current_time_gmt.strftime('%A')}")
    print()
    
    # Check UK market hours
    print("UK Market (FTSE) Expected Hours:")
    print("-" * 80)
    print("Market Open:  08:00 GMT")
    print("Market Close: 16:30 GMT")
    print()
    
    uk_open = current_time_gmt.replace(hour=8, minute=0, second=0, microsecond=0)
    uk_close = current_time_gmt.replace(hour=16, minute=30, second=0, microsecond=0)
    
    if uk_open <= current_time_gmt <= uk_close:
        minutes_since_open = (current_time_gmt - uk_open).seconds // 60
        print(f"✓ UK Market is OPEN (opened {minutes_since_open} minutes ago)")
    else:
        print(f"✗ UK Market is CLOSED")
    print()
    
    # Test yfinance fetch for FTSE
    print("Test 1: Fetch ^FTSE Data")
    print("-" * 80)
    
    try:
        ticker = yf.Ticker('^FTSE')
        print(f"Fetching 5 days of 15-minute interval data...")
        hist = ticker.history(period='5d', interval='15m')
        
        if hist.empty:
            print("❌ PROBLEM: No data returned from yfinance!")
            print("   Possible causes:")
            print("   - yfinance API issue")
            print("   - Yahoo Finance data delay")
            print("   - Symbol ^FTSE not available")
            print()
            return
        
        print(f"✓ Fetched {len(hist)} data points")
        print(f"  Date range: {hist.index[0].date()} to {hist.index[-1].date()}")
        print(f"  Time range: {hist.index[0].time()} to {hist.index[-1].time()}")
        print()
        
        # Check latest data
        latest_time = hist.index[-1]
        latest_price = hist['Close'].iloc[-1]
        time_since_latest = current_time_gmt - latest_time.tz_convert(gmt)
        minutes_ago = time_since_latest.seconds // 60
        
        print(f"Latest Data Point:")
        print(f"  Time: {latest_time.tz_convert(gmt).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Price: {latest_price:.2f}")
        print(f"  Age: {minutes_ago} minutes ago")
        print()
        
        if minutes_ago > 30:
            print(f"⚠️  WARNING: Latest data is {minutes_ago} minutes old!")
            print(f"   Expected: Data within last 15-20 minutes for active market")
            print()
        
    except Exception as e:
        print(f"❌ ERROR fetching data: {e}")
        print()
        return
    
    # Test 24-hour window
    print("\nTest 2: Apply 24-Hour Window Filter")
    print("-" * 80)
    
    # Convert to GMT
    hist.index = hist.index.tz_convert(gmt)
    
    # 24-hour cutoff
    cutoff_time = current_time_gmt - timedelta(hours=24)
    hist_24h = hist[hist.index >= cutoff_time]
    
    print(f"24-hour cutoff: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Data points in last 24h: {len(hist_24h)}")
    print()
    
    if len(hist_24h) == 0:
        print("❌ PROBLEM: No data in last 24 hours!")
        print("   This would cause empty graph")
        print()
        return
    
    # Test market hours filter
    print("\nTest 3: Apply Market Hours Filter")
    print("-" * 80)
    
    market_open_hour = 8
    market_close_hour = 16
    
    # Create market hours filter
    mask = (
        (hist_24h.index.hour >= market_open_hour) &
        (hist_24h.index.hour <= market_close_hour)
    )
    
    market_hours_data = hist_24h[mask]
    
    print(f"Market hours (08:00-16:30): {len(market_hours_data)} data points")
    print()
    
    if len(market_hours_data) == 0:
        print("❌ PROBLEM: No data during market hours!")
        print("   Possible causes:")
        print("   - Market hasn't started yet today")
        print("   - Market closed (holiday)")
        print("   - No trading data in yfinance for today")
        print()
        
        # Show what hours we DO have data for
        if len(hist_24h) > 0:
            hours_with_data = hist_24h.index.hour.unique()
            print(f"Hours with data in last 24h: {sorted(hours_with_data)}")
            print()
        
        return
    
    # Test percentage calculation
    print("\nTest 4: Calculate Percentage Changes")
    print("-" * 80)
    
    try:
        # Get previous close
        ticker_info = ticker.info
        previous_close = ticker_info.get('regularMarketPreviousClose', 
                                        ticker_info.get('previousClose'))
        
        if not previous_close:
            previous_close = market_hours_data['Close'].iloc[0]
            print(f"Using session open as reference: {previous_close:.2f}")
        else:
            print(f"Using official previous close: {previous_close:.2f}")
        
        print()
        
        # Calculate percentage changes
        pct_changes = ((market_hours_data['Close'] - previous_close) / previous_close) * 100
        
        print(f"Percentage changes calculated: {len(pct_changes)} points")
        print(f"  Min change: {pct_changes.min():.2f}%")
        print(f"  Max change: {pct_changes.max():.2f}%")
        print(f"  Latest change: {pct_changes.iloc[-1]:.2f}%")
        print()
        
        # Show first few and last few points
        print("First 3 data points:")
        for idx in range(min(3, len(market_hours_data))):
            time = market_hours_data.index[idx]
            price = market_hours_data['Close'].iloc[idx]
            pct = pct_changes.iloc[idx]
            print(f"  {time.strftime('%H:%M')}: {price:.2f} ({pct:+.2f}%)")
        
        print()
        print("Last 3 data points:")
        for idx in range(max(0, len(market_hours_data) - 3), len(market_hours_data)):
            time = market_hours_data.index[idx]
            price = market_hours_data['Close'].iloc[idx]
            pct = pct_changes.iloc[idx]
            print(f"  {time.strftime('%H:%M')}: {price:.2f} ({pct:+.2f}%)")
        
        print()
        
    except Exception as e:
        print(f"❌ ERROR calculating percentages: {e}")
        print()
        return
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print()
    
    if len(market_hours_data) > 0:
        print("✓ Data is available for ^FTSE")
        print(f"✓ {len(market_hours_data)} data points during market hours")
        print(f"✓ Percentage changes calculated successfully")
        print()
        print("VERDICT: Chart should display correctly")
        print()
        print("If chart still not showing:")
        print("  1. Check dashboard callback is running (look for [DASHBOARD] logs)")
        print("  2. Check browser console for JavaScript errors")
        print("  3. Try hard refresh (Ctrl+F5)")
        print("  4. Check if trading system is started")
    else:
        print("❌ No data available for chart")
        print()
        print("Most likely cause: Market data not yet available in yfinance")
        print("  - yfinance may have 15-20 minute delay")
        print("  - Data may not be available until more trading occurs")
        print()
        print("ACTION: Wait 10-15 more minutes and try again")
    
    print()
    print("="*80 + "\n")


if __name__ == "__main__":
    diagnose_market_chart()
