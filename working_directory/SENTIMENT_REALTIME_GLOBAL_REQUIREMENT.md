# REAL-TIME GLOBAL SENTIMENT REQUIREMENT

**Date**: 2026-01-29  
**Priority**: HIGH  
**User Requirement**: "This should be a global value that is calculated throughout the day and changes not just once every run. The sentiment is a measure of direction and should be used in ongoing calculations of buy sell throughout a trading period."

---

## Current Problem

### What's Wrong Now

**Current Behavior**:
- ✅ Sentiment loaded ONCE from morning report (static all day)
- ❌ Hardcoded to AU market only (ignores US/UK)
- ❌ No real-time updates during trading session
- ❌ No intraday recalculation based on market movements

**Code Location**: `paper_trading_coordinator.py`, line 391
```python
# Loads ONCE at startup from morning report
morning_data = self.sentiment_analyzer.load_morning_sentiment(market='au')
# Result: Static sentiment all day (e.g., 65.0 at 8am → still 65.0 at 8pm)
```

### User's Correct Expectation

**Required Behavior**:
- ✅ GLOBAL multi-market sentiment (US 50% + UK 25% + AU 25%)
- ✅ REAL-TIME updates throughout trading day
- ✅ DYNAMIC recalculation every trading cycle (5-15 minutes)
- ✅ Used in ONGOING buy/sell decisions (not static)

**Example Timeline**:
```
08:00 GMT: Global Sentiment = 65.0 (BULLISH) → BUY signals active
10:00 GMT: Global Sentiment = 52.0 (NEUTRAL) → Reduced confidence
14:00 GMT: Global Sentiment = 35.0 (BEARISH) → SELL signals, block new buys
18:00 GMT: Global Sentiment = 48.0 (NEUTRAL) → Resume monitoring
```

---

## Solution Architecture

### Real-Time Global Sentiment Calculator

**New Function**: `get_realtime_global_sentiment()`

**Data Sources** (priority order):
1. **Real-time index prices** (yfinance, 15-min delay)
   - ^GSPC (S&P 500) - US
   - ^IXIC (NASDAQ) - US  
   - ^FTSE (FTSE 100) - UK
   - ^AORD (ASX All Ords) - AU
   
2. **VIX/Fear indices**
   - ^VIX (US Fear Index)
   - ^VFTSE (UK Fear Index)
   
3. **Morning report baseline** (fallback)
   - Static sentiment from overnight pipeline
   - Used if real-time data fails

**Update Frequency**: Every trading cycle (5-15 minutes)

**Calculation Method**: Weighted multi-market with trend analysis

---

## Implementation Plan

### Phase 1: Real-Time Market Data Fetcher

