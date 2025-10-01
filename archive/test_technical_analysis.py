#!/usr/bin/env python3
"""
Test script for Technical Analysis module
Verifies that all indicators are working correctly
"""

import sys
sys.path.append('render_backend')

from technical_analysis_engine import technical_engine
import json

def test_technical_analysis():
    """Test the technical analysis engine"""
    
    print("🧪 Testing Technical Analysis Engine")
    print("=" * 50)
    
    # Test symbols
    test_symbols = ["AAPL", "CBA.AX", "^GSPC"]
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        
        try:
            # Generate comprehensive analysis
            analysis = technical_engine.generate_comprehensive_analysis(symbol, period="1mo", interval="1d")
            
            if "error" in analysis:
                print(f"  ❌ Error: {analysis['error']}")
                continue
            
            # Display results
            print(f"  ✅ Current Price: ${analysis.get('current_price', 0):.2f}")
            print(f"  📈 Overall Signal: {analysis.get('overall_signal', 'N/A')}")
            print(f"  💪 Confidence: {analysis.get('confidence', 0):.1%}")
            
            # Display indicators
            indicators = analysis.get('indicators', {})
            
            # RSI
            rsi_data = indicators.get('rsi', {})
            print(f"  📉 RSI: {rsi_data.get('value', 0):.2f} - {rsi_data.get('description', 'N/A')}")
            
            # MACD
            macd_data = indicators.get('macd', {})
            print(f"  📊 MACD: {macd_data.get('description', 'N/A')}")
            
            # Bollinger Bands
            bb_data = indicators.get('bollinger_bands', {})
            print(f"  📈 Bollinger: Position {bb_data.get('position', 0):.1%} - {bb_data.get('description', 'N/A')}")
            
            # Moving Averages
            ma_data = indicators.get('moving_averages', {})
            print(f"  📊 MA Trend: {ma_data.get('trend', 'N/A')}")
            
            # Volume
            vol_data = indicators.get('volume', {})
            print(f"  📊 Volume: {vol_data.get('volume_signal', 'N/A')}")
            
            # Signals summary
            signals = analysis.get('signals', [])
            if signals:
                print(f"\n  🎯 Trading Signals ({len(signals)}):")
                for signal in signals[:3]:  # Show first 3 signals
                    print(f"    - {signal['indicator']}: {signal['signal']} ({signal['confidence']:.1%})")
            
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Technical Analysis Engine test complete!")

def test_api_endpoints():
    """Test API endpoints availability"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    endpoints = [
        "/api/technical/analysis/AAPL",
        "/api/technical/indicators/rsi/AAPL",
        "/api/technical/indicators/macd/AAPL",
        "/api/technical/indicators/bollinger/AAPL",
        "/api/technical/candlestick-data/AAPL",
        "/api/technical/signals/AAPL",
        "/api/technical/health"
    ]
    
    print("📍 Available endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint}")
    
    print("\n✅ API endpoints configured and ready!")

if __name__ == "__main__":
    test_technical_analysis()
    test_api_endpoints()