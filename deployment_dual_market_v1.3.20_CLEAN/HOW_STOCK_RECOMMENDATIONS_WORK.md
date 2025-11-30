# How the Pipeline Chooses Stock Recommendations

## Overview

The Event Risk Guard system uses a **multi-stage filtering and scoring process** to identify top trading opportunities. It combines machine learning, technical analysis, market sentiment, and risk assessment to rank stocks.

---

## Pipeline Workflow (6 Phases)

### Phase 1: Market Sentiment Analysis
**Purpose:** Understand overall market conditions before analyzing individual stocks

**ASX Market:**
- Monitors SPI 200 futures
- Compares futures price to ASX 200 index
- Calculates expected gap (bullish/bearish/neutral)
- Sentiment Score: 0-100 (market confidence level)

**US Market:**
- Monitors S&P 500 index
- Monitors VIX (volatility index)
- Calculates market mood (calm/healthy/anxious/fear)
- Sentiment Score: 0-100

**Output:** Market direction signal (bullish/bearish/neutral) used to align stock picks

---

### Phase 1.5: Market Regime Detection
**Purpose:** Identify current market volatility state using Hidden Markov Model (HMM)

**Process:**
1. Fetches 1 year of market data (ASX 200 or S&P 500)
2. Calculates returns, volatility, momentum
3. HMM classifies into 3 states:
   - **CALM** (Low volatility, stable returns)
   - **NORMAL** (Medium volatility, typical conditions)
   - **HIGH_VOL** (High volatility, crash risk)

4. Calculates crash risk probability
5. Adjusts risk appetite based on regime

**Impact on Recommendations:**
- HIGH_VOL regime → More conservative picks, higher quality threshold
- CALM regime → Can take more opportunities
- Risk multipliers: CALM (0.7x), NORMAL (1.0x), HIGH_VOL (1.5x)

---

### Phase 2: Stock Scanning & Validation
**Purpose:** Filter universe of stocks to tradeable candidates

#### 2.1 Sector-Based Scanning
**ASX:** 8 sectors, 30 stocks per sector = 240 stocks
**US:** 8 sectors, 30 stocks per sector = 240 stocks

**Sectors:**
- Technology
- Healthcare  
- Financials
- Consumer Discretionary
- Communication Services
- Industrials
- Energy
- Consumer Staples

#### 2.2 Stock Validation Criteria

**Price Filters:**
- ASX: A$0.20 - A$500.00
- US: $5.00 - $1,000.00

**Volume Filters:**
- ASX: Min 500,000 shares average daily volume
- US: Min 1,000,000 shares average daily volume

**Market Cap:**
- ASX: Min A$50 million
- US: Min $2 billion

**Data Quality:**
- Must have 20+ days of recent price data
- Must have valid OHLCV data
- No delisted or suspended stocks

#### 2.3 Technical Analysis (per stock)

**Calculated Indicators:**
1. **RSI (14-day)** - Overbought/oversold indicator
2. **MA20** - 20-day moving average (short-term trend)
3. **MA50** - 50-day moving average (medium-term trend)
4. **Volatility** - Annualized standard deviation of returns
5. **Volume Ratio** - Current volume vs average volume

**Fundamental Data (NEW - US stocks):**
- Company name
- Market capitalization
- Beta (volatility vs market)
- Sector classification

#### 2.4 Initial Screening Score (0-100)

**Scoring Factors:**
- RSI score (30 points): Prefers 40-60 range, bonus for oversold (<30)
- Moving average position (25 points): Bonus if price above MA20 and MA50
- Volume strength (20 points): Higher score for volume >2x average
- Volatility (15 points): Prefers moderate volatility (0.15-0.35)
- Sector weight (10 points): Some sectors weighted higher (e.g., Tech = 1.4x)

**Output:** ~180-200 validated stocks with initial scores

---

### Phase 3: Batch Prediction (ML Ensemble)
**Purpose:** Predict future price direction for each stock

#### 3.1 Ensemble Model (4 Components)

**Component Weights:**
- **LSTM Neural Network: 45%** (primary predictor)
- **Trend Analysis: 25%** (moving average momentum)
- **Technical Indicators: 15%** (RSI, MACD, volatility)
- **Sentiment Analysis: 15%** (market alignment)

#### 3.2 LSTM Prediction (45% weight)

**Yes, LSTM Training Occurs!**

**When Training Happens:**
- **Phase 4.5** (after scoring, before reporting)
- Trains models for top opportunity stocks
- **Max 100 models per night** (configurable)
- Only trains if model is stale (>7 days old)

**LSTM Architecture:**
- Sequence length: 60 days
- Inputs: OHLCV + technical indicators
- Outputs: Price direction probability
- Training: 50 epochs, 32 batch size, 20% validation split

**Prediction Process:**
1. Checks if pre-trained model exists for stock
2. If available and fresh (<7 days): Uses saved model
3. If not available or stale: Uses trend-based fallback
4. Returns direction (-1 to +1) and confidence (0-1)

