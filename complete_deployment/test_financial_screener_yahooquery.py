#!/usr/bin/env python3
"""
Test Financial Sector Screener - yahooquery ONLY
No Alpha Vantage, no yfinance - Pure yahooquery implementation

Tests:
1. Stock data fetching (OHLCV)
2. Market sentiment calculation
3. Financial sector screening
"""

import logging
from datetime import datetime, timedelta
from yahooquery import Ticker
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FINANCIAL SECTOR TEST STOCKS (ASX)
# ============================================================================
FINANCIAL_SECTOR_STOCKS = [
    'CBA.AX',   # Commonwealth Bank
    'WBC.AX',   # Westpac
    'NAB.AX',   # National Australia Bank
    'ANZ.AX',   # ANZ Bank
    'MQG.AX',   # Macquarie Group
]

MARKET_INDICES = {
    'ASX200': '^AXJO',
    'SP500': '^GSPC',
    'NASDAQ': '^IXIC',
    'DOW': '^DJI'
}


# ============================================================================
# DATA FETCHING - yahooquery ONLY
# ============================================================================

def fetch_stock_data(symbol, period='1mo'):
    """
    Fetch stock OHLCV data using yahooquery ONLY
    
    Args:
        symbol: Stock ticker (e.g., 'CBA.AX')
        period: Period string (e.g., '1mo', '3mo')
        
    Returns:
        DataFrame with OHLCV data, or None on error
    """
    try:
        logger.info(f"Fetching {symbol} with yahooquery...")
        ticker = Ticker(symbol)
        hist = ticker.history(period=period)
        
        if isinstance(hist, pd.DataFrame) and not hist.empty:
            # Normalize column names to standard format
            hist.columns = [col.capitalize() for col in hist.columns]
            logger.info(f"✅ {symbol}: Retrieved {len(hist)} rows")
            return hist
        else:
            logger.warning(f"❌ {symbol}: No data returned")
            return None
            
    except Exception as e:
        logger.error(f"❌ {symbol}: Error - {e}")
        return None


def fetch_market_sentiment():
    """
    Calculate market sentiment using yahooquery ONLY
    
    Returns:
        dict with sentiment metrics
    """
    logger.info("Calculating market sentiment...")
    sentiment = {
        'timestamp': datetime.now().isoformat(),
        'indices': {},
        'overall_score': 0
    }
    
    for name, symbol in MARKET_INDICES.items():
        try:
            ticker = Ticker(symbol)
            hist = ticker.history(period='5d')
            
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                # Normalize columns
                hist.columns = [col.capitalize() for col in hist.columns]
                
                # Calculate change
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[0]
                change_pct = ((current_price - previous_price) / previous_price) * 100
                
                sentiment['indices'][name] = {
                    'symbol': symbol,
                    'current': float(current_price),
                    'change_pct': float(change_pct),
                    'status': 'positive' if change_pct > 0 else 'negative'
                }
                
                logger.info(f"  {name}: {change_pct:+.2f}%")
            else:
                logger.warning(f"  {name}: No data")
                
        except Exception as e:
            logger.error(f"  {name}: Error - {e}")
    
    # Calculate overall sentiment score
    if sentiment['indices']:
        changes = [idx['change_pct'] for idx in sentiment['indices'].values()]
        sentiment['overall_score'] = sum(changes) / len(changes)
        sentiment['market_status'] = 'bullish' if sentiment['overall_score'] > 0 else 'bearish'
    
    logger.info(f"Overall market sentiment: {sentiment['overall_score']:+.2f}% ({sentiment.get('market_status', 'neutral')})")
    return sentiment


# ============================================================================
# STOCK VALIDATION
# ============================================================================

def validate_stock(symbol, hist):
    """
    Validate stock meets basic criteria
    
    Args:
        symbol: Stock ticker
        hist: Historical data DataFrame
        
    Returns:
        bool: True if valid
    """
    if hist is None or hist.empty:
        logger.debug(f"  {symbol}: No data")
        return False
    
    try:
        # Get current price
        current_price = hist['Close'].iloc[-1]
        
        # Price check (ASX: $0.50 - $500)
        if not (0.50 <= current_price <= 500):
            logger.debug(f"  {symbol}: Price ${current_price:.2f} out of range")
            return False
        
        # Volume check
        avg_volume = hist['Volume'].mean()
        if avg_volume < 100000:  # Minimum 100k average volume
            logger.debug(f"  {symbol}: Volume {int(avg_volume):,} too low")
            return False
        
        logger.info(f"  ✅ {symbol}: Valid (Price: ${current_price:.2f}, Vol: {int(avg_volume):,})")
        return True
        
    except Exception as e:
        logger.debug(f"  {symbol}: Validation error - {e}")
        return False


