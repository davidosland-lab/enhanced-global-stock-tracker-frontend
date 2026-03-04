# FinBERT Sentiment Integration for Unified Trading Platform

## Problem Analysis

### What You Discovered
Looking at the **FinBERT v4.4.4** sentiment display in your screenshot shows:
- **Negative Sentiment:** High (red bar)
- **Neutral Sentiment:** Moderate (yellow bar)  
- **Positive Sentiment:** Low (green bar)
- **Result:** Should be a **NO BUY** day

### But the Unified Trading Platform Bought Stock Anyway!

**Why?** The unified trading platform is using **DIFFERENT sentiment data**:

| Platform | Sentiment Source | Data Type | Issue |
|----------|------------------|-----------|-------|
| **FinBERT v4.4.4** | FinBERT AI Model | News + Financial Text Analysis | ✅ Accurate, AI-powered |
| **Unified Trading Dashboard** | SPY Price Action | Technical indicators only | ❌ Ignores news sentiment |

---

## Root Cause

### Unified Trading Dashboard (Current Implementation)

**File:** `paper_trading_coordinator.py`, lines 356-414

```python
def get_market_sentiment(self) -> float:
    """
    Get current market sentiment (0-100)
    Simulated by analyzing SPY and VIX  # ← PROBLEM: No FinBERT!
    """
    # Fetch SPY (S&P 500) data
    spy_data = self.fetch_market_data('SPY', period='1mo')
    
    # Calculate sentiment based on price action
    sentiment = 50  # Neutral baseline
    sentiment += daily_change * 3.33     # ± 10 points
    sentiment += five_day_change * 3     # ± 15 points
    sentiment += ma_position * 5         # ± 10 points
    
    return sentiment  # 0-100 score
```

**What's Missing:**
- ❌ No FinBERT sentiment analysis
- ❌ No news data
- ❌ No negative/neutral/positive breakdown
- ❌ No connection to overnight pipeline sentiment

### Overnight Pipeline (Correct Implementation)

**File:** `models/screening/overnight_pipeline.py`

```python
# Uses SPI Monitor for proper sentiment
spi_sentiment = self._fetch_spi_market_sentiment()

# Returns comprehensive sentiment:
{
    'sentiment_score': 45.2,          # 0-100
    'sentiment_label': 'BEARISH',     # Classification
    'gap_prediction': {
        'direction': 'down',
        'magnitude_pct': -0.5
    },
    'recommendation': {
        'stance': 'CAUTION',          # ← THIS should block trades
        'confidence': 'HIGH'
    }
}
```

**What's Right:**
- ✅ Uses SPI Monitor (ASX-specific)
- ✅ Incorporates US market closes
- ✅ Predicts opening gaps
- ✅ Provides trading recommendations

---

## The Disconnect

```
┌─────────────────────────────────────────────────────────────┐
│                  OVERNIGHT PIPELINE                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Scan 240 stocks                                    │  │
│  │ 2. Run FinBERT + LSTM predictions                     │  │
│  │ 3. Get SPI sentiment → BEARISH (45.2/100)            │  │
│  │ 4. Score opportunities                                │  │
│  │ 5. Generate au_morning_report.json                    │  │
│  │    - sentiment_score: 45.2                            │  │
│  │    - recommendation: CAUTION                          │  │
│  │    - top_opportunities: [...                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ au_morning_report.json
                            ▼
              ❌ NOT CONNECTED ❌
                            │
┌─────────────────────────────────────────────────────────────┐
│            UNIFIED TRADING DASHBOARD                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. User selects stocks                                │  │
│  │ 2. Calculate sentiment from SPY price → 55/100       │  │
│  │    (ignores overnight pipeline data!)                 │  │
│  │ 3. Generate signals from technicals only             │  │
│  │ 4. ✅ BUY signal generated (sentiment > 40)          │  │
│  │ 5. Enters positions (ignoring BEARISH warning!)      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**The Gap:** The unified trading dashboard **never reads** the `au_morning_report.json` file!

---

## Solution: Integrate FinBERT Sentiment

### Option 1: Use Overnight Pipeline Sentiment (Recommended)

**Modify:** `paper_trading_coordinator.py`

#### Step 1: Add Morning Report Reader

```python
def load_morning_sentiment(self, market: str = 'au') -> Optional[Dict]:
    """
    Load sentiment from overnight pipeline morning report
    
    Args:
        market: Market code ('au', 'us', 'uk')
    
    Returns:
        Sentiment data from morning report
    """
    try:
        # Path to morning report
        report_path = Path('reports/screening') / f'{market}_morning_report.json'
        
        if not report_path.exists():
            logger.warning(f"Morning report not found: {report_path}")
            return None
        
        # Check if report is recent (< 24 hours old)
        file_age = time.time() - report_path.stat().st_mtime
        if file_age > 86400:  # 24 hours
            logger.warning(f"Morning report is stale ({file_age/3600:.1f} hours old)")
            return None
        
        # Load report
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        # Extract sentiment data
        sentiment_data = {
            'overall_sentiment': report.get('overall_sentiment', 50),
            'confidence': report.get('confidence', 'MODERATE'),
            'risk_rating': report.get('risk_rating', 'Moderate'),
            'volatility_level': report.get('volatility_level', 'Normal'),
            'recommendation': report.get('recommendation', 'HOLD'),
            'spi_sentiment': report.get('spi_sentiment', {}),
            'report_date': report.get('report_date'),
            'generated_at': report.get('generated_at')
        }
        
        logger.info(f"[SENTIMENT] Loaded {market.upper()} morning report: "
                   f"{sentiment_data['overall_sentiment']:.1f}/100 "
                   f"({sentiment_data['recommendation']})")
        
        return sentiment_data
        
    except Exception as e:
        logger.error(f"Error loading morning sentiment: {e}")
        return None
