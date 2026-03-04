# Simulate what the dashboard would show with different score scenarios

scenarios = [
    ("Old Report (No FinBERT)", None),
    ("Zero Scores", {'negative': 0, 'neutral': 0, 'positive': 0}),
    ("Small Raw Scores", {'negative': 0.3, 'neutral': 0.1, 'positive': 0.35}),
    ("Normalized Scores", {'negative': 0.40, 'neutral': 0.13, 'positive': 0.47}),
]

print("="*80)
print("DASHBOARD DISPLAY SIMULATION")
print("="*80)

for scenario_name, scores in scenarios:
    print(f"\n{scenario_name}:")
    print("-" * 40)
    
    if scores is None:
        print("  ❌ No finbert_sentiment field → Shows 'FinBERT data loading...'")
        continue
    
    total = scores.get('negative', 0) + scores.get('neutral', 0) + scores.get('positive', 0)
    
    if total == 0:
        print(f"  ❌ Total: {total} → All bars at 0% width")
        print("  Result: No visible bars!")
        continue
    
    # Normalize
    scores_norm = {k: scores[k] / total for k in scores}
    
    print(f"  Raw Total: {total:.3f}")
    print(f"  Negative: {scores_norm['negative']*100:.1f}% width")
    print(f"  Neutral:  {scores_norm['neutral']*100:.1f}% width")
    print(f"  Positive: {scores_norm['positive']*100:.1f}% width")
    print(f"  Total: {sum(scores_norm.values())*100:.1f}%")
    
    if total < 0.5:
        print(f"  ⚠️  WARNING: Raw total < 0.5, bars will be small!")

print("\n" + "="*80)
print("DIAGNOSIS:")
print("="*80)
print("""
If dashboard bars are VERY SMALL or invisible:
1. Check if finbert_sentiment field exists in report
2. Check if overall_scores values are all zero
3. Check if raw scores are very small (< 0.1 each)

Expected values in v193.6+ report:
  negative: 0.35-0.50 (35-50% of 1.0)
  neutral:  0.25-0.35 (25-35% of 1.0)
  positive: 0.20-0.35 (20-35% of 1.0)
  Total: ~1.0

If values are much smaller (e.g., 0.003), the FinBERT
summary calculation may be dividing by stock count.
""")

