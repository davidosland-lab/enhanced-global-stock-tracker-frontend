"""Market Regime Engine

Combines:
- RegimeDetector (HMM / mixture)
- VolatilityForecaster (GARCH / EWMA)

into a single market regime + risk snapshot.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, List

import numpy as np
import pandas as pd
import yfinance as yf

try:
    from .regime_detector import RegimeDetector, RegimeConfig
    from .volatility_forecaster import VolatilityForecaster, VolForecastConfig
except ImportError:
    from regime_detector import RegimeDetector, RegimeConfig
    from volatility_forecaster import VolatilityForecaster, VolForecastConfig

logger = logging.getLogger(__name__)


@dataclass
class MarketRegimeConfig:
    index_symbol: str = "^AXJO"
    vol_symbol: Optional[str] = None  # ASX VIX not available on Yahoo Finance - using calculated volatility instead
    fx_symbol: str = "AUDUSD=X"
    lookback_days: int = 180


class MarketRegimeEngine:
    def __init__(
        self,
        config: Optional[MarketRegimeConfig] = None,
        regime_config: Optional[RegimeConfig] = None,
        vol_config: Optional[VolForecastConfig] = None,
    ) -> None:
        self.config = config or MarketRegimeConfig()
        self.regime_detector = RegimeDetector(regime_config)
        self.vol_forecaster = VolatilityForecaster(vol_config)

    def analyse(self) -> Dict:
        end = datetime.utcnow().date()
        start = end - timedelta(days=self.config.lookback_days)

        # Build symbol list (VIX is optional - may not be available)
        symbols: List[str] = [self.config.index_symbol]
        if self.config.vol_symbol:
            symbols.append(self.config.vol_symbol)
        if self.config.fx_symbol:
            symbols.append(self.config.fx_symbol)
        logger.info(
            f"MarketRegimeEngine: fetching {symbols} from {start.isoformat()} to {end.isoformat()}"
        )

        try:
            data = yf.download(
                tickers=symbols,
                start=start.isoformat(),
                end=end.isoformat(),
                interval="1d",
                auto_adjust=True,
                progress=False,
                group_by="ticker",
            )
        except Exception as e:
            logger.warning(f"MarketRegimeEngine: yfinance download failed: {e}")
            return {
                "regime_label": "unknown",
                "regime_probabilities": {},
                "vol_1d": None,
                "vol_annual": None,
                "vol_method": "none",
                "crash_risk_score": 0.0,
                "data_window": {"start": start.isoformat(), "end": end.isoformat()},
                "error": str(e),
            }

        close = self._extract_close(data, symbols)
        logger.info(f"Extracted close prices: {close.shape[0]} rows, {close.shape[1] if not close.empty else 0} columns")
        if not close.empty:
            logger.info(f"Available symbols in data: {list(close.columns)}")
        
        # Reduced from 30 to 50 to account for 20-day rolling window loss in features
        if close.empty or close.shape[0] < 50:
            logger.warning(f"MarketRegimeEngine: insufficient price history (got {close.shape[0] if not close.empty else 0} rows, need 50+)")
            return {
                "regime_label": "unknown",
                "regime_probabilities": {},
                "vol_1d": None,
                "vol_annual": None,
                "vol_method": "none",
                "crash_risk_score": 0.0,
                "data_window": {"start": start.isoformat(), "end": end.isoformat()},
                "warning": "insufficient_data",
            }

        feats = self._build_features(close)
        
        # Check again after feature engineering (rolling windows reduce row count)
        if feats.empty or feats.shape[0] < 40:
            logger.warning(f"MarketRegimeEngine: insufficient features after processing (got {feats.shape[0]} rows, need 40+)")
            return {
                "regime_label": "unknown",
                "regime_probabilities": {},
                "vol_1d": None,
                "vol_annual": None,
                "vol_method": "none",
                "crash_risk_score": 0.0,
                "data_window": {"start": start.isoformat(), "end": end.isoformat()},
                "warning": "insufficient_features",
            }
        
        self.regime_detector.fit(feats)
        regime_info = self.regime_detector.analyse_latest(feats)

        index_ret = feats["ret_index"]
        vol_info = self.vol_forecaster.forecast_next_day(index_ret)

        crash_risk = self._compute_crash_risk(regime_info, vol_info)

        return {
            "regime_label": regime_info.get("regime_label", "unknown"),
            "regime_probabilities": regime_info.get("probabilities", {}),
            "vol_1d": vol_info.get("vol_1d"),
            "vol_annual": vol_info.get("vol_annual"),
            "vol_method": vol_info.get("method"),
            "crash_risk_score": crash_risk,
            "data_window": {"start": start.isoformat(), "end": end.isoformat()},
        }

    @staticmethod
    def _extract_close(data: pd.DataFrame, symbols: List[str]) -> pd.DataFrame:
        if data is None or data.empty:
            logger.warning("_extract_close: data is None or empty")
            return pd.DataFrame()
        
        logger.info(f"_extract_close: data shape={data.shape}, columns type={type(data.columns)}")
        logger.info(f"_extract_close: columns={list(data.columns)[:10]}")  # First 10 to avoid spam
        
        if isinstance(data.columns, pd.MultiIndex):
            logger.info(f"_extract_close: MultiIndex detected, levels={data.columns.nlevels}")
            logger.info(f"_extract_close: Level 0 values={list(data.columns.get_level_values(0).unique())}")
            logger.info(f"_extract_close: Level 1 values={list(data.columns.get_level_values(1).unique())}")
            
            # For yfinance multi-ticker downloads, structure is (Ticker, Price_Type)
            # We need to get the 'Close' or 'Adj Close' price type for each ticker
            price_types = data.columns.get_level_values(1).unique()
            
            if "Adj Close" in price_types:
                # Get all tickers' Adj Close prices
                close = data.xs('Adj Close', level=1, axis=1).copy()
                logger.info("_extract_close: Using 'Adj Close' from MultiIndex level 1")
            elif "Close" in price_types:
                # Get all tickers' Close prices
                close = data.xs('Close', level=1, axis=1).copy()
                logger.info("_extract_close: Using 'Close' from MultiIndex level 1")
            else:
                logger.warning(f"_extract_close: No 'Close' or 'Adj Close' in MultiIndex level 1. Available: {list(price_types)}")
                return pd.DataFrame()
        else:
            # Single column dataframe or regular columns
            cols = list(data.columns)
            logger.info(f"_extract_close: Regular columns={cols}")
            
            if "Adj Close" in cols:
                close = data[["Adj Close"]].copy()
                logger.info("_extract_close: Using 'Adj Close' column")
            elif "Close" in cols:
                close = data[["Close"]].copy()
                logger.info("_extract_close: Using 'Close' column")
            else:
                logger.warning(f"_extract_close: No 'Close' or 'Adj Close' in columns")
                return pd.DataFrame()
            
            if len(symbols) == 1:
                close.columns = [symbols[0]]
                logger.info(f"_extract_close: Single symbol, renamed column to {symbols[0]}")
        
        logger.info(f"_extract_close: close.shape after extraction={close.shape}, columns={list(close.columns)}")
        
        available = [s for s in symbols if s in close.columns]
        logger.info(f"_extract_close: symbols requested={symbols}, available={available}")
        
        result = close[available] if available else pd.DataFrame()
        logger.info(f"_extract_close: returning shape={result.shape}")
        return result

    def _build_features(self, close: pd.DataFrame) -> pd.DataFrame:
        df = close.copy().sort_index()
        idx = self.config.index_symbol
        vix = self.config.vol_symbol
        fx = self.config.fx_symbol

        feats = pd.DataFrame(index=df.index)
        feats["ret_index"] = df[idx].pct_change()
        feats["ret_fx"] = df[fx].pct_change() if fx and fx in df.columns else 0.0
        
        # VIX features (optional - ASX VIX ^XVI not available on Yahoo Finance)
        # Falls back to calculated realized volatility from index returns
        if vix and vix in df.columns:
            feats["vix_level"] = df[vix]
            feats["vix_change"] = df[vix].pct_change()
            logger.info(f"Using external VIX data: {vix}")
        else:
            # Use calculated volatility from index as proxy
            feats["vix_level"] = feats["ret_index"].rolling(window=20).std() * np.sqrt(252) * 100  # Annualized vol as VIX proxy
            feats["vix_change"] = feats["vix_level"].pct_change()
            logger.info("Using calculated volatility from ASX 200 returns (VIX data unavailable)")
        
        feats["realized_vol_10d"] = feats["ret_index"].rolling(window=10).std()
        
        logger.info(f"Features before dropna: {feats.shape[0]} rows")
        feats = feats.dropna()
        logger.info(f"Features after dropna: {feats.shape[0]} rows (need 30+ for regime detection)")
        
        return feats

    def _compute_crash_risk(self, regime_info: Dict, vol_info: Dict) -> float:
        regime_label = regime_info.get("regime_label", "normal")
        vol_1d = vol_info.get("vol_1d") or 0.0
        vol_scale = min(3.0, vol_1d / 0.01) if vol_1d else 0.0
        if regime_label == "high_vol":
            base = 0.4
        elif regime_label == "normal":
            base = 0.2
        else:
            base = 0.1
        crash_risk = base + 0.3 * vol_scale
        crash_risk = max(0.0, min(1.0, crash_risk))
        return float(crash_risk)
