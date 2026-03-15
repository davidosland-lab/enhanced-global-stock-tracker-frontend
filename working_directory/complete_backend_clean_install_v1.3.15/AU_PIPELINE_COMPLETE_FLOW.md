# AU Pipeline Complete Flow - Detailed Documentation
**Date**: January 3, 2026  
**Version**: 1.0.0  
**Status**: Production-Ready ✅

## Executive Summary

The AU (Australia) Pipeline implements a **sophisticated multi-stage filtering system** that scans 240 stocks and returns only high-quality opportunities that meet stringent scoring thresholds. This document explains why **only a few stocks (sometimes none) reach the buy threshold**.

---

## Complete Pipeline Flow

### Stage 1: Stock Scanning (240 Stocks)
**Module**: `stock_scanner.py`  
**Method**: `scan_all_sectors(top_n_per_sector=30)`

```
Input: 8 Sectors × 30 Stocks = 240 Total Stocks
├── Financials (30 stocks)
├── Materials (30 stocks)
├── Healthcare (30 stocks)
├── Technology (30 stocks)
├── Energy (30 stocks)
├── Industrials (30 stocks)
├── Consumer_Discretionary (30 stocks)
└── Consumer_Staples (30 stocks)
```

**Validation Criteria (First Filter)**:
- **Min Price**: $0.50
- **Max Price**: $500.00
- **Min Avg Volume**: 500,000 shares/day
- **Min Market Cap**: $500M

**Result**: ~180-200 stocks pass validation (40-60 filtered out for low liquidity/price)

---

### Stage 2: Technical Analysis & Scoring (0-100)
**Module**: `stock_scanner.py`  
**Method**: `analyze_stock(symbol, sector_weight)`

Each validated stock receives a **screening score (0-100)** based on:

1. **Price vs Moving Averages** (35%)
   - Above MA20: +35 points
   - Above MA50: bonus points
   - Golden cross: bonus points

2. **RSI Analysis** (25%)
   - RSI 40-60 (optimal): +25 points
   - RSI 30-40 (oversold, opportunity): +20 points
   - RSI 60-70: +15 points
   - RSI >70 (overbought): +5 points

3. **Volatility** (20%)
   - Low volatility (15-25%): +20 points
   - Medium (25-35%): +15 points
   - High (>35%): +5 points

4. **Volume Confirmation** (20%)
   - Volume >500K: +20 points
   - Volume >1M: +25 points

**Result**: All stocks scored 0-100  
**Next Filter**: Only stocks scoring **≥50** proceed to ML prediction

---

### Stage 3: ML Ensemble Prediction
**Module**: `batch_predictor.py`  
**Method**: `predict_batch(stocks)`

**Ensemble Weights**:
- **LSTM Models**: 45% (requires trained model for symbol)
- **Trend Analysis**: 25%
- **Technical Indicators**: 15%
- **FinBERT Sentiment**: 15%

**Predictions Generated**:
- **BUY**: Bullish signal
- **SELL**: Bearish signal
- **HOLD**: Neutral/uncertain

**Confidence Score**: 0-100%

**Important**: If LSTM unavailable → Fallback to trend-based prediction

**Result**: All stocks get prediction + confidence  
**Next Stage**: Opportunity scoring

---

### Stage 4: Opportunity Scoring (0-100)
**Module**: `opportunity_scorer.py`  
**Method**: `score_opportunities(stocks_with_predictions, spi_sentiment)`

**This is the CRITICAL FILTER that determines which stocks appear in reports**

#### Composite Score Calculation (0-100):

**Base Factors** (weighted sum × 100):

1. **Prediction Confidence** (30%)
   - BUY with high confidence: 1.0 × 1.2 = 1.2 → 36 points
   - SELL with high confidence: 1.0 × 0.8 = 0.8 → 24 points
   - HOLD: 0.5 → 15 points

2. **Technical Strength** (20%)
   - Screening score + RSI + MA alignment
   - Max 20 points