**Model Storage:**
- Trained models saved to: `finbert_v4.4.4/models/trained/`
- File format: `{SYMBOL}_lstm_model.h5` or `.keras`
- Reused on subsequent runs if fresh

#### 3.3 Trend Analysis (25% weight)

**Signals:**
- Price above MA20 → Bullish (+1)
- Price below MA20 → Bearish (-1)
- Price above MA50 → Bullish (+1)
- MA20 > MA50 (golden cross) → Bullish (+1)
- MA20 rising → Bullish momentum (+1)

**Direction:** Average of signals (-1 to +1)
**Confidence:** Unanimity of signals (0-1)

#### 3.4 Technical Indicators (15% weight)

**RSI Signal:**
- RSI < 30 → Strong Buy (1.0)
- RSI 30-40 → Moderate Buy (0.5)
- RSI 40-60 → Neutral (0)
- RSI 60-70 → Moderate Sell (-0.5)
- RSI > 70 → Strong Sell (-1.0)

**Volatility Signal:**
- Low volatility (<0.02) → Positive (0.5)
- Medium volatility (0.02-0.04) → Neutral (0.2)
- High volatility (>0.04) → Negative (-0.2)

**Combined:** 70% RSI + 30% Volatility

#### 3.5 Sentiment Alignment (15% weight)

**Factors:**
- Stock prediction vs market sentiment alignment
- Market confidence level
- News sentiment (if available via FinBERT)

**Scoring:**
- Perfect alignment (BUY + bullish market) → 1.0
- Misalignment (BUY + bearish market) → 0.3
- Neutral combinations → 0.5

#### 3.6 Ensemble Prediction Output

**Final Prediction:**
```
Ensemble Direction = (LSTM × 0.45) + (Trend × 0.25) + (Technical × 0.15) + (Sentiment × 0.15)
```

**Direction Threshold:**
- \> 0.3 → **BUY** signal
- < -0.3 → **SELL** signal  
- -0.3 to 0.3 → **HOLD** signal

**Confidence:** Weighted average of component confidences (0-100%)

**Output:** Each stock now has `prediction` (BUY/SELL/HOLD) and `confidence` (0-100%)

---

### Phase 4: Opportunity Scoring
**Purpose:** Rank stocks by investment quality (0-100 composite score)

#### 4.1 Scoring Components (6 Factors)

**1. Prediction Confidence (30%)**
- Higher confidence = higher score
- BUY signals get 20% bonus
- SELL signals get 20% penalty
- HOLD signals get 50% penalty

**2. Technical Strength (20%)**
- RSI in optimal range (40-60) = 1.0
- Price above MA20 = bonus
- Scanner score from Phase 2

**3. Market Alignment (15%)**
- Stock prediction matches market sentiment = 1.0
- Misalignment (contrarian) = 0.3
- Neutral combinations = 0.5
- Weighted by market confidence

**4. Liquidity (15%)**
- Volume score:
  - \>5M shares/day = 1.0
  - \>2M shares/day = 0.8
  - \>1M shares/day = 0.6
  - <500K shares/day = 0.2
- Market cap bonus for large caps

**5. Volatility Risk (10%)**
- Low volatility (0.15-0.25) = 0.8
- Medium volatility (0.25-0.35) = 0.6
- High volatility (>0.40) = 0.3
- Penalizes excessive risk

**6. Sector Momentum (10%)**
- Compares stock to sector average
- Sector leaders get bonus
- Sector laggards get penalty

#### 4.2 Adjustments (Penalties & Bonuses)

**Penalties:**
- Low volume: -10 points
- High volatility: -15 points
- Negative sentiment: -20 points

**Bonuses:**
- Fresh LSTM model (<7 days): +5 points
- High historical win rate: +10 points
- Sector leader: +5 points

#### 4.3 Final Opportunity Score

**Formula:**
```
Score = (Prediction × 0.30) + (Technical × 0.20) + (Alignment × 0.15) + 
        (Liquidity × 0.15) + (Volatility × 0.10) + (Sector × 0.10)
        + Bonuses - Penalties
```

**Range:** 0-100
- **80-100:** Excellent opportunity
- **65-79:** Good opportunity  
- **50-64:** Moderate opportunity
- **<50:** Low opportunity

**Output:** All stocks ranked by opportunity score

---

### Phase 4.5: LSTM Model Training (Optional)
**Purpose:** Train neural networks for future predictions

**Training Queue Creation:**
- Selects top stocks by opportunity score
- Only trains if model is stale (>7 days old)
- Max 100 models per night

**Training Process:**
1. Fetches 1 year of historical data
2. Prepares sequences (60-day windows)
3. Trains LSTM model (50 epochs)
4. Validates on 20% holdout data
5. Saves model to disk

