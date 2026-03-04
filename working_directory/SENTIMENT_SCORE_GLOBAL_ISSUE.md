# SENTIMENT SCORE ISSUE - Unified Trading Dashboard

**Date**: 2026-01-29  
**Issue**: Market sentiment in Unified Trading Dashboard is based ONLY on AU market (FTSE 100 not included)  
**User Report**: "The sentiment score in the unified trading interface shouldn't just be based on ftse 100."

---

## Current Problem

### What's Happening Now

**File**: `paper_trading_coordinator.py`  
**Function**: `get_market_sentiment()` (line 375)  
**Issue**: Hardcoded to load **ONLY Australian market** sentiment

```python
# Line 391 - HARDCODED TO 'au' ONLY
morning_data = self.sentiment_analyzer.load_morning_sentiment(market='au')
```

**Result**: 
- ✅ Loads AU market sentiment (SPI 200, ASX)
- ❌ Ignores US market sentiment (S&P 500, NASDAQ, Dow)
- ❌ Ignores UK market sentiment (FTSE 100, VFTSE, GBP/USD)

### User's Expectation (Correct)

The sentiment score should be a **GLOBAL multi-market sentiment** that considers:
- 🇦🇺 AU Market (ASX, SPI 200)
- 🇺🇸 US Market (S&P 500, NASDAQ, Dow) ← **Most important (50% weight)**
- 🇬🇧 UK Market (FTSE 100, VFTSE) ← **Missing from current calculation**

---

## Why This Matters

### Market Influence Hierarchy

In reality, global markets have **different levels of influence**:

1. **US Markets** (50% weight)
   - S&P 500, NASDAQ, Dow Jones
   - **Dominant** global market mover
   - US session moves set tone for next day

2. **UK/European Markets** (25% weight)
   - FTSE 100, DAX, CAC
   - Bridge between Asian and US sessions
   - Influences both AU and US opening

3. **AU/Asian Markets** (25% weight)
   - ASX, Nikkei, Hang Seng
   - First to open in trading day
   - Reacts to overnight US close

### Current vs Expected

**Current Calculation**:
```
Global Sentiment = AU Sentiment (100%)
                 = SPI 200 only
```

**Expected Calculation**:
```
Global Sentiment = (US Sentiment × 0.50) +    [S&P 500, NASDAQ, Dow]
                   (UK Sentiment × 0.25) +    [FTSE 100, VFTSE]
                   (AU Sentiment × 0.25)      [SPI 200, ASX]
```

---

## Example of the Issue

### Scenario: US Bearish, UK Neutral, AU Bullish

**Real Market State**:
- 🇺🇸 US: S&P 500 -1.5%, NASDAQ -2.0% → Sentiment: 30/100 (Bearish)
- 🇬🇧 UK: FTSE 100 +0.2%, VFTSE 15 → Sentiment: 52/100 (Neutral)
- 🇦🇺 AU: SPI 200 +0.8%, ASX +1.0% → Sentiment: 65/100 (Bullish)

**Current Dashboard Display**:
```
Market Sentiment: 65.0 (BULLISH)  ← WRONG! Only shows AU
```

**Expected Dashboard Display**:
```
Global Sentiment = (30 × 0.50) + (52 × 0.25) + (65 × 0.25)
                 = 15 + 13 + 16.25
                 = 44.25 (NEUTRAL to SLIGHTLY BEARISH)
                 
Market Sentiment: 44.3 (NEUTRAL)  ← CORRECT! Considers all markets
```

**Impact**: Current dashboard shows BULLISH when global markets are actually NEUTRAL/BEARISH.

---

## The Fix

### Solution: Multi-Market Sentiment Aggregator

Create a new function that loads **all three markets** and calculates weighted sentiment:

```python
def get_market_sentiment(self) -> float:
    """
    Get current GLOBAL market sentiment (0-100)
    
    **Enhanced**: Multi-market aggregation (AU/US/UK)
    
    Weighting:
    - US Markets: 50% (dominant global influence)
    - UK Markets: 25% (bridge session)
    - AU Markets: 25% (first to open)
    
    Returns:
        Global sentiment score (0-100)
    """
    # Try to load all three markets
    sentiments = {}
    
    if self.sentiment_analyzer:
        try:
            # Load all available morning reports
            for market_code in ['au', 'us', 'uk']:
                morning_data = self.sentiment_analyzer.load_morning_sentiment(market=market_code)
                if morning_data:
                    sentiments[market_code] = {
                        'score': morning_data['overall_sentiment'],
                        'recommendation': morning_data['recommendation'],
                        'confidence': morning_data.get('confidence', 'MODERATE')
                    }
                    logger.info(f"[SENTIMENT] {market_code.upper()}: {morning_data['overall_sentiment']:.1f}/100 "
                               f"({morning_data['recommendation']})")
            
            # Calculate weighted global sentiment if we have multiple markets
            if len(sentiments) > 0:
                # Define market weights
                weights = {
                    'us': 0.50,  # US markets most influential
                    'uk': 0.25,  # UK/Europe bridge session
                    'au': 0.25   # AU/Asia first to open
                }
                
                # Calculate weighted average
                total_weight = 0
                weighted_sentiment = 0
                
                for market_code, data in sentiments.items():
                    weight = weights.get(market_code, 0.25)
                    weighted_sentiment += data['score'] * weight
                    total_weight += weight
                
                # Normalize if not all markets available
                if total_weight > 0:
                    global_sentiment = weighted_sentiment / total_weight
                else:
                    global_sentiment = 50.0  # Neutral default
                
                # Store for decision making
                self.last_market_sentiment = global_sentiment
                self.multi_market_breakdown = sentiments
                
                logger.info(f"[SENTIMENT] GLOBAL (weighted): {global_sentiment:.1f}/100")
                logger.info(f"            Markets: {len(sentiments)}/3 available")
                
                return global_sentiment
            else:
                logger.info("[SENTIMENT] No morning reports available, using SPY fallback")
                
        except Exception as e:
            logger.warning(f"[SENTIMENT] Error loading morning reports: {e}, using SPY fallback")
    
    # Fallback to SPY-based sentiment (original logic)
    # ... (rest of existing SPY fallback code)
```