```

#### Step 2: Replace get_market_sentiment()

```python
def get_market_sentiment(self, use_morning_report: bool = True) -> float:
    """
    Get current market sentiment (0-100)
    
    Args:
        use_morning_report: Use overnight pipeline sentiment if available
    
    Returns:
        Sentiment score (0-100)
    """
    # Try to load morning report sentiment first
    if use_morning_report:
        morning_sentiment = self.load_morning_sentiment(market='au')
        
        if morning_sentiment:
            sentiment_score = morning_sentiment['overall_sentiment']
            recommendation = morning_sentiment['recommendation']
            
            logger.info(f"[SENTIMENT] Using morning report: {sentiment_score:.1f}/100 "
                       f"({recommendation})")
            
            self.last_market_sentiment = sentiment_score
            self.sentiment_recommendation = recommendation
            return sentiment_score
    
    # Fallback to SPY-based sentiment (original logic)
    logger.info("[SENTIMENT] Morning report not available, using SPY-based sentiment")
    
    try:
        # ... original SPY-based code ...
        spy_data = self.fetch_market_data('SPY', period='1mo')
        # ... rest of original logic ...
    except Exception as e:
        logger.error(f"Error calculating market sentiment: {e}")
        return 50.0
```

#### Step 3: Add Sentiment Gate to Trading Logic

```python
def should_enter_position(self, symbol: str, signal: Dict, sentiment_score: float) -> bool:
    """
    Determine if position should be entered based on signal and sentiment
    
    Args:
        symbol: Stock symbol
        signal: Trading signal
        sentiment_score: Market sentiment (0-100)
    
    Returns:
        True if position should be entered
    """
    # Get sentiment recommendation if available
    if hasattr(self, 'sentiment_recommendation'):
        recommendation = self.sentiment_recommendation
        
        # Block trades on strong negative sentiment
        if recommendation in ['STRONG_SELL', 'AVOID']:
            logger.warning(f"[BLOCK] {symbol}: Market recommendation is {recommendation}")
            return False
        
        # Reduce position size on CAUTION
        if recommendation == 'CAUTION' and sentiment_score < 45:
            logger.warning(f"[CAUTION] {symbol}: Bearish market (sentiment: {sentiment_score:.1f})")
            # Allow trades but with reduced size (handled in position sizing)
    
    # Original sentiment gates
    if sentiment_score < self.config.get('sentiment_block_threshold', 30):
        logger.warning(f"[BLOCK] {symbol}: Sentiment too low ({sentiment_score:.1f} < 30)")
        return False
    
    # Check signal strength
    if signal['action'] not in ['BUY', 'STRONG_BUY']:
        return False
    
    # Check confidence
    min_confidence = self.config.get('min_signal_confidence', 60)
    if signal.get('confidence', 0) < min_confidence:
        logger.info(f"[SKIP] {symbol}: Confidence {signal.get('confidence'):.1f}% < {min_confidence}%")
        return False
    
    return True
