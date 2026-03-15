# Unified FinBERT v4.4.4 Sentiment Integration - Complete Analysis

## Current Architecture Discovery

### ✅ **GOOD NEWS: Overnight Pipelines ALREADY Use FinBERT v4.4.4!**

**Discovery:** The overnight pipelines (AU/UK/US) ARE using FinBERT v4.4.4 through `finbert_bridge.py`

**File:** `models/screening/finbert_bridge.py`

```python
# Line 78-84: Imports FinBERT v4.4.4 sentiment analyzer
from finbert_sentiment import FinBERTSentimentAnalyzer
SENTIMENT_ANALYZER_AVAILABLE = True

# Line 148: Initializes with same model as standalone FinBERT
self.sentiment_analyzer = FinBERTSentimentAnalyzer(model_name="ProsusAI/finbert")
```

**File:** `models/screening/batch_predictor.py`

```python
# Line 507-515: Uses REAL FinBERT for every stock
if self.finbert_bridge and self.finbert_components['sentiment_available']:
    sentiment_result = self.finbert_bridge.get_sentiment_analysis(symbol)
    # Returns: negative/neutral/positive scores + compound + confidence
```

---

## The THREE Problems

### Problem 1: FinBERT Bridge May Not Be Connecting ⚠️

**Why Your Negative Sentiment Wasn't Showing:**

```
FinBERT v4.4.4 Path Detection:
1. Try: C:\Users\david\AATelS\finbert_v4.4.4
2. Try: ../finbert_v4.4.4
3. If NOT found → Falls back to SPI sentiment (gap prediction only)
```

**Result:** If path detection fails, overnight pipelines use **SPI gap prediction** instead of FinBERT sentiment.

---

### Problem 2: Unified Trading Platform Uses DIFFERENT FinBERT ❌

**File:** `ml_pipeline/swing_signal_generator.py`

- Uses `ml_pipeline` FinBERT (separate implementation)
- NOT connected to FinBERT v4.4.4
- Different sentiment scores
- Different model weights

---

### Problem 3: No Connection Between Overnight + Real-Time Trading ❌

```
Overnight Pipeline (FinBERT v4.4.4)
    ↓
  au_morning_report.json
    ↓
  ❌ NOT READ ❌
    ↓
Unified Trading Platform (ml_pipeline FinBERT)
    ↓
  Different sentiment scores!
```

---

## The Unified Solution

### Goal: **ONE** FinBERT v4.4.4 for Everything

```
                    ┌────────────────────────────────┐
                    │   FinBERT v4.4.4 (Single)     │
                    │   finbert_v4.4.4/models/       │
                    │   finbert_sentiment.py         │
                    └────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌─────────────┐ ┌──────────┐ ┌──────────┐
            │ AU Pipeline │ │UK Pipeline│ │US Pipeline│
            └─────────────┘ └──────────┘ └──────────┘
                    │
                    ▼
          au_morning_report.json
          (with FinBERT scores)
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Unified Trading Platform   │
        │  (reads morning report)     │
        └─────────────────────────────┘
```

---

## Implementation Plan

### Step 1: Fix FinBERT Bridge Path Detection ✅

**Current Issue:** Hardcoded path may fail

**Solution:** Make path configurable + better detection

```python
# finbert_bridge.py - Enhanced path detection
def _find_finbert_path():
    """Find FinBERT v4.4.4 installation with multiple fallbacks"""
    
    # Priority 1: Environment variable
    if 'FINBERT_PATH' in os.environ:
        path = Path(os.environ['FINBERT_PATH'])
        if path.exists():
            return path
    
    # Priority 2: User-specified (AATelS)
    path = Path(r'C:\Users\david\AATelS\finbert_v4.4.4')
    if path.exists():
        return path
    
    # Priority 3: Same directory as complete_backend
    path = Path(__file__).parent.parent.parent / 'finbert_v4.4.4'
    if path.exists():
        return path
    
    # Priority 4: Current working directory
    path = Path.cwd() / 'finbert_v4.4.4'
    if path.exists():
        return path
    
    # Priority 5: Parent of current directory
    path = Path.cwd().parent / 'finbert_v4.4.4'
    if path.exists():
        return path
    
    raise FileNotFoundError(
        "FinBERT v4.4.4 not found. Please set FINBERT_PATH environment variable "
        "or place finbert_v4.4.4 in the project directory."
    )
```

