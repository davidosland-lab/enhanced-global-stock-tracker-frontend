import json

# Check if the AU morning report has FinBERT data
try:
    with open('ULTIMATE_v193_COMPLETE/reports/screening/au_morning_report.json', 'r') as f:
        report = json.load(f)
    
    print("="*80)
    print("AU MORNING REPORT - FinBERT SENTIMENT CHECK")
    print("="*80)
    
    # Check for finbert_sentiment
    if 'finbert_sentiment' in report:
        fb = report['finbert_sentiment']
        print("✅ finbert_sentiment field EXISTS")
        print(f"\nOverall Scores:")
        if 'overall_scores' in fb:
            scores = fb['overall_scores']
            print(f"  Negative: {scores.get('negative', 'MISSING')}")
            print(f"  Neutral:  {scores.get('neutral', 'MISSING')}")
            print(f"  Positive: {scores.get('positive', 'MISSING')}")
            
            # Calculate total
            total = scores.get('negative', 0) + scores.get('neutral', 0) + scores.get('positive', 0)
            print(f"\n  Total: {total} (should be ~1.0 for raw scores)")
        else:
            print("  ❌ overall_scores field MISSING")
        
        print(f"\nCompound: {fb.get('compound', 'MISSING')}")
        print(f"Confidence: {fb.get('confidence', 'MISSING')}")
        print(f"Dominant: {fb.get('dominant_sentiment', 'MISSING')}")
        print(f"Stock Count: {fb.get('stock_count', 'MISSING')}")
    else:
        print("❌ finbert_sentiment field DOES NOT EXIST")
    
    # Check timestamp
    print(f"\n{'='*80}")
    print(f"Report Timestamp: {report.get('timestamp', 'MISSING')}")
    print(f"Market: {report.get('market', 'MISSING')}")
    
    # Check market_sentiment
    if 'market_sentiment' in report:
        ms = report['market_sentiment']
        print(f"\nMarket Sentiment Score: {ms.get('sentiment_score', 'MISSING')}")
        print(f"Recommendation: {ms.get('recommendation', 'MISSING')}")
    
    print("="*80)
    
except FileNotFoundError:
    print("❌ Report file not found!")
except json.JSONDecodeError as e:
    print(f"❌ JSON decode error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
