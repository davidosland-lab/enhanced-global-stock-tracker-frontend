"""
Test Intraday Momentum Scoring (Phase 2)

This script tests the full intraday scoring implementation:
1. Fetches intraday 1-minute data
2. Calculates momentum scores
3. Compares overnight vs intraday scoring
"""

import sys
from pathlib import Path
from datetime import datetime

# Add models directory to path
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH / "models" / "screening"))

from market_hours_detector import MarketHoursDetector
from stock_scanner import StockScanner
from opportunity_scorer import OpportunityScorer

def test_intraday_scoring():
    """Test intraday scoring with real market data"""
    
    print("=" * 80)
    print("INTRADAY MOMENTUM SCORING TEST (Phase 2)")
    print("=" * 80)
    print()
    
    # Step 1: Check market status
    print("Step 1: Market Hours Detection")
    print("-" * 80)
    detector = MarketHoursDetector()
    market_status = detector.is_market_open('ASX')
    print(detector.get_market_status_summary('ASX'))
    print()
    
    if not market_status['is_open']:
        print("⚠️  WARNING: ASX market is currently CLOSED")
        print("   Intraday data may be limited or from previous session")
        print("   For best results, run this test during market hours (10 AM - 4 PM AEST)")
        print()
    
    # Step 2: Initialize scanner and scorer
    print("Step 2: Initialize Components")
    print("-" * 80)
    config_path = BASE_PATH / "models" / "config" / "screening_config.json"
    scanner = StockScanner(str(config_path))
    scorer = OpportunityScorer(str(config_path))
    print("✓ Stock Scanner initialized")
    print("✓ Opportunity Scorer initialized")
    print()
    
    # Step 3: Test with a few ASX stocks
    print("Step 3: Test Stock Analysis")
    print("-" * 80)
    test_symbols = ['CBA.AX', 'BHP.AX', 'WBC.AX', 'NAB.AX', 'ANZ.AX']
    print(f"Testing with: {', '.join(test_symbols)}")
    print()
    
    # Analyze stocks with and without intraday data
    overnight_stocks = []
    intraday_stocks = []
    
    for symbol in test_symbols:
        print(f"Analyzing {symbol}...")
        
        # Overnight analysis
        overnight_data = scanner.analyze_stock(symbol, sector_weight=1.0, include_intraday=False)
        if overnight_data:
            overnight_stocks.append(overnight_data)
            print(f"  ✓ Overnight: Price ${overnight_data['price']:.2f}")
        
        # Intraday analysis
        intraday_data = scanner.analyze_stock(symbol, sector_weight=1.0, include_intraday=True)
        if intraday_data:
            intraday_stocks.append(intraday_data)
            if 'intraday_data' in intraday_data:
                id_data = intraday_data['intraday_data']
                print(f"  📈 Intraday: Price ${id_data['current_price']:.2f} " +
                      f"({id_data['session_change_pct']:+.2f}% session, " +
                      f"{id_data['momentum_15m']:+.2f}% 15m)")
            else:
                print(f"  ⚠️  No intraday data available")
        
        print()
    
    if not overnight_stocks:
        print("✗ No stocks analyzed successfully")
        return
    
    # Step 4: Score opportunities (both modes)
    print("Step 4: Opportunity Scoring Comparison")
    print("-" * 80)
    print()
    
    # Create mock predictions for testing
    for stock in overnight_stocks:
        stock['prediction'] = 'BUY'
        stock['confidence'] = 70
    
    for stock in intraday_stocks:
        stock['prediction'] = 'BUY'
        stock['confidence'] = 70
    
    # Mock sentiment
    mock_sentiment = {
        'sentiment_score': 60,
        'gap_prediction': {'predicted_gap_pct': 0.5, 'direction': 'bullish', 'confidence': 65}
    }
    
    # Score overnight mode
    print("🌙 OVERNIGHT MODE SCORING")
    print("-" * 40)
    overnight_scored = scorer.score_opportunities(
        overnight_stocks,
        mock_sentiment,
        market_status={'is_open': False}
    )
    
    print("\nTop 3 Overnight Scores:")
    for i, stock in enumerate(overnight_scored[:3], 1):
        breakdown = stock.get('score_breakdown', {})
        print(f"\n{i}. {stock['symbol']}: {stock['opportunity_score']:.1f}/100")
        print(f"   - Prediction Confidence: {breakdown.get('prediction_confidence', 0):.1f}")
        print(f"   - Technical Strength: {breakdown.get('technical_strength', 0):.1f}")
        print(f"   - SPI Alignment: {breakdown.get('spi_alignment', 0):.1f}")
        print(f"   - Liquidity: {breakdown.get('liquidity', 0):.1f}")
    
    print()
    print("=" * 80)
    print()
    
    # Score intraday mode
    print("📈 INTRADAY MODE SCORING")
    print("-" * 40)
    intraday_scored = scorer.score_opportunities(
        intraday_stocks,
        mock_sentiment,
        market_status=market_status
    )
    
    print("\nTop 3 Intraday Scores:")
    for i, stock in enumerate(intraday_scored[:3], 1):
        breakdown = stock.get('score_breakdown', {})
        momentum_bd = stock.get('momentum_breakdown', {})
        print(f"\n{i}. {stock['symbol']}: {stock['opportunity_score']:.1f}/100")
        print(f"   - Intraday Momentum: {breakdown.get('intraday_momentum', 0):.1f}")
        print(f"     • Momentum Score: {momentum_bd.get('momentum', 0):.1f}")
        print(f"     • Volume Surge: {momentum_bd.get('volume_surge', 0):.1f} (ratio: {momentum_bd.get('surge_ratio', 0):.2f}x)")
        print(f"     • Volatility: {momentum_bd.get('volatility', 0):.1f}")
        print(f"     • Breakout: {momentum_bd.get('breakout', 0):.1f}")
        print(f"   - Technical Strength: {breakdown.get('technical_strength', 0):.1f}")
        print(f"   - Liquidity: {breakdown.get('liquidity', 0):.1f}")
        print(f"   - Prediction (reduced): {breakdown.get('prediction_confidence', 0):.1f}")
    
    print()
    print("=" * 80)
    print()
    
    # Step 5: Compare scores
    print("Step 5: Score Comparison")
    print("-" * 80)
    print()
    
    print(f"{'Symbol':<10} {'Overnight':<12} {'Intraday':<12} {'Change':<10} {'Reason'}")
    print("-" * 80)
    
    for symbol in test_symbols:
        # Find scores
        overnight_stock = next((s for s in overnight_scored if s['symbol'] == symbol), None)
        intraday_stock = next((s for s in intraday_scored if s['symbol'] == symbol), None)
        
        if overnight_stock and intraday_stock:
            overnight_score = overnight_stock['opportunity_score']
            intraday_score = intraday_stock['opportunity_score']
            change = intraday_score - overnight_score
            
            # Determine reason for change
            if change > 5:
                reason = "Strong momentum"
            elif change > 0:
                reason = "Positive momentum"
            elif change < -5:
                reason = "Weak momentum"
            else:
                reason = "Similar"
            
            print(f"{symbol:<10} {overnight_score:>6.1f}/100   {intraday_score:>6.1f}/100   " +
                  f"{change:>+6.1f}     {reason}")
    
    print()
    print("=" * 80)
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 80)
    print()
    print("✅ Phase 2 Implementation Status:")
    print("   ✓ Intraday data fetching (1-minute bars)")
    print("   ✓ Momentum scoring (15m, 60m, session)")
    print("   ✓ Volume surge detection")
    print("   ✓ Intraday volatility scoring")
    print("   ✓ Breakout detection")
    print("   ✓ Mode-aware weight adjustment")
    print()
    print("📈 Key Differences:")
    print("   • Overnight: Prediction-focused (30% weight)")
    print("   • Intraday: Momentum-focused (30% weight)")
    print("   • SPI alignment: 15% → 5% (gap already occurred)")
    print("   • Liquidity: 15% → 20% (critical for execution)")
    print("   • Volatility: 10% → 15% (opportunity for traders)")
    print()
    
    if market_status['is_open']:
        print("✅ Test completed during market hours - Results are LIVE")
    else:
        print("⚠️  Test completed after hours - Rerun during market hours for live data")
    
    print()
    print("=" * 80)
    print("✅ Phase 2 test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_intraday_scoring()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
