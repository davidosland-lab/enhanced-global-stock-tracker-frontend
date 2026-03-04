"""
Analyze why financial stocks (BP.L, BOQ.AX, NAB.AX) were bought during risk-off conditions
"""

print("=" * 100)
print("ANALYSIS: WHY FINANCIALS WERE BOUGHT DURING RISK-OFF CONDITIONS")
print("=" * 100)

print("\n📊 DASHBOARD OBSERVATIONS:")
print("-" * 100)
print("✅ Portfolio Value: $99,443.94 (down -0.56%)")
print("✅ Open Positions: 3")
print("   - BP.L (BP): 38 shares @ $493.00 | P&L: +0.00%")
print("   - BOQ.AX (Bank of Queensland): 2179 shares @ $6.99 | P&L: -2.36%")  
print("   - NAB.AX (National Australia Bank): 259 shares @ $47.64 | P&L: -1.22%")
print("\n📉 FinBERT Sentiment: 33% Negative, 8% Neutral, 34% Positive")
print("   ⚠️ ASSESSMENT: 'Weak market sentiment (47/100, Risk: Moderate)'")

print("\n\n🌍 MARKET CONTEXT (from logs):")
print("-" * 100)
print("📍 Date: March 4, 2026 (~14:00-14:10 AEDT)")
print("📍 US Markets (March 3): CLOSED - but had SEVERE selloff:")
print("   - S&P 500 (^GSPC): -0.70% to -2.47% (intraday range)")
print("   - NASDAQ (^IXIC): -0.77% to -2.74% (intraday range)")
print("   - FTSE 100 (^FTSE): -1.44% to -3.41% (intraday range)")
print("\n📍 Current Market Sentiment: 53.7/100 (NEUTRAL)")
print("   - SPY component: 50.0")
print("   - VIX component: 59.3 (ELEVATED FEAR)")
print("\n📍 AU Morning Report (6.2 hours old):")
print("   - Overall Sentiment: 42.1/100 (HOLD) - WEAK")
print("   - World Risk Score: 100/100 (EXTREME) - Nuclear threat detected")
print("   - Recommendation: HOLD (cautious)")
print("   - ASX 200: Down -0.98%")

print("\n\n🎯 TRADING SIGNALS ANALYSIS:")
print("-" * 100)
print("\n1️⃣  BP.L (British Petroleum):")
print("   Signal: BUY (confidence=0.54)")
print("   Combined Score: 0.080")
print("   Breakdown:")
print("     - Sentiment: 0.000 (NEUTRAL - no FinBERT data)")
print("     - LSTM: 0.190 (BULLISH)")
print("     - Technical: 0.055 (SLIGHT BULLISH)")
print("     - Momentum: 0.054 (SLIGHT BULLISH)")
print("     - Volume: 0.500 (STRONG VOLUME)")
print("   ⚠️ WARNING: 'Insufficient data to train LSTM for BP.L'")
print("   📊 Current: $493.00 | P&L: 0.00%")

print("\n2️⃣  BOQ.AX (Bank of Queensland):")
print("   Signal: HOLD (confidence=0.50)")
print("   Combined Score: -0.011 (SLIGHTLY BEARISH)")
print("   Breakdown:")
print("     - Sentiment: 0.000 (NEUTRAL - no FinBERT data)")
print("     - LSTM: -0.031 (SLIGHT BEARISH)")
print("     - Technical: 0.049 (SLIGHT BULLISH)")
print("     - Momentum: -0.024 (SLIGHT BEARISH)")
print("     - Volume: -0.236 (WEAK VOLUME)")
print("   ⚠️ WARNING: 'Insufficient data to train LSTM for BOQ.AX'")
print("   📊 Entry: $6.99 | Current: $6.83 | P&L: -2.36%")

print("\n3️⃣  NAB.AX (National Australia Bank):")
print("   Signal: HOLD (confidence=0.50)")
print("   Combined Score: 0.045 (SLIGHT BULLISH)")
print("   Breakdown:")
print("     - Sentiment: 0.000 (NEUTRAL - no FinBERT data)")
print("     - LSTM: 0.148 (BULLISH)")
print("     - Technical: 0.147 (BULLISH)")
print("     - Momentum: -0.032 (SLIGHT BEARISH)")
print("     - Volume: 0.000 (NEUTRAL)")
print("   ⚠️ WARNING: 'Insufficient data to train LSTM for NAB.AX'")
print("   📊 Entry: $47.64 | Current: $47.06 | P&L: -1.22%")

print("\n\n🚨 CRITICAL PROBLEMS IDENTIFIED:")
print("=" * 100)

