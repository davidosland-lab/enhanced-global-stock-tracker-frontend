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
        spi_sentiment: Dict = None,
        ai_scores: Dict = None,
        market_status: Dict = None
    ) -> List[Dict]:
        """
        Calculate opportunity scores for all stocks (mode-aware)
        
        Args:
            stocks_with_predictions: List of stocks with prediction data
            spi_sentiment: Market sentiment data
            ai_scores: Optional AI scoring data {symbol: {scores}}
            market_status: Optional market hours status (for intraday mode)
            
        Returns:
            List of stocks with opportunity_score added, sorted by score
        """
        # Determine scoring mode
        if market_status and market_status.get('is_open', False):
            pipeline_mode = 'intraday'
            logger.info(f"📈 Intraday scoring mode active")
            logger.info(f"  Market: {market_status.get('trading_hours_elapsed_pct', 0):.1f}% complete")
        else:
            pipeline_mode = 'overnight'
            logger.info(f"🌙 Overnight scoring mode active")
        
        logger.info(f"Scoring {len(stocks_with_predictions)} opportunities...")
        
        # Check if AI scoring is enabled
        ai_enabled = ai_scores is not None and len(ai_scores) > 0
        if ai_enabled:
            logger.info(f"  🤖 AI-enhanced scoring enabled ({len(ai_scores)} stocks have AI scores)")
        
        scored_stocks = []
        
        for stock in stocks_with_predictions:
            try:
                # Calculate base opportunity score (mode-aware)
                if pipeline_mode == 'intraday':
                    score = self._calculate_intraday_score(stock, market_status, spi_sentiment)
                else:
                    score = self._calculate_opportunity_score(stock, spi_sentiment)
                
                # Add AI score if available
                symbol = stock.get('symbol', '')
                if ai_enabled and symbol in ai_scores:
                    ai_data = ai_scores[symbol]
                    score = self._integrate_ai_score(score, ai_data)
                    stock['ai_enhanced'] = True
                    stock['ai_score_data'] = ai_data
                else:
                    stock['ai_enhanced'] = False
                
                # Add score to stock data
                stock['opportunity_score'] = score['total_score']
                stock['score_breakdown'] = score['breakdown']
                stock['score_factors'] = score['factors']
                stock['pipeline_mode'] = pipeline_mode
                
                scored_stocks.append(stock)
                
            except Exception as e:
                logger.error(f"Scoring error for {stock.get('symbol', 'UNKNOWN')}: {e}")
                stock['opportunity_score'] = 0
                stock['score_error'] = str(e)
                stock['pipeline_mode'] = pipeline_mode
                scored_stocks.append(stock)
        
        # Sort by opportunity score (descending)
        scored_stocks.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        if scored_stocks:
            logger.info(f"Scoring complete. Top score: {scored_stocks[0]['opportunity_score']:.1f}")
            logger.info(f"  Mode: {pipeline_mode.upper()}")
            if ai_enabled:
                ai_enhanced_count = sum(1 for s in scored_stocks if s.get('ai_enhanced', False))
                logger.info(f"  🤖 {ai_enhanced_count} stocks enhanced with AI scores")
        
        return scored_stocks
    
    def _integrate_ai_score(self, base_score: Dict, ai_data: Dict) -> Dict:
        """
        Integrate AI scores into the base opportunity score.
        
        Args:
            base_score: Base scoring result
            ai_data: AI scoring data
            
        Returns:
            Updated score with AI component
        """
        # Extract AI scores (0-100)
        ai_overall = ai_data.get('overall_ai_score', 50)
        
        # Original weights (without AI): total 100%
        # - prediction_confidence: 30%
        # - technical_strength: 20%
        # - spi_alignment: 15%
        # - liquidity: 15%
        # - volatility: 10%
        # - sector_momentum: 10%
        
        # New weights (with AI at 15%): reduce others proportionally
        # - prediction_confidence: 25% (was 30%)
        # - technical_strength: 20%
        # - spi_alignment: 15%
        # - liquidity: 15%
        # - volatility: 10%
        # - AI_score: 15% (NEW)
        
        # Recalculate with AI component
        breakdown = base_score['breakdown']
        factors = base_score['factors']
        
        # Adjust weights to make room for AI (15%)
        adjusted_total = (
            breakdown.get('prediction_confidence', 0) * 0.25 +  # reduced from 30%
            breakdown.get('technical_strength', 0) * 0.20 +
            breakdown.get('spi_alignment', 0) * 0.15 +
            breakdown.get('liquidity', 0) * 0.15 +
            breakdown.get('volatility', 0) * 0.10 +
            ai_overall * 0.15  # NEW AI component
        )
        
        # Update breakdown with AI component
        breakdown['ai_score'] = ai_overall
        
        # Update factors with AI details
        factors['ai_fundamental'] = ai_data.get('fundamental_score', 50)
        factors['ai_risk'] = ai_data.get('risk_score', 50)
        factors['ai_recommendation'] = ai_data.get('recommendation_score', 50)
        factors['ai_confidence'] = ai_data.get('confidence', 50)
        factors['ai_recommendation_text'] = ai_data.get('recommendation', 'Hold')
        
        # Return updated score
        return {
            'total_score': adjusted_total,
            'breakdown': breakdown,
            'factors': factors
        }
    
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
    
    # ========================================================================
    # INTRADAY MOMENTUM SCORING (Phase 2)
    # ========================================================================
    
    def _score_intraday_momentum(self, stock: Dict, market_status: Dict) -> float:
        """
        Score intraday momentum for stocks during market hours (0-1)
        
        Components:
        1. Price Rate of Change (40%): 15m, 60m, session momentum
        2. Volume Surge (30%): Current vs typical hourly rate
        3. Intraday Volatility (20%): High-low range
        4. Breakout Detection (10%): Support/resistance levels
        
        Args:
            stock: Stock data with intraday_data
            market_status: Market hours status dict
            
        Returns:
            Momentum score (0-1)
        """
        intraday_data = stock.get('intraday_data', {})
        
        if not intraday_data:
            logger.debug(f"No intraday data for {stock.get('symbol', 'UNKNOWN')}")
            return 0.5  # Neutral if no intraday data
        
        scores = {}
        
        # 1. Price Momentum (40% of momentum score)
        mom_15m = intraday_data.get('momentum_15m', 0)
        mom_60m = intraday_data.get('momentum_60m', 0)
        session_change = intraday_data.get('session_change_pct', 0)
        
        # Score based on absolute momentum (direction-agnostic, we want movement)
        # Scale: 1% move = 50 points, 2%+ = 100 points
        score_15m = min(abs(mom_15m) * 50, 100)
        score_60m = min(abs(mom_60m) * 40, 100)
        score_session = min(abs(session_change) * 30, 100)
        
        momentum_score = (
            score_15m * 0.4 +      # Recent acceleration
            score_60m * 0.3 +      # Sustained trend
            score_session * 0.3    # Overall session
        )
        scores['momentum'] = momentum_score
        
        # 2. Volume Surge (30% of momentum score)
        hours_elapsed = market_status.get('trading_hours_elapsed_pct', 50) / 100
        session_duration = 6.0  # ASX trades 6 hours (10 AM - 4 PM)
        hours_elapsed_actual = hours_elapsed * session_duration
        
        if hours_elapsed_actual > 0.5:  # At least 30 minutes elapsed
            current_volume = intraday_data.get('current_volume', 0)
            avg_daily_volume = stock.get('volume', 1_000_000)
            
            # Calculate volume rate
            current_volume_rate = current_volume / hours_elapsed_actual if hours_elapsed_actual > 0 else 0
            typical_hourly_volume = avg_daily_volume / session_duration
            
            surge_ratio = current_volume_rate / typical_hourly_volume if typical_hourly_volume > 0 else 1.0
            
            # Score volume surge
            if surge_ratio > 2.0:
                volume_score = 100
            elif surge_ratio > 1.5:
                volume_score = 80
            elif surge_ratio > 1.2:
                volume_score = 60
            elif surge_ratio > 0.8:
                volume_score = 50
            else:
                volume_score = 30  # Below normal volume
            
            scores['volume_surge'] = volume_score
            scores['surge_ratio'] = surge_ratio
        else:
            volume_score = 50  # Too early to assess
            scores['volume_surge'] = volume_score
            scores['surge_ratio'] = 1.0
        
        # 3. Intraday Volatility (20% of momentum score)
        intraday_range_pct = intraday_data.get('intraday_range_pct', 0)
        
        # Higher range = more trading opportunity
        # Scale: 1% range = 40 points, 2.5%+ = 100 points
        if intraday_range_pct > 2.5:
            volatility_score = 100
        elif intraday_range_pct > 2.0:
            volatility_score = 90
        elif intraday_range_pct > 1.5:
            volatility_score = 75
        elif intraday_range_pct > 1.0:
            volatility_score = 60
        elif intraday_range_pct > 0.5:
            volatility_score = 45
        else:
            volatility_score = 30
        
        scores['volatility'] = volatility_score
        
        # 4. Breakout Detection (10% of momentum score)
        current_price = intraday_data.get('current_price', stock.get('price', 0))
        high_price = intraday_data.get('high_price', current_price)
        low_price = intraday_data.get('low_price', current_price)
        
        technical = stock.get('technical', {})
        ma_20 = technical.get('ma_20', current_price)
        ma_50 = technical.get('ma_50', current_price)
        
        # Check for breakout conditions
        breakout_score = 50  # Default neutral
        
        # Strong breakout above MA50
        if current_price > ma_50 * 1.02:
            breakout_score = 100
        # Breakout above MA20
        elif current_price > ma_20 * 1.02:
            breakout_score = 80
        # Testing highs
        elif current_price > high_price * 0.995:
            breakout_score = 90
        # Testing lows (breakdown)
        elif current_price < low_price * 1.005:
            breakout_score = 85  # Breakdowns can be opportunities too
        # Above MA20 but not breaking out
        elif current_price > ma_20:
            breakout_score = 60
        # Below MA20
        else:
            breakout_score = 40
        
        scores['breakout'] = breakout_score
        
        # Combine all momentum components
        total_momentum = (
            momentum_score * 0.40 +
            volume_score * 0.30 +
            volatility_score * 0.20 +
            breakout_score * 0.10
        )
        
        # Store detailed scores for debugging
        stock['momentum_breakdown'] = scores
        
        # Return normalized score (0-1)
        return total_momentum / 100
    
    def _calculate_intraday_score(
        self,
        stock: Dict,
        market_status: Dict,
        spi_sentiment: Dict = None
    ) -> Dict:
        """
        Calculate opportunity score for intraday mode (0-100)
        
        Intraday Weights:
        1. Intraday Momentum (30%): Real-time price velocity
        2. Technical Strength (25%): Live technical indicators
        3. Liquidity (20%): Critical for rapid execution
        4. Volatility (15%): Opportunity for intraday traders
        5. Prediction Confidence (10%): Less reliable intraday
        6. SPI Alignment (5%): Gap already occurred
        
        Args:
            stock: Stock data with intraday_data
            market_status: Market hours status
            spi_sentiment: Market sentiment (optional, less relevant)
            
        Returns:
            Dictionary with total score and breakdown
        """
        breakdown = {}
        
        # Intraday-specific factors
        momentum_score = self._score_intraday_momentum(stock, market_status)
        technical_score = self._score_technical_strength(stock)
        liquidity_score = self._score_liquidity(stock)
        volatility_score = self._score_volatility_intraday(stock)
        prediction_score = self._score_prediction_confidence(stock)
        spi_score = self._score_spi_alignment(stock, spi_sentiment)
        
        # Intraday weights (different from overnight)
        intraday_weights = {
            'intraday_momentum': 0.30,
            'technical_strength': 0.25,
            'liquidity': 0.20,
            'volatility': 0.15,
            'prediction_confidence': 0.10,
            'spi_alignment': 0.05
        }
        
        # Calculate weighted total
        total = (
            momentum_score * intraday_weights['intraday_momentum'] +
            technical_score * intraday_weights['technical_strength'] +
            liquidity_score * intraday_weights['liquidity'] +
            volatility_score * intraday_weights['volatility'] +
            prediction_score * intraday_weights['prediction_confidence'] +
            spi_score * intraday_weights['spi_alignment']
        ) * 100  # Convert to 0-100 scale
        
        breakdown = {
            'intraday_momentum': momentum_score * 100,
            'technical_strength': technical_score * 100,
            'liquidity': liquidity_score * 100,
            'volatility': volatility_score * 100,
            'prediction_confidence': prediction_score * 100,
            'spi_alignment': spi_score * 100,
            'base_total': total
        }
        
        # Apply adjustments (reduced for intraday)
        adjustments = self._apply_intraday_adjustments(stock, market_status)
        total += adjustments['total_adjustment']
        
        # Ensure score is within bounds
        total = max(0, min(100, total))
        
        return {
            'total_score': total,
            'breakdown': breakdown,
            'factors': {
                'adjustments': adjustments,
                'prediction': stock.get('prediction'),
                'confidence': stock.get('confidence', 0),
                'mode': 'intraday',
                'market_status': market_status.get('market_phase', 'unknown')
            }
        }
    
    def _score_volatility_intraday(self, stock: Dict) -> float:
        """
        Score volatility for intraday trading (0-1)
        
        For intraday: HIGHER volatility = HIGHER score (opportunity)
        Opposite of overnight where lower volatility is preferred
        
        Args:
            stock: Stock data
            
        Returns:
            Volatility score (0-1)
        """
        intraday_data = stock.get('intraday_data', {})
        
        if intraday_data:
            # Use intraday range as primary volatility metric
            intraday_range_pct = intraday_data.get('intraday_range_pct', 0)
            
            # Higher intraday range = better for intraday trading
            if intraday_range_pct > 2.5:
                return 1.0
            elif intraday_range_pct > 2.0:
                return 0.9
            elif intraday_range_pct > 1.5:
                return 0.8
            elif intraday_range_pct > 1.0:
                return 0.6
            else:
                return 0.4
        else:
            # Fallback to historical volatility (inverted preference)
            technical = stock.get('technical', {})
            volatility = technical.get('volatility', 0.05)
            
            # For intraday, prefer higher volatility
            if volatility > 0.06:
                return 0.8  # High volatility = good
            elif volatility > 0.04:
                return 0.6
            else:
                return 0.4  # Low volatility = less opportunity
    
    def _apply_intraday_adjustments(self, stock: Dict, market_status: Dict) -> Dict:
        """
        Apply intraday-specific penalties and bonuses
        
        Different from overnight adjustments:
        - No SPI alignment penalties (gap already occurred)
        - Emphasis on execution risk (liquidity, spread)
        - Momentum confirmation bonuses
        
        Args:
            stock: Stock data
            market_status: Market hours status
            
        Returns:
            Dictionary with adjustment details
        """
        adjustments = {
            'penalties': [],
            'bonuses': [],
            'total_adjustment': 0
        }
        
        # PENALTIES
        
        # Very low volume penalty (execution risk)
        if stock.get('volume', float('inf')) < 500_000:
            penalty = 15  # Higher than overnight (10)
            adjustments['penalties'].append({
                'type': 'low_volume_intraday',
                'amount': -penalty
            })
            adjustments['total_adjustment'] -= penalty
        
        # Early market hours penalty (first 10% of day - volatile/unreliable)
        hours_elapsed_pct = market_status.get('trading_hours_elapsed_pct', 50)
        if hours_elapsed_pct < 10:
            penalty = 5
            adjustments['penalties'].append({
                'type': 'early_market_hours',
                'amount': -penalty
            })
            adjustments['total_adjustment'] -= penalty
        
        # BONUSES
        
        # Strong momentum confirmation bonus
        momentum_breakdown = stock.get('momentum_breakdown', {})
        if momentum_breakdown.get('momentum', 0) > 80:
            bonus = 5
            adjustments['bonuses'].append({
                'type': 'strong_momentum',
                'amount': bonus
            })
            adjustments['total_adjustment'] += bonus
        
        # Volume surge confirmation bonus
        surge_ratio = momentum_breakdown.get('surge_ratio', 1.0)
        if surge_ratio > 1.5:
            bonus = 5
            adjustments['bonuses'].append({
                'type': 'volume_surge',
                'amount': bonus
            })
            adjustments['total_adjustment'] += bonus
        
        # Breakout confirmation bonus
        if momentum_breakdown.get('breakout', 0) >= 90:
            bonus = 8
            adjustments['bonuses'].append({
                'type': 'breakout_confirmed',
                'amount': bonus
            })
            adjustments['total_adjustment'] += bonus
        
        return adjustments
    
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