---

### Step 2: Enhance FinBERT Bridge to Return Full Sentiment Breakdown ✅

**Current:** Returns simple direction + confidence

**Enhancement:** Return full FinBERT v4.4.4 format

```python
# finbert_bridge.py - Enhanced get_sentiment_analysis()
def get_sentiment_analysis(self, symbol: str, use_cache: bool = True) -> Dict:
    """
    Get comprehensive FinBERT sentiment analysis
    
    Returns:
        {
            'symbol': 'CBA.AX',
            'sentiment': 'negative',           # negative/neutral/positive
            'confidence': 72.5,                 # 0-100
            'scores': {
                'negative': 0.725,              # ← YOUR SCREENSHOT
                'neutral': 0.225,
                'positive': 0.050
            },
            'compound': -0.675,                 # -1 to +1
            'direction': -0.675,                # For backward compat
            'article_count': 8,
            'method': 'FinBERT v4.4.4',
            'timestamp': '2026-01-28T...'
        }
    """
    if not self._sentiment_initialized:
        return None
    
    try:
        # Get news for symbol
        news_items = self._get_news_for_symbol(symbol, max_items=10)
        
        if not news_items or len(news_items) == 0:
            return None
        
        # Analyze with FinBERT v4.4.4
        news_texts = [item.get('title', '') + ' ' + item.get('summary', '') 
                     for item in news_items]
        
        sentiment = self.sentiment_analyzer.analyze_news_batch(news_texts)
        
        # Add metadata
        sentiment['symbol'] = symbol
        sentiment['article_count'] = len(news_items)
        sentiment['direction'] = sentiment['compound']  # Backward compat
        
        return sentiment
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed for {symbol}: {e}")
        return None
```

---

### Step 3: Update Overnight Pipelines to Save Full FinBERT Scores ✅

**File:** `models/screening/overnight_pipeline.py`

**Enhancement:** Save complete FinBERT breakdown in morning report

```python
# overnight_pipeline.py - Enhanced _finalize_pipeline()
def _finalize_pipeline(self, scored_stocks, spi_sentiment, report_path):
    """Save results with full FinBERT sentiment breakdown"""
    
    # ... existing code ...
    
    # NEW: Add FinBERT sentiment summary to report
    finbert_summary = self._calculate_finbert_summary(scored_stocks)
    
    results = {
        'status': 'success',
        'timestamp': datetime.now(self.timezone).isoformat(),
        'summary': summary,
        'spi_sentiment': spi_sentiment,
        
        # NEW: Full FinBERT breakdown
        'finbert_sentiment': {
            'overall_scores': {
                'negative': finbert_summary['avg_negative'],
                'neutral': finbert_summary['avg_neutral'],
                'positive': finbert_summary['avg_positive']
            },
            'compound': finbert_summary['avg_compound'],
            'sentiment_label': finbert_summary['dominant_sentiment'],
            'confidence': finbert_summary['avg_confidence'],
            'stocks_analyzed': finbert_summary['count'],
            'method': 'FinBERT v4.4.4'
        },
        
        'top_opportunities': top_opps_detailed,
        'report_path': str(report_path)
    }
    
    # Save to au_morning_report.json
    self._save_trading_report(results, market_code='au')
    
    return results

def _calculate_finbert_summary(self, stocks: List[Dict]) -> Dict:
    """Calculate aggregate FinBERT sentiment from all stocks"""
    
    sentiments = []
    for stock in stocks:
        if 'sentiment_scores' in stock:
            sentiments.append(stock['sentiment_scores'])
    
    if not sentiments:
        return {
            'avg_negative': 0.33,
            'avg_neutral': 0.34,
            'avg_positive': 0.33,
            'avg_compound': 0.0,
            'avg_confidence': 50,
            'dominant_sentiment': 'neutral',
            'count': 0
        }
    
    # Aggregate scores
    avg_negative = np.mean([s.get('negative', 0.33) for s in sentiments])
    avg_neutral = np.mean([s.get('neutral', 0.34) for s in sentiments])
    avg_positive = np.mean([s.get('positive', 0.33) for s in sentiments])
    avg_compound = np.mean([s.get('compound', 0) for s in sentiments])
    avg_confidence = np.mean([s.get('confidence', 50) for s in sentiments])
    
    # Determine dominant
    scores = {
        'negative': avg_negative,
        'neutral': avg_neutral,
        'positive': avg_positive
    }
    dominant = max(scores, key=scores.get)
    
    return {
        'avg_negative': round(avg_negative, 4),
        'avg_neutral': round(avg_neutral, 4),
        'avg_positive': round(avg_positive, 4),
        'avg_compound': round(avg_compound, 4),
        'avg_confidence': round(avg_confidence, 2),
        'dominant_sentiment': dominant,
        'count': len(sentiments)
    }
```

