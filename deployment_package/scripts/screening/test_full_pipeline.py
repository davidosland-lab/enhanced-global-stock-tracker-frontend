#!/usr/bin/env python3
"""
Complete Pipeline Test for Overnight Screening System

Tests the full workflow including report generation:
1. Stock Scanner - Validates and scores stocks
2. SPI Monitor - Gets market sentiment
3. Batch Predictor - Generates predictions
4. Opportunity Scorer - Ranks opportunities
5. Report Generator - Creates HTML morning report
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.screening import (
    StockScanner,
    SPIMonitor,
    BatchPredictor,
    OpportunityScorer,
    ReportGenerator
)


def test_complete_pipeline():
    """Test complete screening pipeline with report generation"""
    print("\n" + "="*80)
    print("COMPLETE OVERNIGHT SCREENING PIPELINE TEST")
    print("="*80 + "\n")
    
    # Step 1: Initialize all components
    print("Step 1: Initializing components...")
    scanner = StockScanner()
    spi_monitor = SPIMonitor()
    predictor = BatchPredictor()
    scorer = OpportunityScorer()
    reporter = ReportGenerator()
    print("✓ All components initialized\n")
    
    # Step 2: Get market sentiment
    print("Step 2: Fetching SPI market sentiment...")
    try:
        spi_sentiment = spi_monitor.get_overnight_summary()
        print("✓ Market sentiment retrieved")
        print(f"  Sentiment Score: {spi_sentiment['sentiment_score']:.1f}/100")
        print(f"  Gap Prediction: {spi_sentiment['gap_prediction']['predicted_gap_pct']:+.2f}%")
        print(f"  Direction: {spi_sentiment['gap_prediction']['direction']}")
    except Exception as e:
        print(f"⚠ SPI data unavailable: {e}")
        spi_sentiment = None
    print()
    
    # Step 3: Scan stocks (test with Financials sector, 5 stocks)
    print("Step 3: Scanning stocks (Financials sector, first 5)...")
    try:
        # Get first 5 stocks from Financials
        sector_stocks = scanner.sectors['Financials']['stocks'][:5]
        sector_weight = scanner.sectors['Financials']['weight']
        
        scanned_stocks = []
        for symbol in sector_stocks:
            print(f"  Analyzing {symbol}...")
            if scanner.validate_stock(symbol):
                stock_data = scanner.analyze_stock(symbol, sector_weight)
                if stock_data:
                    scanned_stocks.append(stock_data)
                    print(f"    ✓ Score: {stock_data['score']:.1f}")
            else:
                print(f"    ✗ Failed validation")
        
        print(f"✓ Scanned {len(scanned_stocks)} valid stocks\n")
        
    except Exception as e:
        print(f"✗ Scanning failed: {e}\n")
        return
    
    if not scanned_stocks:
        print("⚠ No valid stocks found to continue test")
        return
    
    # Step 4: Generate predictions
    print("Step 4: Generating batch predictions...")
    try:
        predicted_stocks = predictor.predict_batch(scanned_stocks, spi_sentiment)
        print(f"✓ Generated {len(predicted_stocks)} predictions")
        
        # Show prediction summary
        summary = predictor.get_prediction_summary(predicted_stocks)
        print(f"  BUY: {summary['buy_count']} | SELL: {summary['sell_count']} | HOLD: {summary['hold_count']}")
        print(f"  Avg Confidence: {summary['avg_confidence']:.1f}%\n")
        
    except Exception as e:
        print(f"✗ Prediction failed: {e}\n")
        return
    
    # Step 5: Score opportunities
    print("Step 5: Scoring opportunities...")
    try:
        scored_stocks = scorer.score_opportunities(predicted_stocks, spi_sentiment)
        print(f"✓ Scored {len(scored_stocks)} opportunities")
        
        # Show top opportunities
        summary = scorer.get_opportunity_summary(scored_stocks)
        print(f"  High Opportunities (≥80): {summary['high_opportunity_count']}")
        print(f"  Medium Opportunities (65-80): {summary['medium_opportunity_count']}")
        print(f"  Average Score: {summary['avg_score']:.1f}/100\n")
        
    except Exception as e:
        print(f"✗ Scoring failed: {e}\n")
        return
    
    # Step 6: Generate morning report
    print("Step 6: Generating morning report...")
    try:
        # Prepare sector summary
        sector_summary = {
            'Financials': scanner.get_sector_summary(scored_stocks)
        }
        
        # Get prediction summary for system stats
        pred_summary = predictor.get_prediction_summary(scored_stocks)
        
        # Prepare system stats
        system_stats = {
            'total_scanned': len(scored_stocks),
            'buy_signals': pred_summary['buy_count'],
            'sell_signals': pred_summary['sell_count'],
            'processing_time_seconds': 300,  # Estimated
            'lstm_status': 'Not Available' if not predictor.lstm_available else 'Available'
        }
        
        # Generate report
        report_path = reporter.generate_morning_report(
            opportunities=scored_stocks,
            spi_sentiment=spi_sentiment,
            sector_summary=sector_summary,
            system_stats=system_stats
        )
        
        print(f"✓ Report generated: {report_path}")
        print(f"  File size: {Path(report_path).stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"✗ Report generation failed: {e}\n")
        return
    
    # Step 7: Display summary
    print("\n" + "-"*80)
    print("TOP OPPORTUNITIES (from report)")
    print("-"*80)
    
    top_opportunities = scored_stocks[:5]
    
    for i, stock in enumerate(top_opportunities, 1):
        print(f"\n{i}. {stock['symbol']} - {stock['name']}")
        print(f"   Opportunity Score: {stock['opportunity_score']:.1f}/100")
        print(f"   Prediction: {stock.get('prediction', 'N/A')} (Confidence: {stock.get('confidence', 0):.1f}%)")
        print(f"   Price: ${stock['price']:.2f}")
        print(f"   Market Cap: ${stock['market_cap']/1e9:.2f}B")
        print(f"   RSI: {stock['technical']['rsi']:.1f}")
    
    print("\n" + "="*80)
    print("COMPLETE PIPELINE TEST - SUCCESS ✓")
    print("="*80)
    print("\nAll 6 components working correctly! ✓")
    print(f"\n📊 Open the report in a browser:")
    print(f"   file://{Path(report_path).absolute()}")
    print("\nNext steps:")
    print("  1. Create overnight scheduler")
    print("  2. Build LSTM training integration")
    print("  3. Create batch execution scripts")
    print("  4. Add email notification system")


if __name__ == "__main__":
    test_complete_pipeline()