3. **SPI Alignment** (15%)
   - Stock BUY + Market Bullish: 15 points
   - Stock SELL + Market Bearish: 15 points
   - Misalignment: 4.5 points

4. **Liquidity** (15%)
   - Volume >5M: 15 points
   - Volume 2-5M: 12 points
   - Volume 1-2M: 9 points

5. **Volatility** (10%)
   - Low volatility preferred: 10 points
   - High volatility: 3 points

6. **Sector Momentum** (10%)
   - Sector performance: 0-10 points

**Adjustments** (Penalties & Bonuses):
- **Penalties**: -10 to -20 points
  - Low volume: -10
  - High volatility: -15
  - Negative sentiment: -20
  
- **Bonuses**: +5 to +10 points
  - Fresh LSTM model: +5
  - High win rate: +10
  - Sector leader: +5

**Final Score**: Max(0, Min(100, base_total + adjustments))

---

### Stage 5: Threshold Filtering
**Module**: `opportunity_scorer.py` + `report_generator.py`

**Configuration** (from `screening_config.json`):
```json
{
  "screening": {
    "opportunity_threshold": 65,
    "top_picks_count": 10,
    "min_confidence_score": 60
  }
}
```

**Filter Logic**:
1. **First Filter**: Opportunity Score ≥ 65/100
2. **Second Filter**: Only BUY signals (report builder preference)
3. **Third Filter**: Confidence ≥ 60%

**Result**: Only stocks passing ALL three filters appear in report

---

## Why Few Stocks Meet Threshold

### Threshold 65/100 Analysis

To reach 65/100, a stock needs:

**Example 1 (Minimal Pass - 65 points)**:
- Prediction: BUY (75% conf) → 27 points (30% × 0.9)
- Technical: Good (80/100) → 16 points (20% × 0.8)
- SPI Alignment: Aligned → 15 points
- Liquidity: Medium → 9 points (15% × 0.6)
- Volatility: Low → 8 points (10% × 0.8)
- Sector: Neutral → 5 points (10% × 0.5)
- **Subtotal**: 80 points
- **Penalties**: -15 (high vol, low volume)
- **Final**: 65/100 ✅

**Example 2 (Fails - 58 points)**:
- Prediction: HOLD (60% conf) → 9 points (30% × 0.3)
- Technical: Fair (65/100) → 13 points
- SPI Alignment: Misaligned → 4.5 points
- Liquidity: Low → 6 points
- Volatility: High → 3 points
- Sector: Weak → 3 points
- **Subtotal**: 38.5 points
- **Bonuses**: +10 (high win rate)
- **Final**: 48.5/100 ❌

---

## Realistic Outcomes

### Typical Overnight Screening Results

**240 Stocks Scanned**:
- **Validated**: 180 stocks (price/volume pass)
- **Scored >50**: 120 stocks (proceed to ML)
- **ML Predictions**: 120 stocks
  - BUY: 25 (21%)
  - HOLD: 75 (62%)
  - SELL: 20 (17%)
- **Opportunity Score ≥65**: 8-15 stocks
- **Final Report (BUY + 65+)**: **3-8 stocks** 🎯

**Common Scenarios**:
1. **Bullish Market Day**: 8-12 stocks in report
2. **Normal Day**: 4-6 stocks in report
3. **Bearish/Uncertain Day**: 1-3 stocks (or zero)
4. **High Volatility**: 0-2 stocks (volatility penalties)

---

## Score Distribution Example

From 240 stocks processed:

```
Score Range    Count    Percentage    Prediction
-----------    -----    ----------    ----------
90-100         0        0%            STRONG BUY (very rare)
80-89          2        0.8%          BUY (high confidence)
65-79          6        2.5%          BUY (threshold)
50-64          35       14.6%         Mixed (below threshold)
40-49          45       18.8%         Mostly HOLD
30-39          50       20.8%         HOLD/SELL
0-29           102      42.5%         WEAK/SELL
```

**Result**: 8 stocks score ≥65 (3.3% of 240)  
**Report shows**: 6 BUY signals (2 were SELL)