---

### Step 4: Replace ml_pipeline FinBERT with FinBERT v4.4.4 ✅

**File:** `sentiment_integration.py` (already created)

**Enhancement:** Use FinBERT v4.4.4 directly

```python
# sentiment_integration.py - USE FINBERT v4.4.4
try:
    # Import from FinBERT v4.4.4 directory
    import sys
    from pathlib import Path
    
    # Find FinBERT v4.4.4
    finbert_paths = [
        Path(r'C:\Users\david\AATelS\finbert_v4.4.4'),
        Path(__file__).parent / 'finbert_v4.4.4',
        Path.cwd() / 'finbert_v4.4.4'
    ]
    
    finbert_path = None
    for path in finbert_paths:
        if path.exists():
            finbert_path = path
            break
    
    if finbert_path:
        sys.path.insert(0, str(finbert_path / 'models'))
        from finbert_sentiment import FinBERTSentimentAnalyzer
        FINBERT_AVAILABLE = True
        logger.info(f"[FINBERT v4.4.4] Loaded from {finbert_path}")
    else:
        raise ImportError("FinBERT v4.4.4 not found")
        
except ImportError:
    FINBERT_AVAILABLE = False
    logger.warning("[FINBERT] FinBERT v4.4.4 not available")
```

---

### Step 5: Update Unified Trading Dashboard to Display FinBERT Breakdown ✅

**File:** `unified_trading_dashboard.py`

**New Panel:** FinBERT Sentiment Breakdown (like your screenshot)