print("\n❌ PROBLEM #1: NO FINBERT SENTIMENT DATA")
print("-" * 100)
print("All three positions show 'Sentiment: 0.000'")
print("This means:")
print("  1. Stock-level news was NOT fetched or analyzed")
print("  2. No negative sentiment from US selloff was incorporated")
print("  3. Decision was made BLIND to macro risk")
print("\n💡 What SHOULD have happened:")
print("  - FinBERT should detect bearish US market sentiment")
print("  - Financial sector sentiment should be NEGATIVE (banks sensitive to market selloffs)")
print("  - Sentiment scores should be -0.30 to -0.50 (bearish)")

print("\n❌ PROBLEM #2: INSUFFICIENT LSTM TRAINING DATA")
print("-" * 100)
print("All three positions triggered warning: 'Insufficient data to train LSTM'")
print("This means:")
print("  1. LSTM predictor used FALLBACK logic (unreliable)")
print("  2. No pattern recognition from historical data")
print("  3. LSTM scores (0.190, -0.031, 0.148) are QUESTIONABLE")
print("\n💡 What SHOULD have happened:")
print("  - Require minimum 60+ days of data for LSTM training")
print("  - Reject signals with insufficient data during high-risk periods")

print("\n❌ PROBLEM #3: IGNORED WORLD EVENT RISK")
print("-" * 100)
print("AU Morning Report shows:")
print("  - World Risk: 100/100 (EXTREME)")
print("  - Topic: 'nuclear_threat'")
print("  - Overall Sentiment: 42.1/100 (HOLD)")
print("\n❌ But trading system STILL bought financials!")
print("\n💡 What SHOULD have happened:")
print("  - When World Risk > 80/100 → NO NEW POSITIONS")
print("  - Or reduce position size by 50-75%")
print("  - Or require 80%+ confidence for any buys")

print("\n❌ PROBLEM #4: IGNORED US MARKET CONTEXT")
print("-" * 100)
print("US markets had SEVERE selloff on March 3:")
print("  - S&P 500: -2.47% (worst intraday)")
print("  - NASDAQ: -2.74% (worst intraday)")
print("  - FTSE: -3.41% (worst intraday)")
print("\n❌ But AU trading system opened NEW financial positions next day!")
print("\n💡 What SHOULD have happened:")
print("  - Check overnight US performance BEFORE buying")
print("  - If US down >1.5% → defensive mode (no financials)")
print("  - ASX typically follows US market direction with 1-day lag")

print("\n❌ PROBLEM #5: LOW CONFIDENCE SIGNALS ACCEPTED")
print("-" * 100)
print("Signal confidence levels:")
print("  - BP.L: 0.54 (54%) ← MARGINAL")
print("  - BOQ.AX: 0.50 (50%) ← NEUTRAL/WEAK")
print("  - NAB.AX: 0.50 (50%) ← NEUTRAL/WEAK")
print("\n❌ System bought with 50-54% confidence during EXTREME risk environment!")
print("\n💡 What SHOULD have happened:")
print("  - During high risk (VIX 59.3, World Risk 100) → require 75%+ confidence")
print("  - Confidence <60% during risk-off → SKIP")

print("\n❌ PROBLEM #6: VOLUME ANALYSIS IGNORED FOR BOQ")
print("-" * 100)
print("BOQ.AX shows Volume: -0.236 (WEAK volume)")
print("This indicates:")
print("  - Low conviction from market participants")
print("  - Potential liquidity issues")
print("  - Price may not hold support")
print("\n💡 Result: BOQ.AX down -2.36% (worst performer)")

print("\n\n🔍 ROOT CAUSE ANALYSIS:")
print("=" * 100)

print("\n🎯 PRIMARY ROOT CAUSE: FINBERT SENTIMENT FAILURE")
print("-" * 100)
print("The FinBERT sentiment analysis component FAILED to fetch or process stock-level news.")
print("\nWhy this happened:")
print("  1. Possible API rate limit (Yahoo News, Google News, etc.)")
print("  2. News cache was empty for these symbols")
print("  3. Sentiment bridge returned default 0.000 instead of macro sentiment")
print("  4. No fallback to macro sentiment when stock sentiment unavailable")
print("\nImpact:")
print("  → System was 'blind' to negative market sentiment")
print("  → Technical/LSTM signals dominated (both unreliable)")
print("  → Risk-off conditions were NOT factored into decision")

