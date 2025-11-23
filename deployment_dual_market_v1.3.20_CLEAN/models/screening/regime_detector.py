"""Regime Detector

Uses a simple Hidden Markov / mixture-style model on index returns and volatility
to infer latent market regimes (e.g. calm, normal, high-vol, crisis).

We deliberately design this to:
- degrade gracefully if optional libraries are missing,
- be fast enough for overnight use,
- expose an intuitive regime label + probabilities.

If `hmmlearn` is available, we use a GaussianHMM.
Otherwise we fall back to a Gaussian Mixture Model on recent returns/vol.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Optional imports
try:
    from hmmlearn.hmm import GaussianHMM  # type: ignore
except Exception:  # pragma: no cover - optional dep
    GaussianHMM = None

from sklearn.mixture import GaussianMixture  # lightweight and widely available


@dataclass
class RegimeConfig:
    n_states: int = 3
    min_obs: int = 40  # Reduced from 60 to handle shorter data windows (after 20-day rolling features)
    covariance_type: str = "full"
    random_state: int = 42


class RegimeDetector:
    """Infer latent market regimes from returns and volatility features."""

    def __init__(self, config: Optional[RegimeConfig] = None) -> None:
        self.config = config or RegimeConfig()
        self.model = None
        self._use_hmm = GaussianHMM is not None

    def fit(self, X: pd.DataFrame) -> None:
        """Fit regime model on feature matrix X."""
        if X is None or len(X) < self.config.min_obs:
            logger.warning("RegimeDetector.fit: insufficient observations, skipping fit")
            self.model = None
            return

        Xv = X.values.astype(float)

        if self._use_hmm:
            logger.info("RegimeDetector: fitting GaussianHMM")
            self.model = GaussianHMM(
                n_components=self.config.n_states,
                covariance_type=self.config.covariance_type,
                random_state=self.config.random_state,
                n_iter=200,
            )
            self.model.fit(Xv)
        else:
            logger.info("RegimeDetector: hmmlearn not available; using GaussianMixture fallback")
            self.model = GaussianMixture(
                n_components=self.config.n_states,
                covariance_type=self.config.covariance_type,
                random_state=self.config.random_state,
                n_init=5,
            )
            self.model.fit(Xv)

    def analyse_latest(self, X: pd.DataFrame) -> Dict:
        """Analyse the most recent observation and return regime info."""
        if self.model is None or X is None or X.empty:
            return {
                "regime_label": "unknown",
                "regime_id": -1,
                "probabilities": {},
            }

        Xv = X.values.astype(float)

        if self._use_hmm and isinstance(self.model, GaussianHMM):
            _, post = self.model.score_samples(Xv)
            probs_last = post[-1]
        else:
            probs = self.model.predict_proba(Xv)
            probs_last = probs[-1]

        state_id = int(np.argmax(probs_last))
        prob_map = {int(i): float(p) for i, p in enumerate(probs_last)}

        # Simple heuristic labelling: higher variance state -> "high_vol" etc.
        try:
            state_vols = {}
            for i in range(self.config.n_states):
                mask = self._state_mask(Xv, i)
                if mask.sum() > 0:
                    state_vols[i] = float(np.std(Xv[mask, 0]))  # use first feature as proxy
                else:
                    state_vols[i] = 0.0
            ranked = sorted(state_vols.items(), key=lambda kv: kv[1])
            label_map = {}
            if len(ranked) >= 1:
                label_map[ranked[0][0]] = "calm"
            if len(ranked) >= 2:
                label_map[ranked[1][0]] = "normal"
            if len(ranked) >= 3:
                label_map[ranked[-1][0]] = "high_vol"
            regime_label = label_map.get(state_id, "normal")
        except Exception:
            regime_label = "normal"

        return {
            "regime_label": regime_label,
            "regime_id": state_id,
            "probabilities": prob_map,
        }

    def _state_mask(self, Xv: np.ndarray, state_id: int) -> np.ndarray:
        """Helper for volatility ordering in HMM / mixture space."""
        if self._use_hmm and isinstance(self.model, GaussianHMM):
            states = self.model.predict(Xv)
        else:
            states = self.model.predict(Xv)
        return states == state_id