```python
# unified_trading_dashboard.py - Add FinBERT sentiment panel
html.Div([
    html.H3('[🎯] FinBERT Sentiment Analysis', 
            style={'color': '#FF9800', 'margin': '0 0 15px 0'}),
    
    # Overall sentiment
    html.Div([
        html.P(id='finbert-overall-sentiment', 
               style={'fontSize': '36px', 'fontWeight': 'bold', 'margin': '0'}),
        html.P(id='finbert-sentiment-label',
               style={'color': '#888', 'fontSize': '14px', 'margin': '5px 0 20px 0'})
    ]),
    
    # Sentiment bars (like your screenshot)
    html.Div([
        # Negative bar
        html.Div([
            html.Span('Negative', style={'display': 'inline-block', 'width': '80px'}),
            html.Div(id='finbert-negative-bar', style={
                'display': 'inline-block',
                'backgroundColor': '#F44336',
                'height': '20px',
                'verticalAlign': 'middle'
            }),
            html.Span(id='finbert-negative-pct', 
                     style={'marginLeft': '10px', 'color': '#F44336'})
        ], style={'marginBottom': '10px'}),
        
        # Neutral bar
        html.Div([
            html.Span('Neutral', style={'display': 'inline-block', 'width': '80px'}),
            html.Div(id='finbert-neutral-bar', style={
                'display': 'inline-block',
                'backgroundColor': '#FFC107',
                'height': '20px',
                'verticalAlign': 'middle'
            }),
            html.Span(id='finbert-neutral-pct',
                     style={'marginLeft': '10px', 'color': '#FFC107'})
        ], style={'marginBottom': '10px'}),
        
        # Positive bar
        html.Div([
            html.Span('Positive', style={'display': 'inline-block', 'width': '80px'}),
            html.Div(id='finbert-positive-bar', style={
                'display': 'inline-block',
                'backgroundColor': '#4CAF50',
                'height': '20px',
                'verticalAlign': 'middle'
            }),
            html.Span(id='finbert-positive-pct',
                     style={'marginLeft': '10px', 'color': '#4CAF50'})
        ])
    ]),
    
    # Metadata
    html.P(id='finbert-metadata',
           style={'color': '#888', 'fontSize': '12px', 'marginTop': '15px'})
    
], style={
    'backgroundColor': '#2a2a2a',
    'padding': '20px',
    'borderRadius': '10px',
    'marginBottom': '20px'
})

# Callback to update FinBERT sentiment
@app.callback(
    [Output('finbert-overall-sentiment', 'children'),
     Output('finbert-sentiment-label', 'children'),
     Output('finbert-negative-bar', 'style'),
     Output('finbert-negative-pct', 'children'),
     Output('finbert-neutral-bar', 'style'),
     Output('finbert-neutral-pct', 'children'),
     Output('finbert-positive-bar', 'style'),
     Output('finbert-positive-pct', 'children'),
     Output('finbert-metadata', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_finbert_sentiment(n):
    """Update FinBERT sentiment display from morning report"""
    
    try:
        # Load morning report
        report_path = Path('reports/screening/au_morning_report.json')
        
        if not report_path.exists():
            return (
                "N/A", "No morning report available",
                {'display': 'none'}, "0%",
                {'display': 'none'}, "0%",
                {'display': 'none'}, "0%",
                "Run overnight pipeline to generate sentiment"
            )
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        # Extract FinBERT sentiment
        finbert = report.get('finbert_sentiment', {})
        scores = finbert.get('overall_scores', {})
        
        negative = scores.get('negative', 0.33) * 100
        neutral = scores.get('neutral', 0.34) * 100
        positive = scores.get('positive', 0.33) * 100
        
        compound = finbert.get('compound', 0)
        sentiment_label = finbert.get('sentiment_label', 'neutral').upper()
        confidence = finbert.get('confidence', 50)
        stocks_analyzed = finbert.get('stocks_analyzed', 0)
        
        # Overall sentiment score (0-100)
        overall = (compound + 1) * 50  # Convert -1...+1 to 0...100
        
        # Color based on compound
        if compound < -0.2:
            color = '#F44336'  # Red
        elif compound > 0.2:
            color = '#4CAF50'  # Green
        else:
            color = '#FFC107'  # Yellow
        
        # Bar widths (max 300px)
        neg_width = int(negative * 3)
        neu_width = int(neutral * 3)
        pos_width = int(positive * 3)
        
        return (
            f"{overall:.1f}",
            f"{sentiment_label} (Confidence: {confidence:.1f}%)",
            {'display': 'inline-block', 'backgroundColor': '#F44336', 
             'height': '20px', 'width': f'{neg_width}px', 'verticalAlign': 'middle'},
            f"{negative:.1f}%",
            {'display': 'inline-block', 'backgroundColor': '#FFC107',
             'height': '20px', 'width': f'{neu_width}px', 'verticalAlign': 'middle'},
            f"{neutral:.1f}%",
            {'display': 'inline-block', 'backgroundColor': '#4CAF50',
             'height': '20px', 'width': f'{pos_width}px', 'verticalAlign': 'middle'},
            f"{positive:.1f}%",
            f"FinBERT v4.4.4 | {stocks_analyzed} stocks analyzed | "
            f"Generated: {report.get('generated_at', 'N/A')}"
        )
        
    except Exception as e:
        logger.error(f"Error updating FinBERT sentiment: {e}")
        return (
            "Error", str(e),
            {'display': 'none'}, "0%",
            {'display': 'none'}, "0%",
            {'display': 'none'}, "0%",
            "Error loading sentiment"
        )
```