```python
class RealtimeMarketSentiment:
    """Real-time global market sentiment calculator"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_update = 0
        
        # Market indices to monitor
        self.indices = {
            'us': ['^GSPC', '^IXIC', '^DJI'],  # S&P 500, NASDAQ, Dow
            'uk': ['^FTSE'],                    # FTSE 100
            'au': ['^AORD']                     # ASX All Ords
        }
        
        # Fear indices
        self.fear_indices = {
            'us': '^VIX',      # US VIX
            'uk': '^VFTSE'     # UK VIX
        }
        
        # Market weights (US-dominant)
        self.weights = {
            'us': 0.50,  # 50% - most influential
            'uk': 0.25,  # 25% - bridge session
            'au': 0.25   # 25% - first to open
        }
    
    def get_global_sentiment(self) -> Dict:
        """
        Calculate real-time global sentiment (0-100)
        
        Returns:
            {
                'score': float,        # 0-100
                'label': str,          # BULLISH/NEUTRAL/BEARISH
                'confidence': str,     # HIGH/MODERATE/LOW
                'breakdown': {
                    'us': {'score': float, 'change': float, 'trend': str},
                    'uk': {'score': float, 'change': float, 'trend': str},
                    'au': {'score': float, 'change': float, 'trend': str}
                },
                'timestamp': datetime,
                'source': str          # 'realtime' or 'morning_report'
            }
        """
        # Check cache (refresh every 5 minutes)
        if time.time() - self.last_update < self.cache_ttl:
            if 'global_sentiment' in self.cache:
                return self.cache['global_sentiment']
        
        # Calculate fresh sentiment
        try:
            sentiments = {}
            
            # Fetch each market's real-time sentiment
            for market, indices in self.indices.items():
                market_sentiment = self._calculate_market_sentiment(market, indices)
                if market_sentiment:
                    sentiments[market] = market_sentiment
            
            # Calculate weighted global sentiment
            if len(sentiments) > 0:
                global_score = self._weighted_average(sentiments)
                
                # Build result
                result = {
                    'score': global_score,
                    'label': self._classify_sentiment(global_score),
                    'confidence': self._calculate_confidence(sentiments),
                    'breakdown': sentiments,
                    'timestamp': datetime.now(),
                    'source': 'realtime'
                }
                
                # Update cache
                self.cache['global_sentiment'] = result
                self.last_update = time.time()
                
                return result
            else:
                # Fallback to morning report
                return self._fallback_morning_sentiment()
                
        except Exception as e:
            logger.error(f"[SENTIMENT] Real-time calculation failed: {e}")
            return self._fallback_morning_sentiment()
    
    def _calculate_market_sentiment(self, market: str, symbols: List[str]) -> Dict:
        """Calculate sentiment for a specific market"""
        try:
            scores = []
            changes = []
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                
                # Get intraday data (1 day, 15-min intervals)
                hist = ticker.history(period='1d', interval='15m')
                
                if len(hist) == 0:
                    continue
                
                # Get official previous close
                info = ticker.info
                prev_close = info.get('regularMarketPreviousClose', info.get('previousClose'))
                current_price = hist['Close'].iloc[-1]
                
                if prev_close and prev_close > 0:
                    # Calculate % change from previous close
                    pct_change = ((current_price - prev_close) / prev_close) * 100
                    
                    # Calculate intraday momentum (last hour vs 4 hours ago)
                    if len(hist) >= 16:  # 4 hours = 16 intervals
                        momentum = ((current_price - hist['Close'].iloc[-16]) / hist['Close'].iloc[-16]) * 100
                    else:
                        momentum = pct_change
                    
                    # Convert to sentiment score (0-100)
                    # Baseline 50, ±30 for change, ±20 for momentum
                    sentiment_score = 50 + (pct_change * 10) + (momentum * 5)
                    sentiment_score = max(0, min(100, sentiment_score))  # Clamp
                    
                    scores.append(sentiment_score)
                    changes.append(pct_change)
            
            if len(scores) > 0:
                avg_score = sum(scores) / len(scores)
                avg_change = sum(changes) / len(changes)
                
                # Determine trend
                if avg_change > 0.5:
                    trend = 'UP'
                elif avg_change < -0.5:
                    trend = 'DOWN'
                else:
                    trend = 'FLAT'
                
                return {
                    'score': avg_score,
                    'change': avg_change,
                    'trend': trend,
                    'indices_count': len(scores)
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"[SENTIMENT] Failed to calculate {market} sentiment: {e}")
            return None
    
    def _weighted_average(self, sentiments: Dict) -> float:
        """Calculate weighted average across markets"""
        total_weight = 0
        weighted_sum = 0
        
        for market, data in sentiments.items():
            weight = self.weights.get(market, 0.25)
            weighted_sum += data['score'] * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 50.0
    
    def _classify_sentiment(self, score: float) -> str:
        """Classify sentiment score into label"""
        if score >= 65:
            return 'BULLISH'
        elif score >= 55:
            return 'SLIGHTLY_BULLISH'
        elif score >= 45:
            return 'NEUTRAL'
        elif score >= 35:
            return 'SLIGHTLY_BEARISH'
        else:
            return 'BEARISH'
    
    def _calculate_confidence(self, sentiments: Dict) -> str:
        """Calculate confidence based on market agreement"""
        if len(sentiments) < 2:
            return 'LOW'
        
        scores = [data['score'] for data in sentiments.values()]
        
        # Check variance
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        if std_dev < 10:
            return 'HIGH'      # Markets agree
        elif std_dev < 20:
            return 'MODERATE'  # Some divergence
        else:
            return 'LOW'       # Markets disagree
    
    def _fallback_morning_sentiment(self) -> Dict:
        """Fallback to morning report if real-time fails"""
        # Load from morning reports (static)
        # ... (existing logic)
        pass
```

