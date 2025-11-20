"""Factor View Builder

Constructs a factor-level view of scored opportunities, including:
- Per-stock factor contributions
- Macro betas (XJO, lithium) if available
- Sector-level summaries
- CSV + JSON exports for dashboards / notebooks
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
import pytz

logger = logging.getLogger(__name__)

try:
    BASE_PATH = Path(__file__).parent.parent.parent
except Exception:
    BASE_PATH = Path(".")


class FactorViewBuilder:
    """Builds and persists a factor view for scored stocks."""

    def __init__(self, timezone: Optional[Any] = None) -> None:
        self.timezone = timezone or pytz.timezone("Australia/Sydney")
        self.output_dir = BASE_PATH / "reports" / "factor_view"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_factor_view(self, scored_stocks: List[Dict]) -> Dict[str, Any]:
        """Build an in-memory factor view structure."""
        rows: List[Dict[str, Any]] = []

        for stock in scored_stocks or []:
            breakdown = stock.get("score_breakdown", {}) or {}
            factors = stock.get("score_factors", {}) or {}
            adjustments = factors.get("adjustments", {}) or {}
            macro_betas = stock.get("macro_betas", {}) or {}

            row = {
                "symbol": stock.get("symbol"),
                "name": stock.get("name", stock.get("symbol")),
                "sector": stock.get("sector", "Unknown"),
                "price": stock.get("price"),
                "opportunity_score": float(stock.get("opportunity_score", 0.0)),
                "prediction_confidence": float(breakdown.get("prediction_confidence", 0.0)),
                "technical_strength": float(breakdown.get("technical_strength", 0.0)),
                "spi_alignment": float(breakdown.get("spi_alignment", 0.0)),
                "liquidity": float(breakdown.get("liquidity", 0.0)),
                "volatility": float(breakdown.get("volatility", 0.0)),
                "sector_momentum": float(breakdown.get("sector_momentum", 0.0)),
                "base_total": float(breakdown.get("base_total", stock.get("opportunity_score", 0.0))),
                "total_adjustment": float(adjustments.get("total_adjustment", 0.0)),
                "penalty_count": len(adjustments.get("penalties", [])),
                "bonus_count": len(adjustments.get("bonuses", [])),
                "beta_xjo": float(stock.get("beta_xjo") or macro_betas.get("xjo") or 0.0),
                "beta_lithium": float(stock.get("beta_lithium") or macro_betas.get("lithium") or 0.0),
                "prediction": factors.get("prediction", stock.get("prediction")),
                "confidence_pct": float(factors.get("confidence", stock.get("confidence", 0.0))),
            }
            rows.append(row)

        summary: Dict[str, Any] = {}
        if rows:
            df = pd.DataFrame(rows)

            if "sector" in df.columns and "opportunity_score" in df.columns:
                by_sector = df.groupby("sector", dropna=False)
                sector_avg = by_sector["opportunity_score"].mean().sort_values(ascending=False)
                summary["sector_avg_opportunity"] = sector_avg.to_dict()

                for col in ["beta_xjo", "beta_lithium"]:
                    if col in df.columns:
                        summary[f"{col}_by_sector"] = by_sector[col].mean().to_dict()

            summary["overall"] = {
                "count": int(len(rows)),
                "avg_opportunity_score": float(np.mean([r["opportunity_score"] for r in rows])),
                "avg_beta_xjo": float(np.mean([r["beta_xjo"] for r in rows])),
                "avg_beta_lithium": float(np.mean([r["beta_lithium"] for r in rows])),
            }

        return {
            "stocks": rows,
            "summary": summary,
        }

    def save_factor_view(self, factor_view: Dict[str, Any], date_override: Optional[str] = None) -> Dict[str, str]:
        """Persist factor view to CSV/JSON files."""
        date_str = date_override or datetime.now(self.timezone).strftime("%Y-%m-%d")

        stocks_csv = self.output_dir / f"{date_str}_factor_view_stocks.csv"
        sector_csv = self.output_dir / f"{date_str}_factor_view_sector_summary.csv"
        summary_json = self.output_dir / f"{date_str}_factor_view_summary.json"

        rows = factor_view.get("stocks", []) or []
        summary = factor_view.get("summary", {}) or {}

        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(stocks_csv, index=False)
            logger.info(f"Factor view stocks CSV written: {stocks_csv}")
        else:
            logger.info("Factor view: no rows to write")

        sector_rows: List[Dict[str, Any]] = []
        sector_avg = summary.get("sector_avg_opportunity", {})
        beta_xjo_sector = summary.get("beta_xjo_by_sector", {})
        beta_lithium_sector = summary.get("beta_lithium_by_sector", {})

        for sector, avg_score in sector_avg.items():
            sector_rows.append({
                "sector": sector,
                "avg_opportunity_score": float(avg_score),
                "avg_beta_xjo": float(beta_xjo_sector.get(sector, 0.0)),
                "avg_beta_lithium": float(beta_lithium_sector.get(sector, 0.0)),
            })

        if sector_rows:
            df_sector = pd.DataFrame(sector_rows)
            df_sector.to_csv(sector_csv, index=False)
            logger.info(f"Factor view sector summary CSV written: {sector_csv}")

        with summary_json.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f"Factor view summary JSON written: {summary_json}")

        return {
            "stocks_csv": str(stocks_csv),
            "sector_summary_csv": str(sector_csv),
            "summary_json": str(summary_json),
        }
