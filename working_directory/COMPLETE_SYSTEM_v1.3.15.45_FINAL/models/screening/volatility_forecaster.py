"""Volatility Forecaster

Forecasts short-horizon volatility for an index using either:
- GARCH(1,1) (if `arch` library is available), or
- a simple EWMA fallback if not.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from arch import arch_model  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    arch_model = None


@dataclass
class VolForecastConfig:
    min_obs: int = 100
    ewma_lambda: float = 0.94


class VolatilityForecaster:
    """Wrapper for GARCH(1,1) or EWMA volatility forecasting."""

    def __init__(self, config: Optional[VolForecastConfig] = None) -> None:
        self.config = config or VolForecastConfig()

    def forecast_next_day(self, returns: pd.Series) -> Dict:
        """Forecast next-day volatility (annualized and daily)."""
        if returns is None or returns.dropna().shape[0] < self.config.min_obs:
            logger.warning("VolatilityForecaster: insufficient returns, using simple std")
            r = returns.dropna()
            if r.empty:
                return {"vol_1d": None, "vol_annual": None, "method": "none"}
            daily = float(r.std())
            annual = float(daily * np.sqrt(252))
            return {"vol_1d": daily, "vol_annual": annual, "method": "simple"}

        r = returns.dropna().astype(float)

        if arch_model is not None:
            try:
                am = arch_model(r * 100.0, p=1, q=1, mean="constant", vol="GARCH", dist="normal")
                res = am.fit(disp="off")
                fcast = res.forecast(horizon=1)
                var_1d = fcast.variance.values[-1, 0] / (100.0 ** 2)
                vol_1d = float(np.sqrt(var_1d))
                vol_annual = float(vol_1d * np.sqrt(252))
                return {
                    "vol_1d": vol_1d,
                    "vol_annual": vol_annual,
                    "method": "garch",
                }
            except Exception as e:
                logger.warning(f"VolatilityForecaster: GARCH fit failed, falling back to EWMA: {e}")

        lam = self.config.ewma_lambda
        weights = np.array([lam ** i for i in range(len(r))][::-1])
        weights /= weights.sum()
        mean = float((weights * r.values).sum())
        var = float((weights * (r.values - mean) ** 2).sum())
        vol_1d = float(np.sqrt(var))
        vol_annual = float(vol_1d * np.sqrt(252))
        return {
            "vol_1d": vol_1d,
            "vol_annual": vol_annual,
            "method": "ewma",
        }