### Phase 2: Integration with Trading Coordinator

```python
# In paper_trading_coordinator.py

def __init__(self, ...):
    # ... existing init ...
    
    # Add real-time sentiment calculator
    self.realtime_sentiment = RealtimeMarketSentiment()
    
def get_market_sentiment(self) -> float:
    """
    Get REAL-TIME global market sentiment (0-100)
    
    **NEW**: Updates every 5 minutes throughout trading day
    **GLOBAL**: Weighted average of US (50%), UK (25%), AU (25%)
    
    Returns:
        Current global sentiment score (0-100)
    """
    try:
        # Get real-time global sentiment
        sentiment_data = self.realtime_sentiment.get_global_sentiment()
        
        # Update internal state
        self.last_market_sentiment = sentiment_data['score']
        self.sentiment_breakdown = sentiment_data['breakdown']
        self.sentiment_confidence = sentiment_data['confidence']
        
        # Log sentiment update
        logger.info(f"[SENTIMENT] GLOBAL: {sentiment_data['score']:.1f}/100 "
                   f"({sentiment_data['label']}) - {sentiment_data['confidence']} confidence")
        
        # Log breakdown
        for market, data in sentiment_data['breakdown'].items():
            logger.info(f"            {market.upper()}: {data['score']:.1f} "
                       f"({data['change']:+.2f}%) {data['trend']}")
        
        return sentiment_data['score']
        
    except Exception as e:
        logger.error(f"[SENTIMENT] Real-time calculation failed: {e}, using fallback")
        
        # Fallback to morning report (existing logic)
        return self._fallback_sentiment()

def _evaluate_signal_with_sentiment(self, signal: Dict, sentiment_score: float) -> Dict:
    """
    Evaluate trading signal with real-time sentiment
    
    **NEW**: Uses dynamic sentiment throughout trading session
    
    Args:
        signal: Trading signal with confidence
        sentiment_score: Current real-time sentiment (0-100)
    
    Returns:
        Adjusted signal with sentiment weighting
    """
    original_confidence = signal.get('confidence', 0)
    
    # Sentiment gates (configurable thresholds)
    BLOCK_THRESHOLD = 20   # < 20: BLOCK all buys
    REDUCE_THRESHOLD = 35  # < 35: REDUCE confidence by 30%
    BOOST_THRESHOLD = 65   # > 65: BOOST confidence by 20%
    
    # Apply sentiment adjustments
    if sentiment_score < BLOCK_THRESHOLD:
        # BEARISH: Block new positions
        logger.warning(f"[SENTIMENT GATE] BLOCK - Sentiment {sentiment_score:.1f} < {BLOCK_THRESHOLD}")
        signal['blocked'] = True
        signal['block_reason'] = f"Bearish sentiment ({sentiment_score:.1f})"
        return signal
    
    elif sentiment_score < REDUCE_THRESHOLD:
        # SLIGHTLY BEARISH: Reduce confidence
        adjustment = -0.30
        adjusted_confidence = original_confidence * (1 + adjustment)
        logger.info(f"[SENTIMENT GATE] REDUCE - Sentiment {sentiment_score:.1f} → "
                   f"Confidence {original_confidence:.1%} → {adjusted_confidence:.1%}")
        signal['confidence'] = adjusted_confidence
        signal['sentiment_adjustment'] = adjustment
        return signal
    
    elif sentiment_score > BOOST_THRESHOLD:
        # BULLISH: Boost confidence
        adjustment = +0.20
        adjusted_confidence = min(1.0, original_confidence * (1 + adjustment))
        logger.info(f"[SENTIMENT GATE] BOOST - Sentiment {sentiment_score:.1f} → "
                   f"Confidence {original_confidence:.1%} → {adjusted_confidence:.1%}")
        signal['confidence'] = adjusted_confidence
        signal['sentiment_adjustment'] = adjustment
        return signal
    
    else:
        # NEUTRAL: No adjustment
        logger.debug(f"[SENTIMENT GATE] NEUTRAL - Sentiment {sentiment_score:.1f}, no adjustment")
        signal['sentiment_adjustment'] = 0
        return signal
```

### Phase 3: Trading Cycle Integration

