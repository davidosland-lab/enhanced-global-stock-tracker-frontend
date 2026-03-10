#!/usr/bin/env python3
"""
Regime-Aware Opportunity Scorer
Enhanced opportunity scoring with market regime intelligence

Author: Trading System v1.3.13 - REGIME EDITION
Date: January 6, 2026
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import numpy as np

# Import regime detection modules
try:
    from .market_regime_detector import MarketRegimeDetector, MarketRegime
    from .cross_market_features import CrossMarketFeatures
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from market_regime_detector import MarketRegimeDetector, MarketRegime
    from cross_market_features import CrossMarketFeatures

logger = logging.getLogger(__name__)


class RegimeAwareOpportunityScorer:
    """
    Enhanced opportunity scorer with market regime intelligence
    
    Key improvements over basic scorer:
    1. Detects market regime (US tech rally, commodity boom, risk-off, etc.)
    2. Adjusts scores based on sector-regime fit
    3. Adds cross-market features (NASDAQ, iron ore, AUD/USD, etc.)
    4. Applies dynamic penalties/bonuses based on macro environment
    5. Provides regime-aware explanations
    
    Example:
        US tech rally + commodities weak
        -> Reduce scores for Materials, Energy, Financials
        -> Slight boost for Technology, Healthcare
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Regime-Aware Opportunity Scorer
        
        Args:
            config_path: Path to screening_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "screening_config.json"
        
        self.config = self._load_config(config_path)
        self.scoring_config = self.config.get('scoring', {})
        self.weights = self.scoring_config.get('weights', {})
        self.penalties = self.scoring_config.get('penalties', {})
        self.bonuses = self.scoring_config.get('bonuses', {})
        
        # Initialize regime detection
        self.regime_detector = MarketRegimeDetector()
        self.feature_engineer = CrossMarketFeatures()
        
        # Regime influence weight (0-1) - OPTIMIZED via backtesting
        # 0 = ignore regime, 1 = fully regime-driven
        # Optimized 0.2 = 20% regime influence, 80% stock fundamentals
        # (Week 2 optimization: 0.2 outperforms 0.4 by +2.09%)
        self.regime_weight = self.config.get('regime_weight', 0.2)
        
        # Confidence threshold - OPTIMIZED via parameter tuning
        # Minimum confidence to include in scoring (0-1)
        # Optimized 0.3 = 30% minimum confidence
        # (Week 2 optimization: balances 58% accuracy with 100% coverage)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.3)
        
        # Regime-specific weights (adaptive by regime type)
        # Optimized via cross-validation
        self.regime_specific_weights = self.config.get('regime_specific_weights', {
            'NEUTRAL': 0.2,  # Modest regime influence
            'COMMODITY_WEAK': 0.0,  # Fundamental focus
            'COMMODITY_STRONG': 0.0,  # Fundamental focus
            'US_TECH_RALLY': 0.2,  # Modest regime influence
            'US_RISK_OFF': 0.3,  # Higher regime awareness in risk-off
            'DEFAULT': 0.2  # Default for other regimes
        })
        
        logger.info("[OK] Regime-Aware Opportunity Scorer initialized")
        logger.info(f"  Scoring Weights: {self.weights}")
        logger.info(f"  Base Regime Influence: {self.regime_weight*100:.0f}%")
        logger.info(f"  Confidence Threshold: {self.confidence_threshold*100:.0f}%")
        logger.info(f"  Adaptive Weights: {self.regime_specific_weights}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load screening configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'scoring': {
                'weights': {
                    'prediction_confidence': 0.30,
                    'technical_strength': 0.20,
                    'spi_alignment': 0.15,
                    'liquidity': 0.15,
                    'volatility': 0.10,
                    'sector_momentum': 0.10
                },
                'penalties': {
                    'low_volume': 10,
                    'high_volatility': 15,
                    'negative_sentiment': 20
                },
                'bonuses': {
                    'fresh_lstm_model': 5,
                    'high_win_rate': 10,
                    'sector_leader': 5
                }
            },
            'regime_weight': 0.2
        }
    
    def score_opportunities(
        self,
        stocks_with_predictions: List[Dict],
        market_data: Dict,
        spi_sentiment: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Calculate regime-aware opportunity scores for all stocks
        
        Args:
            stocks_with_predictions: List of stocks with prediction data
            market_data: Market data (SP500, NASDAQ, commodities, FX, rates)
            spi_sentiment: Optional SPI sentiment data
            
        Returns:
            List of stocks with opportunity_score added, sorted by score
        """
        logger.info(f"[*] Scoring {len(stocks_with_predictions)} opportunities with regime intelligence...")
        
        # Step 1: Detect market regime
        regime_data = self.regime_detector.detect_regime(market_data)
        primary_regime = regime_data['primary_regime']
        regime_strength = regime_data['regime_strength']
        regime_confidence = regime_data['confidence']
        
        logger.info(f"[#] Market Regime: {primary_regime.value}")
        logger.info(f"   Strength: {regime_strength:.2f}, Confidence: {regime_confidence:.2f}")
        logger.info(f"   {regime_data['regime_explanation'][:100]}...")
        
        # Step 2: Add cross-market features to each stock
        stocks_with_features = self.feature_engineer.add_features_batch(
            stocks_with_predictions,
            market_data
        )
        
        # Step 3: Score each stock with regime awareness
        scored_stocks = []
        
        for stock in stocks_with_features:
            try:
                # Calculate base opportunity score
                score_data = self._calculate_opportunity_score(
                    stock, 
                    spi_sentiment,
                    regime_data
                )
                
                # Add scores to stock data
                stock['opportunity_score'] = score_data['total_score']
                stock['base_score'] = score_data['base_score']
                stock['regime_adjustment'] = score_data['regime_adjustment']
                stock['score_breakdown'] = score_data['breakdown']
                stock['regime_impact'] = score_data['regime_impact']
                stock['score_explanation'] = score_data['explanation']
                
                scored_stocks.append(stock)
                
            except Exception as e:
                logger.error(f"[X] Scoring error for {stock.get('symbol', 'UNKNOWN')}: {e}", exc_info=True)
                stock['opportunity_score'] = 0
                stock['score_error'] = str(e)
                scored_stocks.append(stock)
        
        # Sort by opportunity score (descending)
        scored_stocks.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        if scored_stocks:
            top_stock = scored_stocks[0]
            logger.info(f"[OK] Scoring complete. Top opportunity: {top_stock.get('symbol')} "
                       f"(score: {top_stock.get('opportunity_score', 0):.1f}, "
                       f"regime adj: {top_stock.get('regime_adjustment', 0):+.1f})")
        
        # Add regime report to results
        for stock in scored_stocks:
            stock['market_regime'] = {
                'primary': primary_regime.value,
                'strength': regime_strength,
                'confidence': regime_confidence,
                'explanation': regime_data['regime_explanation']
            }
        
        return scored_stocks
    
    def _calculate_opportunity_score(
        self,
        stock: Dict,
        spi_sentiment: Optional[Dict],
        regime_data: Dict
    ) -> Dict:
        """
        Calculate regime-aware opportunity score
        
        Process:
        1. Calculate base score (traditional factors)
        2. Calculate regime adjustment (sector fit with macro)
        3. Combine: final_score = base_score * (1 - regime_weight) + regime_adjusted * regime_weight
        
        Args:
            stock: Stock data with predictions and cross-market features
            spi_sentiment: Market sentiment data
            regime_data: Regime detection results
            
        Returns:
            Dictionary with scores and breakdown
        """
        
        # ===== STEP 1: BASE SCORING (Traditional) =====
        
        # Base factors (all return 0-1)
        prediction_score = self._score_prediction_confidence(stock)
        technical_score = self._score_technical_strength(stock)
        spi_score = self._score_spi_alignment(stock, spi_sentiment)
        liquidity_score = self._score_liquidity(stock)
        volatility_score = self._score_volatility(stock)
        sector_score = self._score_sector_momentum(stock)
        
        # Calculate weighted total (0-100 scale)
        base_score = (
            prediction_score * self.weights.get('prediction_confidence', 0.30) +
            technical_score * self.weights.get('technical_strength', 0.20) +
            spi_score * self.weights.get('spi_alignment', 0.15) +
            liquidity_score * self.weights.get('liquidity', 0.15) +
            volatility_score * self.weights.get('volatility', 0.10) +
            sector_score * self.weights.get('sector_momentum', 0.10)
        ) * 100
        
        # Apply traditional penalties/bonuses
        traditional_adjustments = self._apply_traditional_adjustments(stock, spi_sentiment)
        base_score += traditional_adjustments
        
        # ===== STEP 2: REGIME ADJUSTMENT =====
        
        # Get sector-specific regime impact
        sector = stock.get('sector', 'Unknown')
        sector_impacts = regime_data.get('sector_impacts', {})
        regime_sector_bias = sector_impacts.get(sector, 0.0)  # -1 to +1
        
        # Get cross-market opportunity adjustment
        cross_market_adjustment = stock.get('opportunity_adjustment', 0.0)
        
        # Combine regime signals
        # regime_sector_bias: -1 to +1 (from regime detector)
        # cross_market_adjustment: typically -5 to +5 (from feature engineering)
        # Normalize cross_market to -1 to +1 range
        normalized_cross_market = np.tanh(cross_market_adjustment / 3.0)
        
        # Combined regime signal (-1 to +1)
        regime_signal = (regime_sector_bias * 0.6 + normalized_cross_market * 0.4)
        
        # Convert to score adjustment (-30 to +30 points)
        regime_adjustment = regime_signal * 30
        
        # ===== STEP 3: CONFIDENCE SCALING =====
        
        # Scale regime adjustment by regime confidence
        regime_confidence = regime_data.get('confidence', 0.5)
        scaled_regime_adjustment = regime_adjustment * regime_confidence
        
        # ===== STEP 4: ADAPTIVE REGIME WEIGHT =====
        
        # Use regime-specific weight if available (from optimization)
        primary_regime_value = regime_data['primary_regime'].value
        adaptive_weight = self.regime_specific_weights.get(
            primary_regime_value,
            self.regime_specific_weights.get('DEFAULT', self.regime_weight)
        )
        
        # ===== STEP 5: CONFIDENCE FILTERING =====
        
        # Check if prediction meets confidence threshold
        prediction_confidence = stock.get('confidence', 0) / 100
        if prediction_confidence < self.confidence_threshold:
            # Below threshold: reduce regime influence, rely more on fundamentals
            adaptive_weight *= 0.5
        
        # ===== STEP 6: FINAL SCORE =====
        
        # Blend base score and regime adjustment
        # adaptive_weight controls how much regime matters (varies by regime type)
        final_score = base_score + (scaled_regime_adjustment * adaptive_weight)
        
        # Clamp to 0-100
        final_score = max(0, min(100, final_score))
        
        # ===== BREAKDOWN =====
        
        breakdown = {
            'prediction_confidence': prediction_score * 100,
            'technical_strength': technical_score * 100,
            'spi_alignment': spi_score * 100,
            'liquidity': liquidity_score * 100,
            'volatility': volatility_score * 100,
            'sector_momentum': sector_score * 100,
            'base_total': base_score,
            'traditional_adjustments': traditional_adjustments,
            'regime_sector_bias': regime_sector_bias,
            'cross_market_adjustment': cross_market_adjustment,
            'regime_signal': regime_signal,
            'regime_adjustment': scaled_regime_adjustment,
            'adaptive_weight': adaptive_weight,
            'confidence_threshold': self.confidence_threshold,
            'final_score': final_score
        }
        
        # ===== REGIME IMPACT ANALYSIS =====
        
        if regime_signal < -0.3:
            impact_label = "[X] STRONG HEADWINDS"
            impact_color = "red"
        elif regime_signal < -0.1:
            impact_label = "[!] MODERATE HEADWINDS"
            impact_color = "orange"
        elif regime_signal > 0.3:
            impact_label = "[OK] STRONG TAILWINDS"
            impact_color = "green"
        elif regime_signal > 0.1:
            impact_label = "[+] MODERATE TAILWINDS"
            impact_color = "lightgreen"
        else:
            impact_label = "[-] NEUTRAL"
            impact_color = "gray"
        
        regime_impact = {
            'signal': regime_signal,
            'adjustment': scaled_regime_adjustment,
            'label': impact_label,
            'color': impact_color,
            'sector': sector,
            'regime': regime_data['primary_regime'].value
        }
        
        # ===== EXPLANATION =====
        
        explanation = self._generate_score_explanation(
            stock, base_score, regime_signal, scaled_regime_adjustment, regime_data
        )
        
        return {
            'total_score': final_score,
            'base_score': base_score,
            'regime_adjustment': scaled_regime_adjustment,
            'breakdown': breakdown,
            'regime_impact': regime_impact,
            'explanation': explanation
        }
    
    def _score_prediction_confidence(self, stock: Dict) -> float:
        """Score based on prediction confidence (0-1)"""
        prediction = stock.get('prediction', 'HOLD')
        confidence = stock.get('confidence', 0) / 100
        
        score = confidence
        
        if prediction == 'BUY':
            score *= 1.2
        elif prediction == 'SELL':
            score *= 0.8
        elif prediction == 'HOLD':
            score *= 0.5
        
        return min(score, 1.0)
    
    def _score_technical_strength(self, stock: Dict) -> float:
        """Score based on technical indicators (0-1)"""
        technical = stock.get('technical', {})
        screening_score = stock.get('score', 50)
        
        # RSI score
        rsi = technical.get('rsi', 50)
        if 40 <= rsi <= 60:
            rsi_score = 1.0
        elif 30 <= rsi <= 70:
            rsi_score = 0.8
        elif rsi < 30:
            rsi_score = 0.9  # Oversold opportunity
        else:
            rsi_score = 0.4  # Overbought caution
        
        # Price vs MA
        price_vs_ma20 = technical.get('price_vs_ma20', 0)
        ma_score = 1.0 if price_vs_ma20 > 0 else 0.5
        
        # Screening score
        screen_score = screening_score / 100
        
        # Weighted average
        score = (rsi_score * 0.3 + ma_score * 0.3 + screen_score * 0.4)
        
        return score
    
    def _score_spi_alignment(self, stock: Dict, spi_sentiment: Optional[Dict]) -> float:
        """Score based on alignment with market sentiment (0-1)"""
        if not spi_sentiment:
            return 0.5  # Neutral if no sentiment data
        
        prediction = stock.get('prediction', 'HOLD')
        sentiment_score = spi_sentiment.get('sentiment_score', 50)
        
        # High sentiment (bullish market)
        if sentiment_score > 60:
            if prediction == 'BUY':
                return 1.0  # Aligned
            elif prediction == 'HOLD':
                return 0.6
            else:
                return 0.3  # Contrarian
        
        # Low sentiment (bearish market)
        elif sentiment_score < 40:
            if prediction == 'SELL':
                return 0.8  # Defensive
            elif prediction == 'HOLD':
                return 0.6
            else:
                return 0.4  # Risky
        
        # Neutral market
        else:
            return 0.6 if prediction == 'HOLD' else 0.7
    
    def _score_liquidity(self, stock: Dict) -> float:
        """Score based on liquidity (0-1)"""
        volume = stock.get('volume', 0)
        market_cap = stock.get('market_cap', 0)
        
        # Volume score
        if volume > 2000000:
            volume_score = 1.0
        elif volume > 1000000:
            volume_score = 0.9
        elif volume > 500000:
            volume_score = 0.7
        else:
            volume_score = 0.4
        
        # Market cap score
        if market_cap > 10_000_000_000:  # > USD10B
            cap_score = 1.0
        elif market_cap > 1_000_000_000:  # > USD1B
            cap_score = 0.8
        elif market_cap > 500_000_000:  # > USD500M
            cap_score = 0.6
        else:
            cap_score = 0.3
        
        return (volume_score * 0.6 + cap_score * 0.4)
    
    def _score_volatility(self, stock: Dict) -> float:
        """Score based on volatility (0-1, lower volatility = higher score)"""
        technical = stock.get('technical', {})
        volatility = technical.get('volatility', 0.03)
        
        # Lower volatility is better for opportunity
        if volatility < 0.02:  # < 2%
            return 1.0
        elif volatility < 0.03:  # < 3%
            return 0.8
        elif volatility < 0.05:  # < 5%
            return 0.6
        else:
            return 0.3
    
    def _score_sector_momentum(self, stock: Dict) -> float:
        """Score based on sector momentum (0-1)"""
        # This would ideally use real sector performance data
        # For now, use a placeholder
        sector = stock.get('sector', 'Unknown')
        
        # Could enhance with actual sector performance tracking
        return 0.6  # Neutral baseline
    
    def _apply_traditional_adjustments(self, stock: Dict, spi_sentiment: Optional[Dict]) -> float:
        """Apply traditional penalties and bonuses"""
        adjustment = 0.0
        
        # Low volume penalty
        if stock.get('volume', 0) < 500000:
            adjustment -= self.penalties.get('low_volume', 10)
        
        # High volatility penalty
        technical = stock.get('technical', {})
        if technical.get('volatility', 0) > 0.05:
            adjustment -= self.penalties.get('high_volatility', 15)
        
        # Sector leader bonus
        if stock.get('is_sector_leader', False):
            adjustment += self.bonuses.get('sector_leader', 5)
        
        return adjustment
    
    def _generate_score_explanation(
        self,
        stock: Dict,
        base_score: float,
        regime_signal: float,
        regime_adjustment: float,
        regime_data: Dict
    ) -> str:
        """Generate human-readable explanation of the score"""
        
        symbol = stock.get('symbol', 'UNKNOWN')
        sector = stock.get('sector', 'Unknown')
        prediction = stock.get('prediction', 'HOLD')
        confidence = stock.get('confidence', 0)
        
        explanation = [
            f"Stock: {symbol} ({sector})",
            f"Prediction: {prediction} ({confidence}% confidence)",
            f"Base Score: {base_score:.1f}/100",
        ]
        
        if regime_signal < -0.1:
            explanation.append(f"Regime Impact: {regime_adjustment:+.1f} points (HEADWINDS)")
            explanation.append(f"Reason: {regime_data['regime_explanation'][:150]}")
        elif regime_signal > 0.1:
            explanation.append(f"Regime Impact: {regime_adjustment:+.1f} points (TAILWINDS)")
            explanation.append(f"Reason: Favorable macro environment for {sector}")
        else:
            explanation.append(f"Regime Impact: Neutral")
        
        return " | ".join(explanation)
    
    def get_regime_report(self) -> str:
        """Get current regime report"""
        return self.regime_detector.get_regime_report()
    
    def filter_top_opportunities(
        self,
        scored_stocks: List[Dict],
        min_score: Optional[float] = None,
        top_n: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter to top opportunities
        
        Args:
            scored_stocks: List of scored stocks (already sorted)
            min_score: Minimum opportunity score (default from config)
            top_n: Maximum number to return (default from config)
            
        Returns:
            Filtered list of top opportunities
        """
        if min_score is None:
            min_score = self.config.get('screening', {}).get('opportunity_threshold', 65)
        
        if top_n is None:
            top_n = self.config.get('screening', {}).get('top_picks_count', 10)
        
        # Filter by minimum score
        filtered = [s for s in scored_stocks if s.get('opportunity_score', 0) >= min_score]
        
        # Limit to top N
        filtered = filtered[:top_n]
        
        logger.info(f"[LIST] Filtered to {len(filtered)} top opportunities (min_score={min_score}, top_n={top_n})")
        
        return filtered


def test_regime_aware_scorer():
    """Test the regime-aware opportunity scorer"""
    
    print("\n" + "="*80)
    print("TESTING REGIME-AWARE OPPORTUNITY SCORER")
    print("="*80)
    
    scorer = RegimeAwareOpportunityScorer()
    
    # Sample market data (US tech rally, commodities weak - bad for ASX)
    market_data = {
        'sp500_change': 0.8,
        'nasdaq_change': 1.5,
        'iron_ore_change': -2.5,
        'oil_change': -1.8,
        'aud_usd_change': -0.6,
        'usd_index_change': 0.5,
        'us_10y_change': -3,
        'au_10y_change': -1,
        'vix_level': 15,
        'timestamp': datetime.now().isoformat()
    }
    
    # Sample stocks with predictions
    stocks = [
        {
            'symbol': 'BHP.AX',
            'name': 'BHP Group',
            'sector': 'Materials',
            'prediction': 'BUY',
            'confidence': 75,
            'price': 45.20,
            'volume': 8000000,
            'market_cap': 230_000_000_000,
            'technical': {
                'rsi': 55,
                'ma_20': 44.5,
                'price_vs_ma20': 1.57,
                'volatility': 0.03
            },
            'score': 82
        },
        {
            'symbol': 'CBA.AX',
            'name': 'Commonwealth Bank',
            'sector': 'Financials',
            'prediction': 'BUY',
            'confidence': 70,
            'price': 105.50,
            'volume': 5000000,
            'market_cap': 180_000_000_000,
            'technical': {
                'rsi': 58,
                'ma_20': 104.0,
                'price_vs_ma20': 1.44,
                'volatility': 0.025
            },
            'score': 85
        },
        {
            'symbol': 'CSL.AX',
            'name': 'CSL Limited',
            'sector': 'Healthcare',
            'prediction': 'BUY',
            'confidence': 68,
            'price': 285.00,
            'volume': 1200000,
            'market_cap': 125_000_000_000,
            'technical': {
                'rsi': 52,
                'ma_20': 282.0,
                'price_vs_ma20': 1.06,
                'volatility': 0.028
            },
            'score': 78
        },
    ]
    
    # Score opportunities
    scored_stocks = scorer.score_opportunities(stocks, market_data)
    
    # Display results
    print("\n" + scorer.get_regime_report())
    
    print("\n" + "="*80)
    print("SCORED OPPORTUNITIES (Ranked)")
    print("="*80)
    
    for i, stock in enumerate(scored_stocks, 1):
        print(f"\n{i}. {stock['symbol']} - {stock['name']}")
        print(f"   Sector: {stock['sector']}")
        print(f"   Prediction: {stock['prediction']} ({stock['confidence']}% confidence)")
        print(f"   Base Score: {stock['base_score']:.1f}/100")
        print(f"   Regime Adjustment: {stock['regime_adjustment']:+.1f}")
        print(f"   Final Score: {stock['opportunity_score']:.1f}/100")
        print(f"   Regime Impact: {stock['regime_impact']['label']}")
        print(f"   Explanation: {stock['score_explanation']}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_regime_aware_scorer()