### Alternative: Smart Market Selection

If you want to **prioritize by trading hours** instead of fixed weights:

```python
def get_market_sentiment_by_time(self) -> float:
    """
    Get market sentiment based on current trading hours
    
    Priority:
    1. If US market open (14:30-21:00 GMT): Use US sentiment (primary)
    2. If UK market open (08:00-16:30 GMT): Use UK sentiment (primary)
    3. If AU market open (23:00-06:00 GMT): Use AU sentiment (primary)
    4. If multiple markets open: Use weighted average
    5. If all closed: Use most recent available
    
    Returns:
        Context-aware sentiment score (0-100)
    """
    from datetime import datetime
    import pytz
    
    # Get current time in GMT
    now_gmt = datetime.now(pytz.timezone('GMT'))
    current_hour = now_gmt.hour
    
    # Determine which markets are currently open
    markets_open = []
    
    # US Market: 14:30-21:00 GMT (9:30-16:00 EST)
    if 14 <= current_hour < 21:
        markets_open.append(('us', 0.60))  # Higher weight when open
    
    # UK Market: 08:00-16:30 GMT
    if 8 <= current_hour < 17:
        markets_open.append(('uk', 0.50))
    
    # AU Market: 23:00-06:00 GMT (spans midnight)
    if current_hour >= 23 or current_hour < 6:
        markets_open.append(('au', 0.40))
    
    # If no markets open, use default weighting
    if not markets_open:
        markets_open = [('us', 0.50), ('uk', 0.25), ('au', 0.25)]
    
    # Load sentiment for open markets
    sentiments = {}
    
    if self.sentiment_analyzer:
        for market_code, weight in markets_open:
            morning_data = self.sentiment_analyzer.load_morning_sentiment(market=market_code)
            if morning_data:
                sentiments[market_code] = {
                    'score': morning_data['overall_sentiment'],
                    'weight': weight
                }
    
    # Calculate weighted sentiment
    if sentiments:
        weighted_sum = sum(data['score'] * data['weight'] for data in sentiments.values())
        total_weight = sum(data['weight'] for data in sentiments.values())
        global_sentiment = weighted_sum / total_weight if total_weight > 0 else 50.0
        
        logger.info(f"[SENTIMENT] Context-aware: {global_sentiment:.1f}/100 (using {len(sentiments)} markets)")
        return global_sentiment
    
    # Fallback to SPY
    return self.fallback_spy_sentiment()
```

---

## Dashboard Display Enhancement

### Current Display

```
┌─────────────────────────┐
│   Market Sentiment      │
│        65.0             │  ← Only AU market
│      BULLISH            │
└─────────────────────────┘
```

### Enhanced Display (Recommended)

```
┌─────────────────────────────────────────┐
│   Global Market Sentiment               │
│           44.3                          │
│         NEUTRAL                         │
│                                         │
│   Breakdown:                            │
│   🇺🇸 US: 30.0 (BEARISH)    [50%]      │
│   🇬🇧 UK: 52.0 (NEUTRAL)    [25%]      │
│   🇦🇺 AU: 65.0 (BULLISH)    [25%]      │
└─────────────────────────────────────────┘
```