---

## SELL Recommendations

**When do SELL signals appear?**

A stock can score ≥65 with SELL prediction if:
1. **High Confidence SELL** (80%+): 24 base points (30% × 0.8)
2. **Bearish Market Alignment**: +15 points
3. **Strong Technical Weakness**: Technical indicators confirm downtrend
4. **High Liquidity**: Easy to exit position

**Example SELL Signal (68/100)**:
```
Prediction: SELL (85% confidence) → 26 points
Technical: Weak but clear (70/100) → 14 points
SPI Alignment: Bearish market → 15 points
Liquidity: High volume → 12 points
Volatility: Low → 8 points
Sector: Weak → 3 points
Total: 78 points
Penalties: -10 (negative sentiment)
Final: 68/100 ✅ SELL
```

**Outcome**: Report may show 5 BUY + 1 SELL recommendations

---

## Configuration Tuning

### To Increase Opportunities (More Stocks in Report)

**Option 1**: Lower threshold in `screening_config.json`
```json
"opportunity_threshold": 60  // Was 65
```

**Option 2**: Adjust weights (favor prediction)
```json
"weights": {
  "prediction_confidence": 0.40,  // Was 0.30
  "technical_strength": 0.15,      // Was 0.20
  ...
}
```

**Option 3**: Reduce penalties
```json
"penalties": {
  "low_volume": 5,         // Was 10
  "high_volatility": 8,    // Was 15
  "negative_sentiment": 10 // Was 20
}
```

### To Decrease Opportunities (Stricter)

**Option 1**: Raise threshold
```json
"opportunity_threshold": 75  // Was 65
```

**Option 2**: Increase penalties
```json
"penalties": {
  "low_volume": 15,
  "high_volatility": 20,
  "negative_sentiment": 25
}
```

---

## Current Production Settings

**File**: `models/config/screening_config.json`

```json
{
  "screening": {
    "stocks_per_sector": 30,
    "max_total_stocks": 240,
    "opportunity_threshold": 65,
    "top_picks_count": 10,
    "min_confidence_score": 60
  },
  "scoring": {
    "weights": {
      "prediction_confidence": 0.30,
      "technical_strength": 0.20,
      "spi_alignment": 0.15,
      "liquidity": 0.15,
      "volatility": 0.10,
      "sector_momentum": 0.10
    },
    "penalties": {
      "low_volume": 10,
      "high_volatility": 15,
      "negative_sentiment": 20
    },
    "bonuses": {
      "fresh_lstm_model": 5,
      "high_win_rate": 10,
      "sector_leader": 5
    }
  }
}
```

---

## Summary: Why Only Few Stocks

✅ **By Design** - The system implements **5 layers of filtering**:

1. **Layer 1**: Price/Volume validation (240 → 180)
2. **Layer 2**: Technical screening score ≥50 (180 → 120)
3. **Layer 3**: ML prediction (120 → all scored)
4. **Layer 4**: Opportunity score ≥65 (120 → 8-15)
5. **Layer 5**: BUY signals only + Conf ≥60% (8-15 → 3-8)

**The goal is quality over quantity** - Each recommended stock has:
- ✅ Passed 5 filters
- ✅ Score ≥65/100 (top 3-5% of universe)
- ✅ High ML confidence (≥60%)
- ✅ Strong technical alignment
- ✅ Market sentiment support

**Result**: Typical morning report shows **3-8 high-quality opportunities**, not 80 stocks.

---

## Next Steps for Restoration

1. ✅ **Understanding Confirmed**: Pipeline flow documented
2. ⏳ **Restore AU Config**: 8 sectors × 30 stocks
3. ⏳ **Create US Config**: 8 sectors × 30 stocks  
4. ⏳ **Create UK Config**: 8 sectors × 30 stocks
5. ⏳ **Update Runners**: Use sector-based scanner

---

**Document Owner**: Pipeline Trading System  
**Last Updated**: January 3, 2026  
**Review Date**: February 1, 2026