```

---

### Option 2: Direct FinBERT Integration

**Add FinBERT Module to Paper Trading Coordinator**

#### Step 1: Import FinBERT

```python
# At top of paper_trading_coordinator.py

try:
    from finbert_v4.4.4.models.finbert_sentiment import FinBERTSentimentAnalyzer
    FINBERT_AVAILABLE = True
    logger.info("[FINBERT] FinBERT sentiment analyzer loaded")
except ImportError:
    FINBERT_AVAILABLE = False
    logger.warning("[FINBERT] FinBERT not available, using fallback")
```

#### Step 2: Initialize in __init__

```python
def __init__(self, symbols: List[str], initial_capital: float = 100000, config_path: str = None):
    # ... existing init code ...
    
    # Initialize FinBERT if available
    if FINBERT_AVAILABLE:
        self.finbert_analyzer = FinBERTSentimentAnalyzer()
        logger.info("[FINBERT] Sentiment analyzer initialized")
    else:
        self.finbert_analyzer = None
```

#### Step 3: Add News-Based Sentiment

```python
def get_finbert_sentiment(self, symbol: str) -> Dict:
    """
    Get FinBERT sentiment for a stock using recent news
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Sentiment analysis from FinBERT
    """
    if not self.finbert_analyzer:
        return {'sentiment': 'neutral', 'confidence': 50, 'scores': {}}
    
    try:
        # Fetch recent news for the symbol
        news_items = self.fetch_news_data(symbol, max_items=10)
        
        if not news_items:
            logger.info(f"[FINBERT] No news for {symbol}, using neutral")
            return {'sentiment': 'neutral', 'confidence': 50, 'scores': {}}
        
        # Analyze news with FinBERT
        news_texts = [item.get('title', '') + ' ' + item.get('summary', '') 
                     for item in news_items]
        
        sentiment = self.finbert_analyzer.analyze_news_batch(news_texts)
        
        logger.info(f"[FINBERT] {symbol}: {sentiment['sentiment'].upper()} "
                   f"({sentiment['confidence']:.1f}% confidence, "
                   f"compound: {sentiment['compound']:.3f})")
        
        return sentiment
        
    except Exception as e:
        logger.error(f"[FINBERT] Error analyzing {symbol}: {e}")
        return {'sentiment': 'neutral', 'confidence': 50, 'scores': {}}
```

#### Step 4: Integrate into Signal Generation

```python
def generate_enhanced_signal(self, symbol: str, price_data: pd.DataFrame) -> Dict:
    """
    Generate enhanced signal with FinBERT sentiment
    
    Args:
        symbol: Stock symbol
        price_data: Price history
    
    Returns:
        Enhanced signal with sentiment
    """
    # Get base technical signal
    tech_signal = self.generate_swing_signal(symbol, price_data)
    
    # Get FinBERT sentiment
    finbert_sentiment = self.get_finbert_sentiment(symbol)
    
    # Adjust signal based on sentiment
    sentiment_compound = finbert_sentiment.get('compound', 0)
    
    # Strong negative sentiment → Block BUY signals
    if sentiment_compound < -0.3 and tech_signal['action'] == 'BUY':
        logger.warning(f"[FINBERT BLOCK] {symbol}: Negative sentiment ({sentiment_compound:.3f}) blocks BUY")
        tech_signal['action'] = 'HOLD'
        tech_signal['sentiment_blocked'] = True
    
    # Add sentiment data to signal
    tech_signal['finbert_sentiment'] = finbert_sentiment
    tech_signal['sentiment_compound'] = sentiment_compound
    
    return tech_signal