**Training Time:**
- ~2-3 minutes per model
- 100 models = ~3-5 hours total
- Runs overnight (doesn't block reporting)

**Config Settings:**
```json
"lstm_training": {
  "enabled": true,
  "max_models_per_night": 100,
  "stale_threshold_days": 7,
  "epochs": 50,
  "batch_size": 32,
  "validation_split": 0.2,
  "priority_strategy": "highest_opportunity_score"
}
```

**Models Used on Next Run:**
- Trained models cached for 7 days
- Improves prediction accuracy over time
- Falls back to trend analysis if model unavailable

---

### Phase 5: Report Generation
**Purpose:** Create HTML morning report with top recommendations

#### 5.1 Report Filtering

**Minimum Thresholds:**
- Opportunity Score ≥ 65 (configurable)
- Confidence ≥ 60%
- BUY signals only (for top picks)

**Top Picks Selection:**
- Sorts all stocks by opportunity score
- Selects top 10 stocks
- Ensures diversity across sectors

#### 5.2 Report Sections

**1. Market Overview**
- Market sentiment (bullish/bearish/neutral)
- Sentiment score (0-100)
- Market regime (CALM/NORMAL/HIGH_VOL)
- Crash risk probability

**2. Top 10 Opportunities**
For each stock:
- **Symbol & Name**
- **Opportunity Score** (0-100)
- **Signal** (BUY/SELL/HOLD)
- **Confidence** (0-100%)
- **Current Price**
- **RSI** (technical indicator)
- **Market Cap** (fundamental)
- **Beta** (volatility vs market)
- **Analysis Text** (AI-generated summary)

**3. Sector Summary**
- Performance by sector
- Average scores
- Top stocks per sector

**4. Technical Details**
- Regime analysis
- Volatility metrics
- System statistics

---

### Phase 6: Finalization
**Purpose:** Save results, send notifications, update logs

**Outputs:**
- HTML report: `reports/morning_reports/` (ASX) or `reports/us/` (US)
- CSV export: Stock data in tabular format
- JSON state: Pipeline status and metrics
- Email notification: Report sent to configured recipients
- Training logs: LSTM model training results

---

## Key Differences: ASX vs US Pipeline

| Aspect | ASX Pipeline | US Pipeline |
|--------|--------------|-------------|
| **Market Sentiment** | SPI 200 futures | S&P 500 + VIX |
| **Regime Detection** | ASX 200 index | S&P 500 index |
| **Stock Universe** | 240 ASX stocks | 240 US stocks |
| **Price Range** | A$0.20 - A$500 | $5.00 - $1,000 |
| **Min Volume** | 500K shares | 1M shares |
| **Min Market Cap** | A$50M | $2B |
| **LSTM Training** | ✅ Yes (Phase 4.5) | ❌ No |
| **Fundamental Data** | Basic | ✅ Full (name, beta, mcap) |
| **Report Location** | `reports/morning_reports/` | `reports/us/` |
| **Runtime** | ~20-30 min (+ 3-5h training) | ~15-20 min |

---

## Example: How GOOGL Gets Recommended

**Phase 1:** US market bullish (S&P +0.8%, VIX 15.2 = calm)

**Phase 2:** GOOGL scanned
- Price: $299.66 ✓ (within $5-$1000 range)
- Volume: 25.3M ✓ (>1M threshold)
- Market Cap: $2.1T ✓ (>$2B threshold)
- RSI: 52.3 (neutral)
- MA20: $295.00 (price above = bullish)
- MA50: $288.50 (price above = bullish)
- Initial Score: 68/100

**Phase 3:** Ensemble Prediction
- LSTM: +0.42 (bullish, 67% confidence) × 45% = 0.189
- Trend: +0.75 (strong uptrend) × 25% = 0.188
- Technical: +0.20 (neutral RSI) × 15% = 0.030
- Sentiment: +0.80 (aligned with market) × 15% = 0.120
- **Ensemble: +0.527 → BUY signal**
- **Confidence: 72%**

**Phase 4:** Opportunity Scoring
- Prediction Confidence: 72% × 1.2 (BUY bonus) = 86/100
- Technical Strength: 68/100 (from scanner)
- Market Alignment: 95/100 (perfect alignment)
- Liquidity: 100/100 (excellent volume)
- Volatility: 75/100 (moderate risk)
- Sector Momentum: 80/100 (tech sector strong)
- **Final Score: 82/100** → Excellent opportunity

**Phase 5:** Report Inclusion
- Score 82 ≥ 65 threshold ✓
- Confidence 72% ≥ 60% threshold ✓
- BUY signal ✓
- **Included in Top 10**

**Phase 4.5:** LSTM Training (if needed)
- Check: Does GOOGL have fresh model (<7 days)?
- If NO: Queue for training tonight
- If YES: Skip (use existing model next time)

---

## Summary

**The pipeline is highly selective:**
1. Starts with 240 stocks per market
2. Validates ~180-200 stocks (75-85% pass rate)
3. Predicts direction for all validated stocks
4. Scores all stocks (0-100 composite score)
5. Recommends only top 10-20 stocks (top 5-10%)

**Recommendation criteria:**
- ✅ Strong ensemble prediction (BUY signal)
- ✅ High confidence (≥60%)
- ✅ High opportunity score (≥65)
- ✅ Good liquidity and reasonable risk
- ✅ Aligned with market sentiment
- ✅ Strong technical indicators

**The result:** A curated list of high-probability trading opportunities backed by ML, technicals, and market analysis.