**UI Implementation**:
```python
# In unified_trading_dashboard.py, update sentiment display

# Show global sentiment with breakdown
html.Div([
    html.Div(f"{global_sentiment:.1f}", style={'fontSize': '48px', 'fontWeight': 'bold'}),
    html.Div(sentiment_class, style={'fontSize': '18px', 'color': sentiment_color}),
    
    # Add market breakdown
    html.Div([
        html.H4('Regional Breakdown:', style={'marginTop': '20px', 'fontSize': '14px'}),
        
        # US Market
        html.Div([
            html.Span('🇺🇸 US: ', style={'fontSize': '12px'}),
            html.Span(f"{us_sentiment:.1f}", style={'fontWeight': 'bold'}),
            html.Span(f" ({us_label})", style={'color': us_color}),
            html.Span(' [50%]', style={'color': '#888', 'fontSize': '11px'})
        ]),
        
        # UK Market
        html.Div([
            html.Span('🇬🇧 UK: ', style={'fontSize': '12px'}),
            html.Span(f"{uk_sentiment:.1f}", style={'fontWeight': 'bold'}),
            html.Span(f" ({uk_label})", style={'color': uk_color}),
            html.Span(' [25%]', style={'color': '#888', 'fontSize': '11px'})
        ]),
        
        # AU Market
        html.Div([
            html.Span('🇦🇺 AU: ', style={'fontSize': '12px'}),
            html.Span(f"{au_sentiment:.1f}", style={'fontWeight': 'bold'}),
            html.Span(f" ({au_label})", style={'color': au_color}),
            html.Span(' [25%]', style={'fontSize': '11px'})
        ])
    ], style={'marginTop': '15px', 'borderTop': '1px solid #333', 'paddingTop': '10px'})
])
```

---

## Implementation Priority

### Option 1: Fixed Weighted Average (Recommended)

**Pros**:
- Simple, predictable
- Reflects market influence accurately
- Easy to understand

**Cons**:
- Doesn't adapt to market hours

**Best for**: General trading across all sessions

### Option 2: Time-Aware Weighting

**Pros**:
- More responsive during trading hours
- Higher weight to active markets

**Cons**:
- More complex logic
- Behavior changes by time of day

**Best for**: Intraday trading focused on current session

### Option 3: Hybrid Approach

**Use**:
- **Fixed weights** for overnight/morning decision making
- **Time-aware** for intraday real-time updates

**Best for**: Full 24-hour trading system

---

## Testing the Fix

### Test Case 1: All Markets Available

**Setup**:
- Run all three overnight pipelines (AU, US, UK)
- All morning reports exist and recent

**Expected**:
```
[SENTIMENT] AU: 65.0/100 (BUY)
[SENTIMENT] US: 30.0/100 (CAUTION)
[SENTIMENT] UK: 52.0/100 (HOLD)
[SENTIMENT] GLOBAL (weighted): 44.3/100
```

### Test Case 2: Only US Available

**Setup**:
- Only US morning report exists

**Expected**:
```
[SENTIMENT] US: 30.0/100 (CAUTION)
[SENTIMENT] GLOBAL (weighted): 30.0/100
[SENTIMENT] Markets: 1/3 available
```

### Test Case 3: No Reports Available

**Setup**:
- No morning reports exist

**Expected**:
```
[SENTIMENT] No morning reports available, using SPY fallback
[SENTIMENT] Using SPY-based sentiment
[SENTIMENT] SPY: 55.0/100 (NEUTRAL)
```

---

## Impact Analysis

### Current State

**Users see**: AU-only sentiment (misleading if AU bullish but US bearish)  
**Decision quality**: Poor (ignores 75% of global markets)  
**User trust**: Low (sentiment doesn't match global market reality)

### After Fix

**Users see**: Global multi-market sentiment (accurate global picture)  
**Decision quality**: High (considers all major markets with proper weighting)  
**User trust**: High (sentiment matches observed market conditions)

---

## Recommended Action

### Immediate Fix

**Replace line 391** in `paper_trading_coordinator.py`:

```python
# OLD (AU-only)
morning_data = self.sentiment_analyzer.load_morning_sentiment(market='au')

# NEW (Multi-market)
sentiments = {}
for market_code in ['au', 'us', 'uk']:
    market_data = self.sentiment_analyzer.load_morning_sentiment(market=market_code)
    if market_data:
        sentiments[market_code] = market_data['overall_sentiment']

# Calculate weighted global sentiment
weights = {'us': 0.50, 'uk': 0.25, 'au': 0.25}
if sentiments:
    global_sentiment = sum(sentiments.get(m, 50) * w for m, w in weights.items() if m in sentiments)
    total_weight = sum(w for m, w in weights.items() if m in sentiments)
    sentiment_score = global_sentiment / total_weight if total_weight > 0 else 50.0
else:
    sentiment_score = None  # Trigger SPY fallback
```

### Dashboard Update

Update `unified_trading_dashboard.py` to show **regional breakdown** alongside global sentiment.

---

## Summary

**Current Issue**: ✅ User is correct - sentiment is AU-only, not global

**Expected Behavior**: Global sentiment with US 50%, UK 25%, AU 25% weighting

**Fix Required**: Yes - update `get_market_sentiment()` to aggregate all three markets

**Priority**: MEDIUM-HIGH (affects trading decisions, but current AU sentiment is valid)

**Estimated Fix Time**: 30-45 minutes (code + testing)

---

**Status**: ISSUE CONFIRMED  
**User Observation**: CORRECT  
**Fix**: Multi-market sentiment aggregation required  
**Next Step**: Implement weighted global sentiment calculation
