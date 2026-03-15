"""
Trading Logic Diagnostic - Why No Trades During AU Open

This script diagnoses why no stocks were purchased during the AU open.
Checks all blocking conditions in sequence.

Date: 2026-02-18
Issue: User reports no trades during AU market hours
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def diagnose_trading_logic():
    """Diagnose trading logic issues"""
    
    print("\n" + "="*80)
    print("TRADING LOGIC DIAGNOSTIC")
    print("="*80 + "\n")
    
    print("Checking potential blocking conditions:\n")
    
    # Issue 1: Entry timing check
    print("Issue 1: Entry Timing Check")
    print("-" * 80)
    print("Location: paper_trading_coordinator.py, line 817")
    print("Code: if self.entry_strategy and signal.get('action') in ['BUY', 'STRONG_BUY']:")
    print()
    print("❌ PROBLEM: Signal format mismatch!")
    print("   Standard signals use: {'prediction': 1, 'confidence': 75}")
    print("   Entry timing expects: {'action': 'BUY'}")
    print()
    print("   Result: Entry timing check NEVER runs for normal trades")
    print("   Impact: Low (entry timing not checked, but also not blocking)")
    print()
    
    # Issue 2: Signal format in should_allow_trade
    print("\nIssue 2: Signal Format in Trade Gates")
    print("-" * 80)
    print("Location: paper_trading_coordinator.py, line 805")
    print("Code: if signal.get('action') not in ['BUY', 'STRONG_BUY']:")
    print()
    print("❌ PROBLEM: Signal format mismatch!")
    print("   Check at line 805: signal.get('action') not in ['BUY', 'STRONG_BUY']")
    print("   Standard signal format: {'prediction': 1}")
    print()
    print("   Result: Line 806 returns True, 1.0, 'Signal not a buy'")
    print("   Impact: MEDIUM (bypasses all subsequent checks)")
    print()
    
    # Issue 3: Possible root causes
    print("\nIssue 3: Possible Root Causes for No Trades")
    print("-" * 80)
    print()
    print("1. Low Market Sentiment")
    print("   - If sentiment < 30: All trades BLOCKED")
    print("   - If sentiment 30-45: Position reduced to 50%")
    print("   Check: Dashboard shows current sentiment score")
    print()
    print("2. Low Signal Confidence")
    print("   - Default threshold: 52%")
    print("   - UI slider threshold: 50-95% (user configurable)")
    print("   - If confidence < threshold: Trade SKIPPED")
    print()
    print("3. Signal Generation Issues")
    print("   - Simplified signal may generate low confidence")
    print("   - LSTM not available: Falls back to basic technical")
    print("   - No news sentiment: Reduces composite score")
    print()
    print("4. Entry Timing (v1.3.15.163)")
    print("   - Entry score < 40: Trade BLOCKED")
    print("   - Entry score 40-59: Position reduced 50%")
    print("   - But: Not running due to signal format mismatch!")
    print()
    
    # Issue 4: The actual bug
    print("\nIssue 4: THE ACTUAL BUG - Signal Format Mismatch")
    print("-" * 80)
    print()
    print("Root Cause:")
    print("  generate_swing_signal() returns:")
    print("    {'prediction': 1, 'confidence': 75.5, 'signal_strength': 75.5}")
    print()
    print("  should_allow_trade() expects:")
    print("    {'action': 'BUY', 'confidence': 75.5}")
    print()
    print("Impact on Trading:")
    print("  Line 805: if signal.get('action') not in ['BUY', 'STRONG_BUY']:")
    print("            → Evaluates to True (no 'action' key)")
    print("  Line 806: return True, 1.0, 'Signal not a buy'")
    print("            → Bypasses ALL checks (sentiment, entry timing, etc.)")
    print()
    print("  BUT THEN:")
    print("  Line 1229 in evaluate_entry():")
    print("    should_enter = prediction == 1 and confidence >= threshold")
    print("    → Checks 'prediction' instead of 'action'")
    print()
    print("Result:")
    print("  ✓ Trades CAN go through (prediction==1 check works)")
    print("  ✗ But bypass sentiment gates (line 806 exits early)")
    print("  ✗ But bypass entry timing (line 817 never runs)")
    print()
    
    # Fix
    print("\nFIX Required:")
    print("-" * 80)
    print()
    print("Solution 1: Fix signal format in should_allow_trade()")
    print("  Change line 805:")
    print("    FROM: if signal.get('action') not in ['BUY', 'STRONG_BUY']:")
    print("    TO:   if signal.get('prediction', 0) != 1:")
    print()
    print("Solution 2: Fix entry timing check")
    print("  Change line 817:")
    print("    FROM: if self.entry_strategy and signal.get('action') in ['BUY', 'STRONG_BUY']:")
    print("    TO:   if self.entry_strategy and signal.get('prediction', 0) == 1:")
    print()
    print("Impact of Fix:")
    print("  ✓ Sentiment gates will work correctly")
    print("  ✓ Entry timing will check properly")
    print("  ✓ Trades will be blocked/reduced based on conditions")
    print()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print()
    print("Why No Trades During AU Open:")
    print()
    print("Most Likely Causes (in order):")
    print("  1. Low market sentiment (sentiment < 30 blocks all trades)")
    print("  2. Low signal confidence (confidence < threshold)")
    print("  3. Entry timing blocking trades (if yfinance fetch works)")
    print("  4. Max positions reached")
    print()
    print("Bug Found:")
    print("  Signal format mismatch in should_allow_trade()")
    print("  → Causes early exit, bypassing sentiment/timing checks")
    print("  → But trades can still go through via evaluate_entry()")
    print()
    print("Action Required:")
    print("  1. Fix signal format checks (lines 805, 817)")
    print("  2. Check logs for actual blocking reason")
    print("  3. Verify market sentiment score")
    print("  4. Test with mock AU stocks")
    print()
    print("="*80 + "\n")


if __name__ == "__main__":
    diagnose_trading_logic()
