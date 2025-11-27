#!/usr/bin/env python3
"""
Diagnose why US pipeline scores are 0
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.screening.us_stock_scanner import USStockScanner
from models.screening.batch_predictor import BatchPredictor
from models.screening.opportunity_scorer import OpportunityScorer

print("="*80)
print("🔍 DIAGNOSING US PIPELINE SCORING ISSUE")
print("="*80)

# Step 1: Scan a stock
print("\n1️⃣ Scanning a US stock (AAPL)...")
scanner = USStockScanner()
stock_data = scanner.analyze_stock('AAPL', sector_weight=1.0)

if not stock_data:
    print("❌ Failed to scan AAPL")
    sys.exit(1)

print(f"✓ Scanned AAPL successfully")
print(f"  Fields: {list(stock_data.keys())}")
print(f"  Scanner score: {stock_data.get('score', 'N/A')}")
print(f"  Technical fields: {list(stock_data.get('technical', {}).keys())}")

# Step 2: Generate prediction
print("\n2️⃣ Generating prediction...")
predictor = BatchPredictor()

# Fake sentiment for testing
fake_sentiment = {
    'gap_prediction': {
        'gap_pct': 0.5,
        'direction': 'bullish',
        'confidence': 70
    }
}

predicted = predictor.predict_batch([stock_data], fake_sentiment)

if not predicted:
    print("❌ Failed to generate predictions")
    sys.exit(1)

predicted_stock = predicted[0]
print(f"✓ Prediction generated")
print(f"  Fields after prediction: {list(predicted_stock.keys())}")
print(f"  Prediction: {predicted_stock.get('prediction', 'N/A')}")
print(f"  Confidence: {predicted_stock.get('prediction_confidence', 'N/A')}")

# Step 3: Score opportunity
print("\n3️⃣ Scoring opportunity...")
scorer = OpportunityScorer()

try:
    scored = scorer.score_opportunities(
        stocks_with_predictions=[predicted_stock],
        spi_sentiment=fake_sentiment,
        ai_scores=None,
        market_status={'is_open': False}
    )
    
    if not scored:
        print("❌ Scoring returned empty list")
        sys.exit(1)
    
    scored_stock = scored[0]
    print(f"✓ Scoring successful")
    print(f"\n📊 RESULTS:")
    print(f"  Opportunity Score: {scored_stock.get('opportunity_score', 'N/A')}/100")
    
    if 'score_breakdown' in scored_stock:
        print(f"\n  Score Breakdown:")
        for key, value in scored_stock['score_breakdown'].items():
            print(f"    - {key}: {value:.2f}")
    
    if 'score_error' in scored_stock:
        print(f"\n❌ SCORING ERROR: {scored_stock['score_error']}")
    
    print("\n" + "="*80)
    print("✅ DIAGNOSIS COMPLETE")
    print("="*80)
    
    if scored_stock.get('opportunity_score', 0) == 0:
        print("\n⚠️  ISSUE FOUND: Score is 0")
        print("Possible causes:")
        print("  1. Missing required fields in stock data")
        print("  2. Scoring algorithm returning 0")
        print("  3. Exception during scoring (check score_error field)")
    else:
        print("\n✅ Scoring working correctly!")
        
except Exception as e:
    print(f"\n❌ SCORING FAILED WITH EXCEPTION:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
