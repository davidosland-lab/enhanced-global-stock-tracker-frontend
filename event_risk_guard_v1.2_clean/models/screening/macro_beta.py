"""Macro Beta Calculator

Computes simple OLS betas of each stock vs a set of macro factors
(e.g. ASX 200 index, lithium ETF) using daily returns.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class FactorDefinition:
    """Defines a single macro factor."""
    name: str    # internal key, e.g. "xjo"
    symbol: str  # ticker, e.g. "^AXJO"


class MacroBetaCalculator:
    """
    Computes stock betas vs a small set of macro factors.
    """

    def __init__(
        self,
        lookback_days: int = 90,
        min_obs: int = 40,
        factors: Optional[List[FactorDefinition]] = None,
    ) -> None:
        self.lookback_days = lookback_days
        self.min_obs = min_obs

        # Default factors: ASX 200 index and a lithium proxy
        self.factors: List[FactorDefinition] = factors or [
            FactorDefinition(name="xjo", symbol="^AXJO"),      # ASX 200
            FactorDefinition(name="lithium", symbol="LIT.AX"), # Lithium ETF proxy
        ]

    def compute_betas(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Compute betas for the given symbols vs configured macro factors.
        """
        symbols = [s for s in (symbols or []) if s]
        if not symbols or not self.factors:
            return {}

        factor_symbols = [f.symbol for f in self.factors]
        all_symbols = sorted(set(symbols + factor_symbols))

        end = datetime.utcnow().date()
        start = end - timedelta(days=self.lookback_days)

        logger.info(
            f"MacroBetaCalculator: fetching {len(all_symbols)} symbols "
            f"from {start.isoformat()} to {end.isoformat()}"
        )

        try:
            price_data = yf.download(
                tickers=all_symbols,
                start=start.isoformat(),
                end=end.isoformat(),
                interval="1d",
                auto_adjust=True,
                progress=False,
                group_by="ticker",
            )
        except Exception as e:
            logger.warning(f"MacroBetaCalculator: yfinance download failed: {e}")
            return {}

        close_df = self._extract_close_matrix(price_data, all_symbols)
        if close_df.empty:
            logger.warning("MacroBetaCalculator: no close price data available")
            return {}

        returns = close_df.pct_change().dropna(how="all")
        if returns.empty:
            logger.warning("MacroBetaCalculator: insufficient return data")
            return {}

        factor_returns: Dict[str, pd.Series] = {}
        for f in self.factors:
            if f.symbol not in returns.columns:
                logger.warning(f"MacroBetaCalculator: factor {f.name} ({f.symbol}) missing in data")
                continue
            factor_returns[f.name] = returns[f.symbol].dropna()

        betas: Dict[str, Dict[str, float]] = {}
        for sym in symbols:
            if sym not in returns.columns:
                continue
            sym_ret = returns[sym].dropna()
            if sym_ret.size < self.min_obs:
                continue

            betas[sym] = {}
            for f in self.factors:
                if f.name not in factor_returns:
                    continue
                fac_ret = factor_returns[f.name]

                joined = pd.concat([sym_ret, fac_ret], axis=1, join="inner").dropna()
                if joined.shape[0] < self.min_obs:
                    continue

                r_s = joined.iloc[:, 0].values
                r_f = joined.iloc[:, 1].values

                var_f = float(np.var(r_f))
                if var_f <= 0:
                    continue

                cov_sf = float(np.cov(r_s, r_f)[0, 1])
                beta = cov_sf / var_f
                betas[sym][f.name] = float(beta)

        return betas

    @staticmethod
    def _extract_close_matrix(data: pd.DataFrame, symbols: List[str]) -> pd.DataFrame:
        """
        Normalize yfinance download output into a simple Close price matrix.
        """
        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            # When group_by='ticker', structure is: (ticker, field)
            # Level 0 = tickers, Level 1 = fields (Open, High, Low, Close, Volume)
            level1_values = data.columns.get_level_values(1).unique().tolist()
            
            if "Adj Close" in level1_values:
                # Extract Adj Close using xs (cross-section)
                close = data.xs('Adj Close', axis=1, level=1).copy()
            elif "Close" in level1_values:
                # Extract Close using xs (cross-section)
                close = data.xs('Close', axis=1, level=1).copy()
            else:
                return pd.DataFrame()
        else:
            # Single ticker case - not MultiIndex
            cols = list(data.columns)
            if "Adj Close" in cols:
                close = data[["Adj Close"]].copy()
            elif "Close" in cols:
                close = data[["Close"]].copy()
            else:
                return pd.DataFrame()

            if len(symbols) == 1:
                close.columns = [symbols[0]]

        available = [s for s in symbols if s in close.columns]
        return close[available] if available else pd.DataFrame()
