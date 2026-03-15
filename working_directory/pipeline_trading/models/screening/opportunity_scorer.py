"""
Opportunity Scorer Module

Ranks stocks based on composite opportunity score.
Combines prediction confidence, technical strength, market sentiment,
and other factors to identify top investment opportunities.

Features:
- Composite opportunity scoring (0-100)
- Weighted factor analysis
- Penalty and bonus adjustments
- Risk-adjusted ranking
- Top opportunities filtering
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpportunityScorer:
    """
    Ranks stocks based on investment opportunity score.
    Combines multiple factors for comprehensive ranking.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize Opportunity Scorer
        
        Args:
            config_path: Path to screening_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "screening_config.json"
        
        self.config = self._load_config(config_path)
        self.scoring_config = self.config['scoring']
        self.weights = self.scoring_config['weights']
        self.penalties = self.scoring_config['penalties']
        self.bonuses = self.scoring_config['bonuses']
        
        logger.info("Opportunity Scorer initialized")
        logger.info(f"  Scoring Weights: {self.weights}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load screening configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def score_opportunities(
        self,
        stocks_with_predictions: List[Dict],
        spi_sentiment: Dict = None
    ) -> List[Dict]:
        """
        Calculate opportunity scores for all stocks
        
        Args:
            stocks_with_predictions: List of stocks with prediction data
            spi_sentiment: Market sentiment data
            
        Returns:
            List of stocks with opportunity_score added, sorted by score
        """
        logger.info(f"Scoring {len(stocks_with_predictions)} opportunities...")
        
        scored_stocks = []
        
        for stock in stocks_with_predictions:
            try:
                # Calculate opportunity score
                score = self._calculate_opportunity_score(stock, spi_sentiment)
                
                # Add score to stock data
                stock['opportunity_score'] = score['total_score']
                stock['score_breakdown'] = score['breakdown']
                stock['score_factors'] = score['factors']
                
                scored_stocks.append(stock)
                
            except Exception as e:
                logger.error(f"Scoring error for {stock.get('symbol', 'UNKNOWN')}: {e}")
                stock['opportunity_score'] = 0
                stock['score_error'] = str(e)
                scored_stocks.append(stock)
        
        # Sort by opportunity score (descending)
        scored_stocks.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        logger.info(f"Scoring complete. Top score: {scored_stocks[0]['opportunity_score']:.1f}")
        
        return scored_stocks
    
    def _calculate_opportunity_score(
        self,
        stock: Dict,
        spi_sentiment: Dict = None
    ) -> Dict:
        """
        Calculate composite opportunity score (0-100)
        
        Scoring factors:
        1. Prediction Confidence (30%): How confident is the prediction?
        2. Technical Strength (20%): Technical indicators quality
        3. SPI Alignment (15%): Alignment with market sentiment
        4. Liquidity (15%): Trading volume and market cap
        5. Volatility (10%): Risk assessment
        6. Sector Momentum (10%): Sector performance
        
        Plus penalties and bonuses.
        
        Args:
            stock: Stock data with predictions
            spi_sentiment: Market sentiment data
            
        Returns:
            Dictionary with total score and breakdown
        """
        breakdown = {}
        
        # Base factors
        prediction_score = self._score_prediction_confidence(stock)
        technical_score = self._score_technical_strength(stock)
        spi_score = self._score_spi_alignment(stock, spi_sentiment)
        liquidity_score = self._score_liquidity(stock)
        volatility_score = self._score_volatility(stock)
        sector_score = self._score_sector_momentum(stock)
        
        # Calculate weighted total
        total = (
            prediction_score * self.weights['prediction_confidence'] +
            technical_score * self.weights['technical_strength'] +
            spi_score * self.weights['spi_alignment'] +
            liquidity_score * self.weights['liquidity'] +
            volatility_score * self.weights['volatility'] +
            sector_score * self.weights['sector_momentum']
        ) * 100  # Convert to 0-100 scale
        
        breakdown = {
            'prediction_confidence': prediction_score * 100,
            'technical_strength': technical_score * 100,
            'spi_alignment': spi_score * 100,
            'liquidity': liquidity_score * 100,
            'volatility': volatility_score * 100,
            'sector_momentum': sector_score * 100,
            'base_total': total
        }
        
        # Apply penalties and bonuses
        adjustments = self._apply_adjustments(stock, spi_sentiment)
        total += adjustments['total_adjustment']
        
        # Ensure score is within bounds
        total = max(0, min(100, total))
        
        return {
            'total_score': total,
            'breakdown': breakdown,
            'factors': {
                'adjustments': adjustments,
                'prediction': stock.get('prediction'),
                'confidence': stock.get('confidence', 0)
            }
        }
    
    def _score_prediction_confidence(self, stock: Dict) -> float:
        """
        Score based on prediction confidence (0-1)
        
        Factors:
        - Prediction confidence level
        - Prediction direction strength
        - BUY signals valued higher than SELL
        """
        prediction = stock.get('prediction', 'HOLD')
        confidence = stock.get('confidence', 0) / 100  # Normalize to 0-1
        
        # Base score from confidence
        score = confidence
        
        # Boost for BUY signals
        if prediction == 'BUY':
            score *= 1.2  # 20% bonus
        elif prediction == 'SELL':
            score *= 0.8  # 20% penalty (we prefer buys)
        elif prediction == 'HOLD':
            score *= 0.5  # Neutral is less valuable
        
        return min(score, 1.0)
    
    def _score_technical_strength(self, stock: Dict) -> float:
        """
        Score based on technical indicators (0-1)
        
        Factors:
        - RSI (optimal range)
        - Price vs moving averages
        - Screening score
        """
        technical = stock.get('technical', {})
        screening_score = stock.get('score', 50)  # From stock scanner
        
        # RSI score (prefer 40-60 range)
        rsi = technical.get('rsi', 50)
        if 40 <= rsi <= 60:
            rsi_score = 1.0
        elif 30 <= rsi <= 70:
            rsi_score = 0.8
        elif rsi < 30:  # Oversold (opportunity)
            rsi_score = 0.9
        else:  # Overbought
            rsi_score = 0.4
        
        # Price vs MA score
        price_vs_ma20 = technical.get('price_vs_ma20', 0)
        if price_vs_ma20 > 0:
            ma_score = 1.0
        else:
            ma_score = 0.5
        
        # Screening score (normalize from 0-100 to 0-1)
        screen_score = screening_score / 100
        
        # Weighted average
        score = (rsi_score * 0.3 + ma_score * 0.3 + screen_score * 0.4)
        
        return score
    
    def _score_spi_alignment(
        self,
        stock: Dict,
        spi_sentiment: Dict = None
    ) -> float:
        """
        Score based on alignment with market sentiment (0-1)
        
        Factors:
        - Stock prediction vs SPI prediction alignment
        - Market sentiment strength
        """
        if not spi_sentiment:
            return 0.5  # Neutral if no sentiment data
        
        stock_prediction = stock.get('prediction', 'HOLD')
        gap_prediction = spi_sentiment.get('gap_prediction', {})
        market_direction = gap_prediction.get('direction', 'neutral')
        spi_confidence = gap_prediction.get('confidence', 50) / 100
        
        # Check alignment
        if stock_prediction == 'BUY' and market_direction == 'bullish':
            alignment_score = 1.0  # Perfect alignment
        elif stock_prediction == 'SELL' and market_direction == 'bearish':
            alignment_score = 1.0  # Perfect alignment
        elif stock_prediction == 'HOLD' or market_direction == 'neutral':
            alignment_score = 0.5  # Neutral
        else:
            alignment_score = 0.3  # Misalignment (contrarian opportunity?)
        
        # Weight by SPI confidence
        score = alignment_score * spi_confidence + 0.5 * (1 - spi_confidence)
        
        return score
    
    def _score_liquidity(self, stock: Dict) -> float:
        """
        Score based on liquidity (0-1)
        
        Factors:
        - Average volume
        - Market cap
        """
        volume = stock.get('volume', 0)
        market_cap = stock.get('market_cap', 0)
        
        # Volume score
        if volume > 5_000_000:
            vol_score = 1.0
        elif volume > 2_000_000:
            vol_score = 0.8
        elif volume > 1_000_000:
            vol_score = 0.6
        elif volume > 500_000:
            vol_score = 0.4
        else:
            vol_score = 0.2
        
        # Market cap score
        if market_cap > 10_000_000_000:
            cap_score = 1.0
        elif market_cap > 5_000_000_000:
            cap_score = 0.8
        elif market_cap > 1_000_000_000:
            cap_score = 0.6
        else:
            cap_score = 0.4
        
        # Average
        score = (vol_score * 0.6 + cap_score * 0.4)
        
        return score
    
    def _score_volatility(self, stock: Dict) -> float:
        """
        Score based on volatility/risk (0-1)
        
        Lower volatility = Higher score (less risk)
        """
        technical = stock.get('technical', {})
        volatility = technical.get('volatility', 0.05)
        beta = stock.get('beta', 1.0)
        
        # Volatility score (prefer low volatility)
        if volatility < 0.02:
            vol_score = 1.0
        elif volatility < 0.04:
            vol_score = 0.8
        elif volatility < 0.06:
            vol_score = 0.6
        else:
            vol_score = 0.4
        
        # Beta score (prefer 0.8-1.3 range)
        if 0.8 <= beta <= 1.3:
            beta_score = 1.0
        elif 0.5 <= beta <= 1.5:
            beta_score = 0.8
        else:
            beta_score = 0.5
        
        # Average
        score = (vol_score * 0.7 + beta_score * 0.3)
        
        return score
    
    def _score_sector_momentum(self, stock: Dict) -> float:
        """
        Score based on sector performance (0-1)
        
        Note: This is a placeholder. In full implementation,
        would track sector performance over time.
        """
        # Use screening score as proxy for sector strength
        screening_score = stock.get('score', 50)
        
        # High screening score suggests strong sector positioning
        return screening_score / 100
    
    def _apply_adjustments(
        self,
        stock: Dict,
        spi_sentiment: Dict = None
    ) -> Dict:
        """
        Apply penalties and bonuses to base score
        
        Returns:
            Dictionary with adjustment details
        """
        adjustments = {
            'penalties': [],
            'bonuses': [],
            'total_adjustment': 0
        }
        
        # PENALTIES
        
        # Low volume penalty
        if stock.get('volume', float('inf')) < 500_000:
            penalty = self.penalties['low_volume']
            adjustments['penalties'].append({
                'type': 'low_volume',
                'amount': -penalty
            })
            adjustments['total_adjustment'] -= penalty
        
        # High volatility penalty
        technical = stock.get('technical', {})
        if technical.get('volatility', 0) > 0.06:
            penalty = self.penalties['high_volatility']
            adjustments['penalties'].append({
                'type': 'high_volatility',
                'amount': -penalty
            })
            adjustments['total_adjustment'] -= penalty
        
        # Negative sentiment penalty (contrarian to market)
        if spi_sentiment:
            gap_pred = spi_sentiment.get('gap_prediction', {})
            if (stock.get('prediction') == 'SELL' and 
                gap_pred.get('direction') == 'bullish'):
                penalty = self.penalties['negative_sentiment']
                adjustments['penalties'].append({
                    'type': 'contrarian_position',
                    'amount': -penalty
                })
                adjustments['total_adjustment'] -= penalty
        
        # BONUSES
        
        # Fresh LSTM model bonus (if available)
        # TODO: Check model age from metadata
        
        # High win rate bonus (if available from backtesting)
        # TODO: Check historical win rate
        
        # Sector leader bonus
        if stock.get('score', 0) >= 85:
            bonus = self.bonuses['sector_leader']
            adjustments['bonuses'].append({
                'type': 'sector_leader',
                'amount': bonus
            })
            adjustments['total_adjustment'] += bonus
        
        return adjustments
    
    def filter_top_opportunities(
        self,
        scored_stocks: List[Dict],
        min_score: float = None,
        top_n: int = None
    ) -> List[Dict]:
        """
        Filter stocks to top opportunities
        
        Args:
            scored_stocks: List of scored stocks (sorted)
            min_score: Minimum opportunity score threshold
            top_n: Number of top stocks to return
            
        Returns:
            Filtered list of top opportunities
        """
        if min_score is None:
            min_score = self.config['screening']['opportunity_threshold']
        
        if top_n is None:
            top_n = self.config['screening']['top_picks_count']
        
        # Filter by minimum score
        filtered = [s for s in scored_stocks if s['opportunity_score'] >= min_score]
        
        # Return top N
        return filtered[:top_n]
    
    def get_opportunity_summary(self, scored_stocks: List[Dict]) -> Dict:
        """
        Generate summary of scored opportunities
        
        Args:
            scored_stocks: List of scored stocks
            
        Returns:
            Dictionary with summary statistics
        """
        if not scored_stocks:
            return {'total': 0}
        
        scores = [s['opportunity_score'] for s in scored_stocks]
        
        # Count by score ranges
        high_opportunity = [s for s in scored_stocks if s['opportunity_score'] >= 80]
        medium_opportunity = [s for s in scored_stocks 
                             if 65 <= s['opportunity_score'] < 80]
        low_opportunity = [s for s in scored_stocks if s['opportunity_score'] < 65]
        
        return {
            'total': len(scored_stocks),
            'avg_score': np.mean(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'high_opportunity_count': len(high_opportunity),
            'medium_opportunity_count': len(medium_opportunity),
            'low_opportunity_count': len(low_opportunity),
            'top_opportunities': scored_stocks[:10]
        }


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_opportunity_scorer():
    """Test the opportunity scorer"""
    print("\n" + "="*80)
    print("OPPORTUNITY SCORER TEST")
    print("="*80 + "\n")
    
    # Initialize scorer
    scorer = OpportunityScorer()
    
    # Sample stocks with predictions
    sample_stocks = [
        {
            'symbol': 'CBA.AX',
            'name': 'Commonwealth Bank',
            'price': 105.50,
            'market_cap': 180000000000,
            'volume': 5000000,
            'beta': 1.1,
            'technical': {
                'ma_20': 104.0,
                'ma_50': 102.5,
                'rsi': 55.0,
                'volatility': 0.025,
                'price_vs_ma20': 1.44
            },
            'score': 85.0,
            'prediction': 'BUY',
            'confidence': 75
        },
        {
            'symbol': 'BHP.AX',
            'name': 'BHP Group',
            'price': 45.20,
            'market_cap': 230000000000,
            'volume': 8000000,
            'beta': 1.3,
            'technical': {
                'ma_20': 44.5,
                'ma_50': 43.0,
                'rsi': 62.0,
                'volatility': 0.03,
                'price_vs_ma20': 1.57
            },
            'score': 82.0,
            'prediction': 'BUY',
            'confidence': 68
        },
        {
            'symbol': 'NAB.AX',
            'name': 'National Australia Bank',
            'price': 32.40,
            'market_cap': 105000000000,
            'volume': 4500000,
            'beta': 1.2,
            'technical': {
                'ma_20': 32.0,
                'ma_50': 31.5,
                'rsi': 48.0,
                'volatility': 0.028,
                'price_vs_ma20': 1.25
            },
            'score': 78.0,
            'prediction': 'HOLD',
            'confidence': 55
        }
    ]
    
    # Sample SPI sentiment
    spi_sentiment = {
        'sentiment_score': 65,
        'gap_prediction': {
            'predicted_gap_pct': 0.5,
            'confidence': 75,
            'direction': 'bullish'
        }
    }
    
    print("Scoring opportunities...\n")
    
    # Score opportunities
    scored = scorer.score_opportunities(sample_stocks, spi_sentiment)
    
    # Display results
    print("-"*80)
    print("OPPORTUNITY SCORES")
    print("-"*80)
    
    for i, stock in enumerate(scored, 1):
        print(f"\n{i}. {stock['symbol']} - {stock['name']}")
        print(f"   Opportunity Score: {stock['opportunity_score']:.1f}/100")
        print(f"   Prediction: {stock['prediction']} (Confidence: {stock['confidence']}%)")
        print(f"   Breakdown:")
        for factor, value in stock['score_breakdown'].items():
            if factor != 'base_total':
                print(f"     {factor:25s}: {value:5.1f}")
    
    # Summary
    summary = scorer.get_opportunity_summary(scored)
    print("\n" + "-"*80)
    print("SUMMARY")
    print("-"*80)
    print(f"Total Analyzed: {summary['total']}")
    print(f"Average Score: {summary['avg_score']:.1f}")
    print(f"High Opportunities (≥80): {summary['high_opportunity_count']}")
    print(f"Medium Opportunities (65-80): {summary['medium_opportunity_count']}")
    print(f"Low Opportunities (<65): {summary['low_opportunity_count']}")


if __name__ == "__main__":
    test_opportunity_scorer()