---

## Testing Plan

### Test 1: Verify FinBERT v4.4.4 Path Detection

```bash
cd C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
python -c "from models.screening.finbert_bridge import get_finbert_bridge; bridge = get_finbert_bridge(); print(bridge.is_available())"
```

**Expected Output:**
```
[OK] Using FinBERT from: C:\Users\david\AATelS\finbert_v4.4.4
[OK] LSTM predictor imported successfully
[OK] FinBERT sentiment analyzer imported successfully
{'lstm_available': True, 'sentiment_available': True, 'news_available': True}
```

---

### Test 2: Run Overnight Pipeline with FinBERT v4.4.4

```bash
python run_au_pipeline.py --full-scan --capital 100000
```

**Check logs for:**
```
[OK] Using REAL FinBERT sentiment for CBA.AX: negative (72.5%), 8 articles
[OK] Using REAL FinBERT sentiment for BHP.AX: neutral (55.2%), 5 articles
```

**Check morning report:**
```bash
type reports\screening\au_morning_report.json | findstr "finbert_sentiment"
```

**Expected:**
```json
"finbert_sentiment": {
    "overall_scores": {
        "negative": 0.6500,
        "neutral": 0.2500,
        "positive": 0.1000
    },
    "compound": -0.5500,
    "sentiment_label": "negative",
    "confidence": 72.5,
    "stocks_analyzed": 240,
    "method": "FinBERT v4.4.4"
}
```

---

### Test 3: Verify Unified Trading Platform Respects Sentiment

```bash
python unified_trading_dashboard.py --symbols CBA.AX,BHP.AX --capital 100000
```

**Expected behavior when sentiment is negative (65%):**
```
[SENTIMENT] Loaded AU morning report: 35.0/100 (AVOID)
[BLOCK] CBA.AX: Market recommendation is AVOID
[BLOCK] BHP.AX: Market recommendation is AVOID
[INFO] No positions opened due to negative sentiment
```

---

## Summary of Changes

### Files to Modify:

1. **`models/screening/finbert_bridge.py`**
   - Enhanced path detection
   - Return full FinBERT breakdown

2. **`models/screening/overnight_pipeline.py`**
   - Save full FinBERT scores in morning report
   - Add `_calculate_finbert_summary()` method

3. **`sentiment_integration.py`**
   - Use FinBERT v4.4.4 directly
   - Remove ml_pipeline dependency

4. **`paper_trading_coordinator.py`**
   - Use sentiment_integration module
   - Respect morning report sentiment gates

5. **`unified_trading_dashboard.py`**
   - Add FinBERT sentiment panel
   - Display negative/neutral/positive breakdown
   - Show sentiment bars (like your screenshot)

---

## Benefits

### ✅ **ONE** FinBERT v4.4.4 for Everything

- AU Pipeline → FinBERT v4.4.4 ✅
- UK Pipeline → FinBERT v4.4.4 ✅
- US Pipeline → FinBERT v4.4.4 ✅
- Unified Trading → FinBERT v4.4.4 ✅

### ✅ Consistent Sentiment Scores

- Same negative/neutral/positive breakdown everywhere
- Same compound scores
- Same confidence metrics

### ✅ Respects Negative Sentiment

- When FinBERT shows 65% negative → **NO TRADES**
- Sentiment gates prevent losses
- Dashboard shows WHY trades were blocked

---

## Next Action

Should I implement all 5 file modifications now? This will:

1. ✅ Fix FinBERT path detection
2. ✅ Save full sentiment breakdown in morning reports  
3. ✅ Connect unified trading to FinBERT v4.4.4
4. ✅ Add sentiment display panel (like your screenshot)
5. ✅ Block trades when sentiment is negative

**Estimated time:** 45 minutes
**Result:** Unified FinBERT v4.4.4 across all components

Proceed? 🚀
