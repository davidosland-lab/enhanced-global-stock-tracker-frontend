"""
Test Market Entry Strategy with LGEN.L

This script tests the new entry timing logic that addresses:
"But if you buy at the top and then it falls that is not a good strategy"

For LGEN.L current situation:
- Price: GBP273.40 (down -0.68% today)
- RSI: 61.92 (neutral)
- Price above MA20 and MA50 (uptrend)
- Signal: BUY with 87/100 opportunity score

Question: Should we buy NOW or wait for better entry?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.market_entry_strategy import MarketEntryStrategy, create_entry_timing_report
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lgen_entry():
    """Test entry strategy for LGEN.L"""
    
    symbol = "LGEN.L"
    
    # Fetch price data
    logger.info(f"Fetching data for {symbol}...")
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='3mo')
    
    if hist.empty:
        logger.error(f"Could not fetch data for {symbol}")
        return
    
    logger.info(f"Fetched {len(hist)} days of data")
    
    # Create entry strategy
    entry_strategy = MarketEntryStrategy()
    
    # Simulate BUY signal
    signal = {
        'action': 'BUY',
        'confidence': 72.0,
        'opportunity_score': 87
    }
    
    # Evaluate entry timing
    entry_eval = entry_strategy.evaluate_entry_timing(
        symbol=symbol,
        price_data=hist,
        signal=signal
    )
    
    # Create report
    report = create_entry_timing_report(symbol, entry_eval, signal)
    
    # Print report
    print("\n" * 2)
    print(report)
    print("\n")
    
    # Save report
    report_file = Path(__file__).parent / "LGEN_L_ENTRY_TIMING_ANALYSIS.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Report saved to: {report_file}")
    
    # Summary
    entry_score = entry_eval['entry_score']
    entry_quality = entry_eval['entry_quality']
    current_price = entry_eval.get('current_price', 0)
    target_price = entry_eval.get('entry_price_target')
    
    print("=" * 80)
    print("TRADING DECISION:")
    print("=" * 80)
    
    if entry_quality == 'IMMEDIATE_BUY':
        print(f"[OK] BUY NOW at GBP{current_price:.2f}")
        print(f"   Entry Score: {entry_score:.0f}/100 - Excellent timing")
    elif entry_quality == 'GOOD_ENTRY':
        print(f"[OK] BUY at GBP{current_price:.2f}")
        print(f"   Entry Score: {entry_score:.0f}/100 - Good timing")
    elif entry_quality == 'WAIT_FOR_DIP':
        print(f"[WARN] WAIT for better entry")
        print(f"   Current: GBP{current_price:.2f}")
        print(f"   Target:  GBP{target_price:.2f} ({((target_price/current_price - 1) * 100):.1f}%)")
        print(f"   Entry Score: {entry_score:.0f}/100")
        print(f"   Reason: {entry_eval.get('wait_reason')}")
    else:
        print(f"[ALERT] DON'T BUY - Likely at top")
        print(f"   Entry Score: {entry_score:.0f}/100")
        print(f"   Wait for: GBP{target_price:.2f} ({((target_price/current_price - 1) * 100):.1f}%)")
    
    print("=" * 80)
    print()

if __name__ == "__main__":
    test_lgen_entry()