print("\n🎯 SECONDARY ROOT CAUSE: NO MACRO RISK GATES")
print("-" * 100)
print("The trading system lacks proper macro risk gates:")
print("\nMissing checks:")
print("  ❌ No gate for World Risk > 80/100")
print("  ❌ No gate for US market down >1.5%")
print("  ❌ No gate for VIX > 30")
print("  ❌ No gate for low confidence (<60%) during high risk")
print("\nWhy this is critical:")
print("  → Financials are HIGHEST BETA sector (most sensitive to market)")
print("  → Banks/insurance correlate 0.85+ with broader market")
print("  → Buying banks during selloff = catching falling knife")

print("\n🎯 TERTIARY ROOT CAUSE: INSUFFICIENT DATA HANDLING")
print("-" * 100)
print("LSTM training failed for all 3 positions, but system proceeded anyway.")
print("\nProper handling should be:")
print("  1. If LSTM training fails → reduce signal confidence by 30%")
print("  2. During high risk → reject signals with <60 days LSTM data")
print("  3. Weight fallback logic lower (current: seems equal weight)")

print("\n\n💡 RECOMMENDED FIXES:")
print("=" * 100)

print("\n1️⃣  IMMEDIATE FIX: Add Macro Risk Gates")
print("-" * 100)
print("""
# In paper_trading_coordinator.py or swing_signal_generator.py

def should_allow_new_position(self, symbol, signal, confidence):
    # Get macro context
    world_risk = self.get_world_risk_score()
    us_market_change = self.get_us_overnight_performance()
    vix = self.get_vix()
    
    # Gate 1: World Risk
    if world_risk > 80:
        logger.warning(f"🚫 REJECTED {symbol}: World Risk {world_risk}/100 > 80 (EXTREME)")
        return False
    
    # Gate 2: US Market Selloff
    if us_market_change < -1.5:
        logger.warning(f"🚫 REJECTED {symbol}: US down {us_market_change}% (risk-off)")
        return False
    
    # Gate 3: VIX Elevated
    if vix > 30 and confidence < 0.70:
        logger.warning(f"🚫 REJECTED {symbol}: VIX {vix} + low confidence {confidence:.2f}")
        return False
    
    # Gate 4: Financials during risk-off
    if symbol in FINANCIAL_SECTORS and (world_risk > 60 or us_market_change < -1.0):
        logger.warning(f"🚫 REJECTED {symbol}: Financial during risk-off conditions")
        return False
    
    return True
""")

print("\n2️⃣  CRITICAL FIX: FinBERT Fallback Logic")
print("-" * 100)
print("""
# In batch_predictor.py or swing_signal_generator.py

def get_sentiment_score(self, symbol):
    # Try stock-specific sentiment
    stock_sentiment = self.finbert_bridge.get_sentiment(symbol)
    
    if stock_sentiment is None or stock_sentiment['confidence'] < 0.3:
        # Fallback to macro sentiment
        macro_sentiment = self.get_macro_sentiment()
        
        logger.warning(
            f"⚠️ {symbol}: No stock sentiment, using macro={macro_sentiment:.3f}"
        )
        
        # Adjust for sector
        if symbol in FINANCIAL_SECTORS:
            # Financials amplify macro sentiment
            return macro_sentiment * 1.3
        else:
            return macro_sentiment
    
    return stock_sentiment['score']
""")

print("\n3️⃣  IMPORTANT FIX: Confidence Adjustment for Missing Data")
print("-" * 100)
print("""
# In swing_signal_generator.py

def adjust_confidence_for_data_quality(self, symbol, base_confidence):
    penalties = []
    
    # Check LSTM data availability
    if not self.has_sufficient_lstm_data(symbol):
        penalties.append(('LSTM_DATA', 0.20))  # -20% confidence
    
    # Check sentiment data availability
    if self.sentiment_score == 0.0:
        penalties.append(('NO_SENTIMENT', 0.15))  # -15% confidence
    
    # Check volume data
    if self.volume_score < -0.2:
        penalties.append(('WEAK_VOLUME', 0.10))  # -10% confidence
    
    # Apply penalties
    adjusted = base_confidence
    for reason, penalty in penalties:
        adjusted -= penalty
        logger.warning(f"⚠️ {symbol}: Confidence penalty -{penalty:.0%} ({reason})")
    
    return max(0.0, adjusted)
""")