# ============================================================================
# TECHNICAL ANALYSIS
# ============================================================================

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except:
        return 50.0  # Neutral


def analyze_stock(symbol, hist, market_sentiment):
    """
    Analyze stock with technical indicators
    
    Args:
        symbol: Stock ticker
        hist: Historical data DataFrame
        market_sentiment: Market sentiment dict
        
    Returns:
        dict with analysis results
    """
    try:
        # Get current metrics
        current_price = hist['Close'].iloc[-1]
        avg_volume = int(hist['Volume'].mean())
        
        # Calculate moving averages
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else current_price
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else ma_20
        
        # Calculate RSI
        rsi = calculate_rsi(hist['Close'])
        
        # Calculate volatility
        volatility = hist['Close'].pct_change().std() * 100
        
        # Simple scoring (0-100)
        score = 50  # Base score
        
        # Price vs MA
        if current_price > ma_20:
            score += 10
        if current_price > ma_50:
            score += 10
        
        # RSI scoring
        if 30 <= rsi <= 70:  # Not overbought/oversold
            score += 10
        
        # Volume scoring
        if avg_volume > 500000:  # High liquidity
            score += 10
        
        # Volatility scoring (lower is better)
        if volatility < 2.0:
            score += 10
        
        # Market sentiment boost
        if market_sentiment.get('market_status') == 'bullish':
            score += 5
        
        return {
            'symbol': symbol,
            'price': float(current_price),
            'volume': avg_volume,
            'ma_20': float(ma_20),
            'ma_50': float(ma_50),
            'rsi': float(rsi),
            'volatility': float(volatility),
            'score': min(100, score),  # Cap at 100
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"  {symbol}: Analysis error - {e}")
        return None


# ============================================================================
# MAIN SCREENING FUNCTION
# ============================================================================

def run_financial_sector_screening():
    """
    Run screening on Financial sector stocks - yahooquery ONLY
    """
    logger.info("="*80)
    logger.info("FINANCIAL SECTOR SCREENER - yahooquery ONLY")
    logger.info("="*80)
    
    # Step 1: Get market sentiment
    logger.info("\n" + "="*80)
    logger.info("STEP 1: Market Sentiment Analysis")
    logger.info("="*80)
    market_sentiment = fetch_market_sentiment()
    
    # Step 2: Screen stocks
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Screening Financial Sector Stocks")
    logger.info("="*80)
    
    results = []
    
    for symbol in FINANCIAL_SECTOR_STOCKS:
        logger.info(f"\nProcessing {symbol}...")
        
        # Fetch data
        hist = fetch_stock_data(symbol, period='3mo')
        
        if hist is None:
            logger.warning(f"  ❌ {symbol}: Skipped (no data)")
            continue
        
        # Validate
        if not validate_stock(symbol, hist):
            logger.warning(f"  ❌ {symbol}: Failed validation")
            continue
        
        # Analyze
        analysis = analyze_stock(symbol, hist, market_sentiment)
        
        if analysis:
            results.append(analysis)
            logger.info(f"  ✅ {symbol}: Score {analysis['score']}/100")
    
    # Step 3: Results
    logger.info("\n" + "="*80)
    logger.info("STEP 3: Results Summary")
    logger.info("="*80)
    
    if not results:
        logger.warning("No stocks passed screening!")
        return
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    logger.info(f"\nTop Financial Stocks (Total: {len(results)}):\n")
    logger.info(f"{'Rank':<6} {'Symbol':<10} {'Price':<10} {'Volume':<12} {'RSI':<8} {'Score':<8}")
    logger.info("-" * 70)
    
    for i, stock in enumerate(results, 1):
        logger.info(
            f"{i:<6} "
            f"{stock['symbol']:<10} "
            f"${stock['price']:<9.2f} "
            f"{stock['volume']:<12,} "
            f"{stock['rsi']:<8.1f} "
            f"{stock['score']:<8.0f}"
        )
    
    # Save results
    df = pd.DataFrame(results)
    output_file = 'financial_sector_results_yahooquery.csv'
    df.to_csv(output_file, index=False)
    logger.info(f"\n✅ Results saved to: {output_file}")
    
    logger.info("\n" + "="*80)
    logger.info("SCREENING COMPLETE")
    logger.info("="*80)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        run_financial_sector_screening()
    except KeyboardInterrupt:
        logger.info("\n\nScreening interrupted by user")
    except Exception as e:
        logger.error(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
