"""
Technical Analysis API endpoints
Provides REST API for technical indicators and analysis
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
import logging
from technical_analysis_engine import technical_engine

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/technical", tags=["technical_analysis"])

@router.get("/analysis/{symbol}")
async def get_technical_analysis(
    symbol: str,
    period: str = Query("3mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
) -> Dict[str, Any]:
    """
    Get comprehensive technical analysis for a symbol
    
    Returns:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - Moving Averages (SMA, EMA)
    - Volume Indicators
    - Momentum Indicators
    - Overall buy/sell/hold signal
    """
    try:
        logger.info(f"📊 Generating technical analysis for {symbol} (period={period}, interval={interval})")
        
        # Generate comprehensive analysis
        analysis = technical_engine.generate_comprehensive_analysis(symbol, period, interval)
        
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
        
        return {
            "success": True,
            "data": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in technical analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/rsi/{symbol}")
async def get_rsi(
    symbol: str,
    period: str = Query("1mo", description="Time period"),
    rsi_period: int = Query(14, description="RSI calculation period")
) -> Dict[str, Any]:
    """Get RSI (Relative Strength Index) for a symbol"""
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data available for symbol")
        
        rsi_data = technical_engine.calculate_rsi(hist['Close'], rsi_period)
        
        return {
            "success": True,
            "symbol": symbol,
            "indicator": "RSI",
            "period": rsi_period,
            "data": rsi_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/macd/{symbol}")
async def get_macd(
    symbol: str,
    period: str = Query("3mo", description="Time period"),
    fast: int = Query(12, description="Fast EMA period"),
    slow: int = Query(26, description="Slow EMA period"),
    signal: int = Query(9, description="Signal line EMA period")
) -> Dict[str, Any]:
    """Get MACD (Moving Average Convergence Divergence) for a symbol"""
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data available for symbol")
        
        macd_data = technical_engine.calculate_macd(hist['Close'], fast, slow, signal)
        
        return {
            "success": True,
            "symbol": symbol,
            "indicator": "MACD",
            "parameters": {"fast": fast, "slow": slow, "signal": signal},
            "data": macd_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/bollinger/{symbol}")
async def get_bollinger_bands(
    symbol: str,
    period: str = Query("1mo", description="Time period"),
    bb_period: int = Query(20, description="Bollinger Bands period"),
    std_dev: int = Query(2, description="Number of standard deviations")
) -> Dict[str, Any]:
    """Get Bollinger Bands for a symbol"""
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data available for symbol")
        
        bollinger_data = technical_engine.calculate_bollinger_bands(hist['Close'], bb_period, std_dev)
        
        return {
            "success": True,
            "symbol": symbol,
            "indicator": "Bollinger Bands",
            "parameters": {"period": bb_period, "std_dev": std_dev},
            "data": bollinger_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/moving-averages/{symbol}")
async def get_moving_averages(
    symbol: str,
    period: str = Query("6mo", description="Time period")
) -> Dict[str, Any]:
    """Get various moving averages for a symbol"""
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data available for symbol")
        
        ma_data = technical_engine.calculate_moving_averages(hist['Close'])
        
        return {
            "success": True,
            "symbol": symbol,
            "indicator": "Moving Averages",
            "data": ma_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating moving averages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candlestick-data/{symbol}")
async def get_candlestick_data(
    symbol: str,
    period: str = Query("1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
) -> Dict[str, Any]:
    """
    Get candlestick data with technical indicators for charting
    
    Returns OHLCV data plus calculated technical indicators
    suitable for rendering candlestick charts with overlays
    """
    try:
        logger.info(f"📈 Fetching candlestick data for {symbol} (period={period}, interval={interval})")
        
        data = technical_engine.get_candlestick_data(symbol, period, interval)
        
        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"])
        
        return {
            "success": True,
            "symbol": symbol,
            "data": data["data"],
            "indicators": data["indicators"],
            "metadata": data["metadata"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candlestick data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/{symbol}")
async def get_trading_signals(
    symbol: str,
    period: str = Query("3mo", description="Time period")
) -> Dict[str, Any]:
    """
    Get trading signals based on technical analysis
    
    Returns buy/sell/hold signals from multiple indicators
    """
    try:
        logger.info(f"🎯 Generating trading signals for {symbol}")
        
        # Get comprehensive analysis
        analysis = technical_engine.generate_comprehensive_analysis(symbol, period)
        
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
        
        # Extract signals
        signals = analysis.get("signals", [])
        overall_signal = analysis.get("overall_signal", "HOLD")
        confidence = analysis.get("confidence", 0.5)
        
        # Create signal summary
        signal_summary = {
            "strong_buy": sum(1 for s in signals if s["signal"] == "strong_buy"),
            "buy": sum(1 for s in signals if s["signal"] == "buy"),
            "hold": sum(1 for s in signals if s["signal"] == "hold"),
            "sell": sum(1 for s in signals if s["signal"] == "sell"),
            "strong_sell": sum(1 for s in signals if s["signal"] == "strong_sell")
        }
        
        return {
            "success": True,
            "symbol": symbol,
            "overall_signal": overall_signal,
            "confidence": confidence,
            "signal_summary": signal_summary,
            "detailed_signals": signals,
            "current_price": analysis.get("current_price", 0),
            "timestamp": analysis.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating trading signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screener")
async def technical_screener(
    symbols: str = Query("AAPL,MSFT,GOOGL,AMZN,TSLA", description="Comma-separated list of symbols"),
    signal_filter: Optional[str] = Query(None, description="Filter by signal: BUY, SELL, HOLD")
) -> Dict[str, Any]:
    """
    Screen multiple symbols for technical signals
    
    Useful for finding trading opportunities across multiple stocks
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        logger.info(f"🔍 Screening {len(symbol_list)} symbols for technical signals")
        
        results = []
        for symbol in symbol_list:
            try:
                analysis = technical_engine.generate_comprehensive_analysis(symbol, "1mo")
                
                if "error" not in analysis:
                    result = {
                        "symbol": symbol,
                        "signal": analysis.get("overall_signal", "HOLD"),
                        "confidence": analysis.get("confidence", 0.5),
                        "price": analysis.get("current_price", 0),
                        "rsi": analysis.get("indicators", {}).get("rsi", {}).get("value", 50),
                        "macd_signal": analysis.get("indicators", {}).get("macd", {}).get("interpretation", "neutral")
                    }
                    
                    # Apply filter if specified
                    if not signal_filter or result["signal"] == signal_filter:
                        results.append(result)
                        
            except Exception as e:
                logger.warning(f"Failed to analyze {symbol}: {e}")
                continue
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "success": True,
            "screened": len(symbol_list),
            "matches": len(results),
            "filter": signal_filter,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in technical screener: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for technical analysis module"""
    return {
        "status": "healthy",
        "module": "technical_analysis",
        "version": "1.0.0",
        "indicators_available": [
            "RSI", "MACD", "Bollinger Bands", "Moving Averages",
            "Volume Indicators", "Momentum Indicators"
        ]
    }