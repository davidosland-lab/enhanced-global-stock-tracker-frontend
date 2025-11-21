"""
US Market Regime Engine

HMM-based market regime classifier for US markets (S&P 500)
Detects market states and crash risk probability

Based on the ASX Market Regime Engine but adapted for US market (^GSPC)
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from yahooquery import Ticker

# Try to import hmmlearn (optional dependency)
try:
    from hmmlearn import hmm
    HMM_AVAILABLE = True
except ImportError:
    HMM_AVAILABLE = False
    logging.warning("hmmlearn not installed - Market Regime Engine will use fallback mode")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class USMarketRegimeEngine:
    """
    US Market Regime Classifier using Hidden Markov Model
    
    Analyzes S&P 500 (^GSPC) to determine current market regime:
    - State 0: Low Volatility (Bull Market)
    - State 1: Medium Volatility (Normal Market)
    - State 2: High Volatility (Bear/Crash Market)
    
    Provides crash risk score (0-1) based on regime probabilities
    """
    
    def __init__(self, n_states: int = 3, lookback_days: int = 252):
        """
        Initialize US Market Regime Engine
        
        Args:
            n_states: Number of hidden states (default: 3)
            lookback_days: Days of historical data to use (default: 252 = 1 year)
        """
        self.n_states = n_states
        self.lookback_days = lookback_days
        self.index_symbol = "^GSPC"  # S&P 500
        self.model = None
        self.fitted = False
        
        if not HMM_AVAILABLE:
            logger.warning("HMM not available - using fallback regime detection")
        
        logger.info(f"US Market Regime Engine initialized (HMM: {HMM_AVAILABLE})")
    
    def fetch_sp500_data(self) -> Optional[pd.DataFrame]:
        """
        Fetch S&P 500 historical data
        
        Returns:
            DataFrame with S&P 500 price data or None on error
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.lookback_days + 30)  # Extra buffer
            
            # Fetch data
            ticker = Ticker(self.index_symbol)
            hist = ticker.history(start=start_date.strftime('%Y-%m-%d'),
                                 end=end_date.strftime('%Y-%m-%d'))
            
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                # Handle MultiIndex (symbol, date) from yahooquery
                if isinstance(hist.index, pd.MultiIndex):
                    # Reset index and set date as index
                    hist = hist.reset_index()
                    hist = hist.set_index('date')
                
                # Standardize column names
                hist.columns = [col.capitalize() for col in hist.columns]
                logger.info(f"Fetched {len(hist)} days of S&P 500 data")
                return hist
            else:
                logger.error("No S&P 500 data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching S&P 500 data: {e}")
            return None
    
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for HMM: daily returns and volatility
        
        Args:
            data: DataFrame with S&P 500 price data
            
        Returns:
            2D array of features [returns, volatility]
        """
        # Calculate daily returns
        returns = data['Close'].pct_change().dropna()
        
        # Calculate rolling volatility (10-day window)
        volatility = returns.rolling(window=10).std().dropna()
        
        # Combine features (align indices)
        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility
        }).dropna()
        
        return features.values
    
    def fit_model(self, features: np.ndarray) -> bool:
        """
        Fit HMM model to features
        
        Args:
            features: 2D array of market features
            
        Returns:
            True if successful, False otherwise
        """
        if not HMM_AVAILABLE:
            return False
        
        try:
            # Initialize Gaussian HMM
            self.model = hmm.GaussianHMM(
                n_components=self.n_states,
                covariance_type="full",
                n_iter=100,
                random_state=42
            )
            
            # Fit model
            self.model.fit(features)
            self.fitted = True
            
            logger.info(f"✓ HMM model fitted with {self.n_states} states")
            return True
            
        except Exception as e:
            logger.error(f"Error fitting HMM model: {e}")
            return False
    
    def predict_regime(self, features: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Predict current market regime
        
        Args:
            features: 2D array of recent market features
            
        Returns:
            Tuple of (predicted_state, state_probabilities)
        """
        if not self.fitted or self.model is None:
            # Fallback: return neutral state
            return 1, np.array([0.33, 0.34, 0.33])
        
        try:
            # Predict state probabilities
            probs = self.model.predict_proba(features)
            
            # Current state (last row)
            current_probs = probs[-1]
            current_state = np.argmax(current_probs)
            
            return int(current_state), current_probs
            
        except Exception as e:
            logger.error(f"Error predicting regime: {e}")
            return 1, np.array([0.33, 0.34, 0.33])
    
    def calculate_crash_risk(self, state_probs: np.ndarray, current_volatility: float) -> float:
        """
        Calculate crash risk score (0-1) based on regime probabilities
        
        Args:
            state_probs: Array of state probabilities [low_vol, med_vol, high_vol]
            current_volatility: Current market volatility
            
        Returns:
            Crash risk score between 0 (safe) and 1 (high risk)
        """
        # Base risk from high volatility state probability
        base_risk = state_probs[2] if len(state_probs) == 3 else 0.3
        
        # Adjust for current volatility
        # Normal market volatility ~0.10-0.20, crash volatility >0.30
        if current_volatility > 0.30:
            volatility_factor = min((current_volatility - 0.30) / 0.20, 1.0)
        else:
            volatility_factor = 0.0
        
        # Combined risk (weighted)
        crash_risk = (base_risk * 0.7) + (volatility_factor * 0.3)
        
        return float(min(crash_risk, 1.0))
    
    def get_regime_label(self, state: int) -> str:
        """Get human-readable label for regime state"""
        labels = {
            0: "low_vol",
            1: "medium_vol",
            2: "high_vol"
        }
        return labels.get(state, "unknown")
    
    def analyse(self) -> Dict:
        """
        Perform complete market regime analysis
        
        Returns:
            Dictionary with regime analysis results
        """
        try:
            # Fetch S&P 500 data
            data = self.fetch_sp500_data()
            
            if data is None or len(data) < 50:
                return self._get_fallback_analysis()
            
            # Prepare features
            features = self.prepare_features(data)
            
            if len(features) < 20:
                return self._get_fallback_analysis()
            
            # Fit model if using HMM
            if HMM_AVAILABLE and not self.fitted:
                self.fit_model(features)
            
            # Predict regime
            if self.fitted:
                state, state_probs = self.predict_regime(features)
            else:
                # Fallback regime detection
                state, state_probs = self._fallback_regime_detection(data)
            
            # Calculate current volatility
            returns = data['Close'].pct_change().dropna()
            current_volatility = returns.iloc[-10:].std() * np.sqrt(252)  # Annualized
            one_day_volatility = returns.iloc[-1]
            
            # Calculate crash risk
            crash_risk = self.calculate_crash_risk(state_probs, current_volatility)
            
            # Get regime label
            regime_label = self.get_regime_label(state)
            
            # Extract dates safely (handle MultiIndex from yahooquery)
            try:
                if isinstance(data.index[0], tuple):
                    # MultiIndex - extract date from first element
                    start_date = pd.Timestamp(data.index[0][0]).strftime('%Y-%m-%d')
                    end_date = pd.Timestamp(data.index[-1][0]).strftime('%Y-%m-%d')
                else:
                    # Regular DatetimeIndex
                    start_date = data.index[0].strftime('%Y-%m-%d')
                    end_date = data.index[-1].strftime('%Y-%m-%d')
            except Exception as e:
                logger.warning(f"Could not extract dates from index: {e}")
                start_date = 'N/A'
                end_date = 'N/A'
            
            result = {
                'regime_state': int(state),
                'regime_label': regime_label,
                'crash_risk_score': float(crash_risk),
                'state_probabilities': {
                    'low_vol': float(state_probs[0]),
                    'medium_vol': float(state_probs[1]),
                    'high_vol': float(state_probs[2])
                },
                'vol_1d': float(abs(one_day_volatility)),
                'vol_annual': float(current_volatility),
                'data_window': {
                    'days': len(data),
                    'start_date': start_date,
                    'end_date': end_date
                },
                'index': 'S&P 500',
                'index_symbol': self.index_symbol,
                'timestamp': datetime.now().isoformat(),
                'method': 'HMM' if self.fitted else 'Fallback'
            }
            
            logger.info(f"✓ Regime: {regime_label} | Crash Risk: {crash_risk:.1%}")
            return result
            
        except Exception as e:
            logger.error(f"Error in regime analysis: {e}")
            return self._get_fallback_analysis()
    
    def _fallback_regime_detection(self, data: pd.DataFrame) -> Tuple[int, np.ndarray]:
        """
        Fallback regime detection without HMM
        Uses simple volatility thresholds
        
        Args:
            data: S&P 500 price data
            
        Returns:
            Tuple of (state, probabilities)
        """
        try:
            # Calculate recent volatility
            returns = data['Close'].pct_change().dropna()
            recent_vol = returns.iloc[-20:].std() * np.sqrt(252)  # Last 20 days, annualized
            
            # Determine state based on volatility thresholds
            if recent_vol < 0.15:
                state = 0  # Low volatility
                probs = np.array([0.70, 0.25, 0.05])
            elif recent_vol < 0.25:
                state = 1  # Medium volatility
                probs = np.array([0.25, 0.60, 0.15])
            else:
                state = 2  # High volatility
                probs = np.array([0.05, 0.25, 0.70])
            
            return state, probs
            
        except Exception as e:
            logger.error(f"Fallback detection error: {e}")
            return 1, np.array([0.33, 0.34, 0.33])
    
    def _get_fallback_analysis(self) -> Dict:
        """Return default analysis when data unavailable"""
        return {
            'regime_state': 1,
            'regime_label': 'medium_vol',
            'crash_risk_score': 0.20,
            'state_probabilities': {
                'low_vol': 0.33,
                'medium_vol': 0.34,
                'high_vol': 0.33
            },
            'vol_1d': 0.01,
            'vol_annual': 0.18,
            'data_window': {
                'days': 0,
                'start_date': 'N/A',
                'end_date': 'N/A'
            },
            'index': 'S&P 500',
            'index_symbol': self.index_symbol,
            'timestamp': datetime.now().isoformat(),
            'method': 'Default',
            'error': 'Insufficient data'
        }


if __name__ == "__main__":
    # Test US Market Regime Engine
    print("\n" + "="*80)
    print("US MARKET REGIME ENGINE TEST")
    print("="*80)
    
    engine = USMarketRegimeEngine()
    
    print("\nAnalyzing S&P 500 market regime...")
    result = engine.analyse()
    
    print(f"\n✓ Analysis Complete:")
    print(f"   Regime: {result['regime_label'].upper()}")
    print(f"   Crash Risk: {result['crash_risk_score']:.1%}")
    print(f"   Method: {result['method']}")
    print(f"   Annual Volatility: {result['vol_annual']:.2%}")
    print(f"\n   State Probabilities:")
    print(f"     Low Vol:    {result['state_probabilities']['low_vol']:.1%}")
    print(f"     Medium Vol: {result['state_probabilities']['medium_vol']:.1%}")
    print(f"     High Vol:   {result['state_probabilities']['high_vol']:.1%}")
    print(f"\n   Data Window: {result['data_window']['days']} days")
    print(f"   Period: {result['data_window']['start_date']} to {result['data_window']['end_date']}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
