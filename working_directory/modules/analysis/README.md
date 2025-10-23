# Analysis Modules

## Overview
This folder contains analytical tools for detailed stock and market analysis.

## Modules

### CBA Analysis
- **cba_analysis.html** - Comprehensive analysis dashboard for Commonwealth Bank (CBA.AX)

## Features
- Technical indicators (moving averages, RSI, MACD)
- Volume analysis with trends
- Price action patterns
- Support and resistance levels
- Historical performance metrics
- Correlation with market indices

## Data Sources
- Real-time data from Yahoo Finance via backend API
- Historical data for trend analysis
- Market context from global indices

## API Dependencies
- `/api/historical/CBA.AX` - Historical CBA data
- `/api/quote/CBA.AX` - Real-time CBA quotes

## Integration Points
- Receives market context from Global Indices Tracker
- Provides analysis data to ML Predictions module
- Can be accessed from Document Center

## Future Enhancements
- Add more ASX stocks (BHP.AX, WBC.AX, ANZ.AX)
- Sector comparison tools
- Fundamental analysis integration
- News sentiment analysis