print("\n4️⃣  DEFENSIVE FIX: Position Sizing During Risk-Off")
print("-" * 100)
print("""
# In paper_trading_coordinator.py

def calculate_position_size(self, symbol, signal, confidence):
    base_size = self.calculate_kelly_size(signal, confidence)
    
    # Risk adjustments
    risk_multiplier = 1.0
    
    # Adjust for world risk
    world_risk = self.get_world_risk_score()
    if world_risk > 80:
        risk_multiplier *= 0.25  # 75% reduction
    elif world_risk > 60:
        risk_multiplier *= 0.50  # 50% reduction
    
    # Adjust for VIX
    vix = self.get_vix()
    if vix > 30:
        risk_multiplier *= 0.50
    
    # Adjust for US overnight performance
    us_change = self.get_us_overnight_performance()
    if us_change < -2.0:
        risk_multiplier *= 0.25
    elif us_change < -1.0:
        risk_multiplier *= 0.50
    
    final_size = base_size * risk_multiplier
    
    logger.info(
        f"💰 {symbol}: Base size ${base_size:.0f} → "
        f"${final_size:.0f} (risk_mult={risk_multiplier:.2f})"
    )
    
    return final_size
""")

print("\n\n📊 EXPECTED OUTCOME WITH FIXES:")
print("=" * 100)

print("\n✅ IF FIXES WERE APPLIED ON MARCH 4:")
print("-" * 100)
print("\n🔒 BP.L:")
print("   Gate 1 (World Risk 100): ❌ REJECTED")
print("   Gate 2 (US down -2.47%): ❌ REJECTED")
print("   Gate 3 (VIX 59.3, conf 54%): ❌ REJECTED")
print("   Gate 4 (Financial + risk-off): ❌ REJECTED")
print("   → NO POSITION OPENED ✅")

print("\n🔒 BOQ.AX:")
print("   Gate 1 (World Risk 100): ❌ REJECTED")
print("   Gate 2 (US down -2.47%): ❌ REJECTED")
print("   Gate 4 (Financial + risk-off): ❌ REJECTED")
print("   Weak Volume (-0.236): ❌ Additional rejection factor")
print("   → NO POSITION OPENED ✅")

print("\n🔒 NAB.AX:")
print("   Gate 1 (World Risk 100): ❌ REJECTED")
print("   Gate 2 (US down -2.47%): ❌ REJECTED")
print("   Gate 4 (Financial + risk-off): ❌ REJECTED")
print("   → NO POSITION OPENED ✅")

print("\n💰 PORTFOLIO OUTCOME:")
print("   Current: $99,443.94 (-0.56%)")
print("   With fixes: $100,000.00 (0.00%) - stayed in cash ✅")
print("   Avoided losses: $556.06")

print("\n\n🎓 LESSONS LEARNED:")
print("=" * 100)

print("""
1. **FinBERT Sentiment is CRITICAL** - without it, system is blind to macro risks
   → Need robust fallback to macro sentiment when stock sentiment unavailable

2. **Macro Risk Gates are ESSENTIAL** - technical signals alone will fail during selloffs
   → Must check World Risk, US performance, VIX before ANY financial sector buys

3. **Confidence Thresholds Must Be Dynamic** - 50% confidence OK in calm markets, not during crises
   → During high risk: require 70%+ confidence, or stay in cash

4. **LSTM Data Requirements** - if LSTM can't train properly, signal quality is compromised
   → Either penalize confidence heavily, or reject signal entirely

5. **Sector-Specific Rules** - Financials behave differently than tech/healthcare
   → Banks/insurance have 0.85+ correlation with broader market
   → Should NEVER buy financials during market selloffs

6. **Position Sizing Matters** - even if signal is "OK", size should reflect risk environment
   → World Risk 100/100 → reduce position size by 75%
   → Multiple risk factors → multiply reductions (0.5 × 0.5 = 0.25)

7. **US Market Leads ASX** - ASX typically follows US with 1-day lag
   → Check overnight US performance BEFORE opening ASX positions
   → US down >1.5% → defensive mode for ASX trading
""")

print("\n\n✅ CONCLUSION:")
print("=" * 100)
print("""
The system bought financial stocks (BP.L, BOQ.AX, NAB.AX) during extreme risk-off 
conditions because:

1. FinBERT sentiment analysis FAILED → returned 0.000 (neutral) instead of negative
2. No macro risk gates → World Risk 100/100 was IGNORED
3. No US market check → -2.47% S&P selloff was IGNORED  
4. Low confidence accepted → 50-54% confidence during high risk
5. LSTM data insufficient → unreliable predictions used anyway

All three positions are now UNDERWATER:
  - BP.L: 0.00% (flat, luck)
  - BOQ.AX: -2.36% 
  - NAB.AX: -1.22%

RECOMMENDED ACTION NOW:
  1. Exit all three positions (cut losses)
  2. Implement macro risk gates IMMEDIATELY
  3. Fix FinBERT sentiment fallback logic
  4. Add confidence penalty for missing data
  5. Do NOT buy financials until World Risk < 60 and US market stabilizes
""")

print("\n" + "=" * 100)

