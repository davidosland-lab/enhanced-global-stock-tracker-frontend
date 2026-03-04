"""
Quick test of World Event Monitor fix v193.4
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from pipelines.models.screening.world_event_monitor import WorldEventMonitor

print("="*80)
print("TESTING WORLD EVENT MONITOR v193.4 FIX")
print("="*80)

monitor = WorldEventMonitor()

# Test articles about Iran-US-Israel conflict
test_articles = [
    {'title': 'Iran launches missile strikes on US military bases', 'source': 'Reuters'},
    {'title': 'Israel and Iran exchange fresh attacks as war escalates', 'source': 'BBC'},
    {'title': 'US sends troops to Middle East amid Iran-Israel conflict', 'source': 'AP'},
    {'title': 'Oil prices surge as Iran threatens Strait of Hormuz', 'source': 'Bloomberg'},
    {'title': 'NATO emergency meeting on Iran-Israel war escalation', 'source': 'Reuters'}
]

print("\n[TEST] Iran-US-Israel War Articles")
print("-"*80)

risk = monitor.get_world_event_risk(test_articles)

print(f"\n✓ World Risk Score: {risk['world_risk_score']:.1f}/100")
print(f"✓ Risk Level: {risk['risk_level']}")
print(f"✓ Fear: {risk['fear']:.2f}, Anger: {risk['anger']:.2f}")
print(f"✓ Topics: {', '.join(risk['top_topics'][:5])}")

print("\n" + "="*80)
if risk['world_risk_score'] >= 75:
    print(f"✅ SUCCESS: Crisis detected! Score: {risk['world_risk_score']:.1f}/100")
    print("   v193.4 fix is WORKING correctly")
else:
    print(f"❌ FAIL: Score too low: {risk['world_risk_score']:.1f}/100")
    print("   Expected: 85-90, Need further investigation")

print("="*80)
