"""Meta Boost Model

Meta-model that combines:
- base LSTM predictions,
- technical features,
- sentiment,
- macro features (betas, OGSI, etc.)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List

import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger(__name__)

try:
    import xgboost as xgb  # type: ignore
except Exception:  # pragma: no cover
    xgb = None

from sklearn.ensemble import GradientBoostingClassifier


@dataclass
class MetaModelConfig:
    model_path: Path
    feature_columns: List[str]


class MetaBoostModel:
    """Wrapper around XGBoost / GradientBoosting that exposes a unified interface."""

    def __init__(self, config: MetaModelConfig) -> None:
        self.config = config
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        if not self.config.model_path.exists():
            logger.warning(f"MetaBoostModel: model file not found at {self.config.model_path}")
            self.model = None
            return
        try:
            self.model = joblib.load(self.config.model_path)
            logger.info(f"MetaBoostModel: loaded model from {self.config.model_path}")
        except Exception as e:
            logger.error(f"MetaBoostModel: failed to load model: {e}")
            self.model = None

    def is_ready(self) -> bool:
        return self.model is not None

    def build_feature_matrix(self, stocks: List[Dict]) -> pd.DataFrame:
        rows = []
        for s in stocks:
            row = {}
            for col in self.config.feature_columns:
                row[col] = s.get(col)
            rows.append(row)
        return pd.DataFrame(rows)

    def predict_proba(self, X: pd.DataFrame):
        if self.model is None:
            logger.warning("MetaBoostModel.predict_proba called but model is not loaded")
            return None
        X = X[self.config.feature_columns]
        return self.model.predict_proba(X.values)