```python
def run_trading_cycle(self):
    """
    Execute one trading cycle with REAL-TIME sentiment updates
    
    **NEW**: Sentiment recalculated EVERY cycle (5-15 minutes)
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"[CYCLE] Trading cycle {self.cycle_count}")
    logger.info(f"{'='*60}")
    
    # STEP 1: Get REAL-TIME global sentiment (updates every cycle)
    current_sentiment = self.get_market_sentiment()
    
    logger.info(f"[SENTIMENT] Current global sentiment: {current_sentiment:.1f}/100")
    logger.info(f"[SENTIMENT] Breakdown: {len(self.sentiment_breakdown)}/3 markets")
    
    # STEP 2: Check if sentiment allows trading
    if current_sentiment < 20:
        logger.warning("[TRADING] Market sentiment too bearish, skipping buy evaluations")
        # Still check for sells (risk management)
        self.check_exit_conditions()
        return
    
    # STEP 3: Generate signals for all symbols
    for symbol in self.symbols:
        try:
            # Generate base signal
            signal = self.generate_swing_signal(symbol)
            
            if signal and signal.get('prediction') == 1:  # BUY signal
                # STEP 4: Apply real-time sentiment adjustment
                adjusted_signal = self._evaluate_signal_with_sentiment(signal, current_sentiment)
                
                if adjusted_signal.get('blocked'):
                    logger.info(f"[{symbol}] BUY signal BLOCKED by sentiment gate")
                    continue
                
                # STEP 5: Check if confidence meets threshold
                if adjusted_signal['confidence'] >= self.config.confidence_threshold:
                    logger.info(f"[{symbol}] BUY signal approved: "
                               f"confidence {adjusted_signal['confidence']:.1%} "
                               f"(sentiment adjusted)")
                    
                    # Execute buy
                    self.execute_buy(symbol, adjusted_signal)
                else:
                    logger.debug(f"[{symbol}] BUY signal below threshold after sentiment adjustment")
        
        except Exception as e:
            logger.error(f"[{symbol}] Error in cycle: {e}")
    
    # STEP 6: Check exit conditions (always runs)
    self.check_exit_conditions()
    
    # STEP 7: Update state
    self.save_state()
    
    logger.info(f"[CYCLE] Cycle {self.cycle_count} complete\n")
```

---

## Dashboard Real-Time Display

### Enhanced Sentiment Panel

```python
# In unified_trading_dashboard.py

# Add interval for real-time updates
app.layout = html.Div([
    # ... existing layout ...
    
    # Real-time sentiment update interval (5 minutes)
    dcc.Interval(
        id='sentiment-update-interval',
        interval=300*1000,  # 5 minutes in milliseconds
        n_intervals=0
    )
])

@app.callback(
    Output('sentiment-panel', 'children'),
    Input('sentiment-update-interval', 'n_intervals')
)
def update_sentiment_display(n):
    """Update sentiment display every 5 minutes"""
    
    # Get current real-time sentiment
    sentiment_data = coordinator.realtime_sentiment.get_global_sentiment()
    
    return html.Div([
        html.H3('Global Market Sentiment', style={'color': '#888', 'fontSize': '14px'}),
        
        # Main sentiment score
        html.Div([
            html.Div(f"{sentiment_data['score']:.1f}", 
                    style={'fontSize': '48px', 'fontWeight': 'bold'}),
            html.Div(sentiment_data['label'], 
                    style={'fontSize': '18px', 'color': get_sentiment_color(sentiment_data['score'])}),
            html.Div(f"{sentiment_data['confidence']} confidence", 
                    style={'fontSize': '12px', 'color': '#888', 'marginTop': '5px'}),
            html.Div(f"Updated: {sentiment_data['timestamp'].strftime('%H:%M:%S')}", 
                    style={'fontSize': '11px', 'color': '#666', 'marginTop': '5px'})
        ], style={'textAlign': 'center', 'padding': '20px 0'}),
        
        # Regional breakdown
        html.Div([
            html.H4('Regional Breakdown:', style={'fontSize': '12px', 'color': '#888', 'marginBottom': '10px'}),
            
            # US Market
            create_market_row('🇺🇸 US', 
                            sentiment_data['breakdown'].get('us', {}), 
                            sentiment_data['weights']['us']),
            
            # UK Market
            create_market_row('🇬🇧 UK', 
                            sentiment_data['breakdown'].get('uk', {}), 
                            sentiment_data['weights']['uk']),
            
            # AU Market
            create_market_row('🇦🇺 AU', 
                            sentiment_data['breakdown'].get('au', {}), 
                            sentiment_data['weights']['au'])
        ], style={'borderTop': '1px solid #333', 'paddingTop': '15px', 'marginTop': '15px'})
    ])

def create_market_row(flag_name: str, market_data: Dict, weight: float):
    """Create a market sentiment row"""
    if not market_data:
        return html.Div(f"{flag_name}: N/A", style={'color': '#666', 'fontSize': '11px'})
    
    score = market_data.get('score', 50)
    change = market_data.get('change', 0)
    trend = market_data.get('trend', 'FLAT')
    
    # Trend icon
    trend_icon = '↑' if trend == 'UP' else '↓' if trend == 'DOWN' else '→'
    trend_color = '#4CAF50' if trend == 'UP' else '#f44336' if trend == 'DOWN' else '#888'
    
    return html.Div([
        html.Span(f"{flag_name}: ", style={'fontSize': '12px'}),
        html.Span(f"{score:.1f}", style={'fontWeight': 'bold', 'fontSize': '12px'}),
        html.Span(f" ({change:+.2f}%)", style={'color': trend_color, 'fontSize': '11px'}),
        html.Span(f" {trend_icon}", style={'color': trend_color, 'fontSize': '12px'}),
        html.Span(f" [{weight:.0%}]", style={'color': '#666', 'fontSize': '10px', 'marginLeft': '5px'})
    ], style={'marginBottom': '8px'})
```