```

---

## Implementation Comparison

| Feature | Option 1: Morning Report | Option 2: Direct FinBERT |
|---------|-------------------------|--------------------------|
| **Data Source** | Overnight pipeline | Live news analysis |
| **Sentiment Type** | Market-wide (ASX/US/UK) | Stock-specific |
| **Update Frequency** | Once per day (morning) | Real-time |
| **Requires** | Overnight pipeline run | FinBERT v4.4.4 |
| **Accuracy** | High (240 stocks analyzed) | High (news-based) |
| **Performance** | Fast (cached) | Slow (API calls) |
| **Best For** | Pre-market decisions | Intraday decisions |

---

## Recommended Solution

**Use BOTH:**

1. **Morning Report Sentiment** (Option 1) for:
   - Initial trading decisions at market open
   - Overall market direction/bias
   - Risk gates (AVOID/CAUTION/BUY)

2. **Direct FinBERT** (Option 2) for:
   - Stock-specific news sentiment
   - Intraday position adjustments
   - Breaking news reactions

### Combined Implementation

```python
def get_comprehensive_sentiment(self, symbol: str) -> Dict:
    """
    Get comprehensive sentiment combining market and stock-specific analysis
    
    Returns:
        {
            'market_sentiment': 45.2,        # From morning report
            'market_recommendation': 'CAUTION',
            'stock_sentiment': {             # From FinBERT
                'sentiment': 'negative',
                'confidence': 72.5,
                'compound': -0.45
            },
            'trading_decision': 'BLOCK',     # Final decision
            'reason': 'Market CAUTION + Stock negative sentiment'
        }
    """
    # Get market-wide sentiment from morning report
    morning_data = self.load_morning_sentiment(market='au')
    market_sentiment = morning_data['overall_sentiment'] if morning_data else 50
    market_rec = morning_data['recommendation'] if morning_data else 'HOLD'
    
    # Get stock-specific FinBERT sentiment
    stock_sentiment = self.get_finbert_sentiment(symbol)
    
    # Combine for trading decision
    decision = 'ALLOW'  # Default
    reason = []
    
    # Market gates
    if market_rec in ['STRONG_SELL', 'AVOID']:
        decision = 'BLOCK'
        reason.append(f"Market {market_rec}")
    elif market_rec == 'CAUTION' and market_sentiment < 45:
        decision = 'REDUCE'
        reason.append(f"Market CAUTION ({market_sentiment:.1f})")
    
    # Stock gates
    if stock_sentiment['compound'] < -0.3:
        decision = 'BLOCK' if decision == 'BLOCK' else 'REDUCE'
        reason.append(f"Stock negative ({stock_sentiment['compound']:.2f})")
    
    return {
        'market_sentiment': market_sentiment,
        'market_recommendation': market_rec,
        'stock_sentiment': stock_sentiment,
        'trading_decision': decision,
        'reason': ' + '.join(reason) if reason else 'No restrictions'
    }
```

---

## Testing the Fix

### Before Fix

```bash
# Run unified trading dashboard
python unified_trading_dashboard.py --symbols CBA.AX,BHP.AX --capital 100000

# Result: Buys stocks even on negative sentiment days
# Sentiment: 55/100 (from SPY price action)
# Action: BUY CBA.AX, BHP.AX
```

### After Fix

```bash
# 1. Run overnight pipeline first
python run_au_pipeline.py --full-scan --capital 100000

# Output: au_morning_report.json
# Sentiment: 45.2/100 (CAUTION)
# Recommendation: Avoid new positions

# 2. Run unified trading dashboard
python unified_trading_dashboard.py --symbols CBA.AX,BHP.AX --capital 100000

# Result: Respects overnight sentiment
# [SENTIMENT] Using morning report: 45.2/100 (CAUTION)
# [BLOCK] CBA.AX: Market recommendation is CAUTION
# [BLOCK] BHP.AX: Market recommendation is CAUTION
# Action: NO TRADES (sentiment gate blocked)
```

---

## Files to Modify

1. **`paper_trading_coordinator.py`**
   - Add `load_morning_sentiment()`
   - Modify `get_market_sentiment()`
   - Add `should_enter_position()` gate
   - Add FinBERT integration (optional)

2. **`unified_trading_dashboard.py`**
   - Display morning report sentiment
   - Show sentiment breakdown (negative/neutral/positive)
   - Add sentiment status indicator

3. **Create `sentiment_integration.py`** (new file)
   - Centralized sentiment logic
   - Combines morning report + FinBERT
   - Provides unified API for sentiment queries

---

## Next Steps

Would you like me to:

1. ✅ **Create the full implementation patch** (v1.3.15.45)
2. ✅ **Integrate Option 1** (Morning Report - Fast)
3. ✅ **Integrate Option 2** (Direct FinBERT - Accurate)
4. ✅ **Implement BOTH** (Recommended - Complete solution)
5. ✅ **Create testing script** to verify sentiment gates work

**The fix will ensure:** When FinBERT shows negative sentiment (like in your screenshot), the unified trading platform will **NOT buy stocks** - it will respect the CAUTION/AVOID recommendation from the overnight pipeline.

---

**Status:** Analysis Complete  
**Priority:** HIGH (Trading on wrong sentiment = Financial loss)  
**Estimated Fix Time:** 2 hours  
**Testing Required:** Yes (with real negative sentiment day)
