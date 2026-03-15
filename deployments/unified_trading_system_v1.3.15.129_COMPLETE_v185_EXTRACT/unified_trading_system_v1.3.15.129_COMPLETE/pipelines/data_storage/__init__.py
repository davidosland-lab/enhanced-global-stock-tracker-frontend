"""
Advanced Data Storage Module

High-performance Parquet-based storage with DuckDB analytics
Inspired by Jon Becker's prediction market analysis framework
"""

from .parquet_store import ParquetTradeStore, ParquetMarketStore
from .duckdb_analytics import DuckDBAnalyticsEngine
from .pipeline_integration import (
    PipelineStorageManager,
    PipelineDataLogger,
    integrate_with_us_pipeline
)

# Legacy imports (if they exist)
try:
    from .maker_taker_classifier import MakerTakerClassifier
    from .cost_basis_normalizer import CostBasisNormalizer
    _legacy_available = True
except ImportError:
    _legacy_available = False
    MakerTakerClassifier = None
    CostBasisNormalizer = None

__all__ = [
    'ParquetTradeStore',
    'ParquetMarketStore',
    'DuckDBAnalyticsEngine',
    'PipelineStorageManager',
    'PipelineDataLogger',
    'integrate_with_us_pipeline',
]

if _legacy_available:
    __all__.extend(['MakerTakerClassifier', 'CostBasisNormalizer'])