---

## Expected Behavior After Fix

### Timeline Example

```
08:00 GMT - Market Open (UK)
├─ Global Sentiment: 65.0 (BULLISH)
│  └─ US: 58.0 (-0.2%), UK: 72.0 (+0.8%), AU: 68.0 (+1.1%)
│  └─ Trading: BUY signals boosted +20%
│
10:30 GMT - Mid-Morning
├─ Global Sentiment: 58.0 (SLIGHTLY BULLISH)
│  └─ US: 55.0 (-0.5%), UK: 65.0 (+0.3%), AU: 58.0 (+0.2%)
│  └─ Trading: Normal confidence, no adjustments
│
14:00 GMT - US Market Open
├─ Global Sentiment: 48.0 (NEUTRAL)
│  └─ US: 42.0 (-1.2%), UK: 58.0 (-0.1%), AU: 55.0 (flat)
│  └─ Trading: Normal confidence, monitoring
│
16:00 GMT - Afternoon Selloff
├─ Global Sentiment: 32.0 (SLIGHTLY BEARISH)
│  └─ US: 25.0 (-2.5%), UK: 48.0 (-0.8%), AU: 45.0 (-0.5%)
│  └─ Trading: BUY confidence reduced -30%, sell signals active
│
18:00 GMT - Recovery
├─ Global Sentiment: 52.0 (NEUTRAL)
│  └─ US: 48.0 (-1.0%), UK: CLOSED, AU: CLOSED
│  └─ Trading: Resume normal operations
│
21:00 GMT - US Close
└─ Final Sentiment: 55.0 (SLIGHTLY BULLISH)
   └─ Set tone for next AU session
```

---

## Summary

### Current State ❌

- Static sentiment (morning report only)
- AU market only (ignores US/UK)
- No intraday updates
- Not used in ongoing decisions

### Required State ✅

- **Real-time sentiment** (updates every 5-15 min)
- **Global multi-market** (US 50%, UK 25%, AU 25%)
- **Dynamic throughout day** (responds to market movements)
- **Integrated in trading** (affects every buy/sell decision)

### Implementation Steps

1. ✅ Create `RealtimeMarketSentiment` class
2. ✅ Integrate with `paper_trading_coordinator.py`
3. ✅ Update trading cycle to recalculate each iteration
4. ✅ Enhance dashboard with real-time display
5. ✅ Add sentiment gates (BLOCK/REDUCE/BOOST)
6. ✅ Add detailed logging for sentiment changes

---

**Status**: User requirement CONFIRMED  
**Priority**: HIGH (core trading logic)  
**Implementation**: Ready to code  
**Estimated Time**: 2-3 hours (full implementation + testing)
