# System Architecture

## Overview
The ASX Market Dashboard follows a client-server architecture with real-time data fetching from Yahoo Finance.

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Frontend Modules                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │Market Periods│  │Global Indices│  │Single Stock│  │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │CBA Analysis  │  │ML Predictions│  │Doc Center │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                             │                                │
│                    JavaScript Fetch API                      │
│                             │                                │
└─────────────────────────────┼────────────────────────────────┘
                              │ HTTP/REST
                              │ Port 8002
┌─────────────────────────────┼────────────────────────────────┐
│                      FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Endpoints                      │   │
│  │  /api/quote/{symbol}                                 │   │
│  │  /api/historical/{symbol}                            │   │
│  │  /api/batch                                          │   │
│  │  /api/market-status                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                             │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Business Logic Layer                 │   │
│  │  - Data validation                                   │   │
│  │  - Percentage calculations                           │   │
│  │  - Error handling                                    │   │
│  │  - Response formatting                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                             │                                 │
└─────────────────────────────┼─────────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │  Yahoo Finance    │
                    │    yfinance API   │
                    └───────────────────┘
```

## Component Layers

### 1. Presentation Layer (Frontend)
- **Technology**: HTML5, JavaScript, CSS
- **Visualization**: Chart.js with annotation plugin
- **Update Frequency**: 30-second intervals for real-time data
- **Time Zone**: Australian Eastern Time (AEST)

### 2. API Layer (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Port**: 8002 (hardcoded for Windows compatibility)
- **CORS**: Enabled for localhost access
- **Response Format**: JSON with nested structure

### 3. Business Logic Layer
- **Data Processing**: Real-time and historical data handling
- **Calculations**: Percentage change using previous close
- **Validation**: Symbol validation and error handling
- **Caching**: 5-minute cache for efficiency

### 4. Data Access Layer
- **Library**: yfinance (Yahoo Finance Python API)
- **Data Types**: Real-time quotes, historical data
- **Symbols**: ASX stocks (e.g., CBA.AX), global indices
- **Rate Limiting**: Built-in yfinance rate limiting

## Data Flow

### Real-time Data Request
1. Frontend timer triggers data fetch (every 30s)
2. JavaScript sends request to `/api/quote/{symbol}`
3. Backend validates symbol
4. yfinance fetches latest data from Yahoo Finance
5. Backend calculates percentage change
6. Response sent in nested JSON format
7. Frontend updates Chart.js visualization

### Historical Data Request
1. User selects time period (Today/Yesterday/7 Days)
2. Frontend requests `/api/historical/{symbol}?period=X`
3. Backend fetches historical data via yfinance
4. Data processed and formatted
5. Response includes `{data: [...], symbol, period}`
6. Frontend renders historical chart

## Security Considerations
- CORS restricted to localhost origins
- Input validation on all API endpoints
- No database passwords (uses public Yahoo Finance API)
- Rate limiting through yfinance library
- Error messages sanitized for production

## Performance Optimizations
- 5-minute cache for frequently accessed data
- Batch endpoint for multiple symbol requests
- Efficient data structures for chart rendering
- Minimal DOM manipulation in frontend
- Asynchronous request handling

## Deployment Architecture
- **Development**: Localhost on port 8002
- **Production**: Not yet deployed (local only)
- **Backup Strategy**: Git versioning with timestamped backups
- **Recovery**: Documented rollback procedures in GIT_PROTECTION_STATUS.md