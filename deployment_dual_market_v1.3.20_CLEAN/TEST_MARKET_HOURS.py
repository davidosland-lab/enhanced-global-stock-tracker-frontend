"""
Test Market Hours Detection

Quick test to verify market hours detector works correctly.
"""

import sys
from pathlib import Path

# Add models directory to path
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH / "models" / "screening"))

from market_hours_detector import MarketHoursDetector

def main():
    """Test market hours detection"""
    
    print("=" * 80)
    print("MARKET HOURS DETECTION TEST")
    print("=" * 80)
    print()
    
    detector = MarketHoursDetector()
    
    # Test ASX
    print("🇦🇺 AUSTRALIAN MARKET (ASX)")
    print("-" * 80)
    print(detector.get_market_status_summary('ASX'))
    asx_status = detector.is_market_open('ASX')
    print()
    
    if asx_status['is_open']:
        print("✅ ASX is OPEN - Pipeline will use INTRADAY mode")
        print(f"   • {asx_status['trading_hours_elapsed_pct']:.1f}% of trading day completed")
        print(f"   • Market closes in: {asx_status['time_until_close']}")
    else:
        print("🌙 ASX is CLOSED - Pipeline will use OVERNIGHT mode")
        print(f"   • Market phase: {asx_status['market_phase'].upper()}")
    
    print()
    print("=" * 80)
    print()
    
    # Test US
    print("🇺🇸 US MARKET")
    print("-" * 80)
    print(detector.get_market_status_summary('US'))
    us_status = detector.is_market_open('US')
    print()
    
    if us_status['is_open']:
        print("✅ US Market is OPEN")
        print(f"   • {us_status['trading_hours_elapsed_pct']:.1f}% of trading day completed")
        print(f"   • Market closes in: {us_status['time_until_close']}")
    else:
        print("🌙 US Market is CLOSED")
        print(f"   • Market phase: {us_status['market_phase'].upper()}")
    
    print()
    print("=" * 80)
    print()
    
    # Summary
    print("📊 RECOMMENDATION:")
    print("-" * 80)
    
    if detector.should_use_intraday_mode('ASX'):
        print("⚡ Run AUS pipeline in INTRADAY mode")
        print("   • Use real-time/recent prices")
        print("   • Focus on momentum indicators")
        print("   • De-emphasize overnight gap predictions")
    else:
        print("🌙 Run AUS pipeline in OVERNIGHT mode (default)")
        print("   • Use standard predictions")
        print("   • Include SPI futures analysis")
        print("   • Focus on next-day opportunities")
    
    print()
    print("=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    main()
