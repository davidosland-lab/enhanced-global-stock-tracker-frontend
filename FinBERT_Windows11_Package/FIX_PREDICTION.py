#!/usr/bin/env python3
"""
Quick fix script - patches the prediction to use enough historical data
Run this to update your existing app files
"""

print("""
========================================
PREDICTION FIX EXPLANATION
========================================

The SMA_50 error during PREDICTION happens because:

1. TRAINING uses 6 months of data (has SMA_50) ✓
2. PREDICTION only fetches 1 month of data (no SMA_50) ✗

THE FIX:
Change prediction to fetch AT LEAST as much data as the longest SMA period.

In your app file, find the predict() method and change:

OLD CODE (causing the error):
----------------------------
def predict(self, symbol: str) -> dict:
    # Get recent data
    df = self.fetcher.get_stock_data(symbol, "1mo")  # ← PROBLEM: Only 1 month!

NEW CODE (fixed):
----------------
def predict(self, symbol: str) -> dict:
    # Get enough data for all features (at least 3 months for SMA_50)
    df = self.fetcher.get_stock_data(symbol, "3mo")  # ← FIXED: 3 months ensures SMA_50
    if df.empty or len(df) < 50:
        df = self.fetcher.get_stock_data(symbol, "6mo")  # ← FALLBACK: Try 6 months

========================================

To apply this fix:

1. Open your app_real_data_only.py (or whichever version you're using)
2. Find the predict() method (search for "def predict")
3. Change the period from "1mo" to "3mo" or "6mo"
4. Save and restart

Or use the fully fixed version: app_real_data_fixed_sma.py
which already has this fix applied.
""")