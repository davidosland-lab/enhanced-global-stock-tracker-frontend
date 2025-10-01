# CRITICAL PROJECT REQUIREMENTS - DO NOT VIOLATE

## 🚫 ABSOLUTE REQUIREMENTS - NO EXCEPTIONS

### 1. NO SYNTHETIC/MOCK/DEMO DATA - EVER
- **NEVER** use Math.random() for price generation
- **NEVER** create generateMockData() or similar functions
- **NEVER** provide fallback synthetic data when backend is unavailable
- **ALWAYS** use real Yahoo Finance data via the backend API
- If backend is unavailable, show error message - DO NOT generate fake data

**User Quote**: "I have also previously set very clear parameters that there is to be no demo or synthetic data used in this project."

### 2. Windows Localhost Fix
- **ALWAYS** use hardcoded `http://localhost:8002` for API calls
- **NEVER** use dynamic URL construction that might fail on Windows
- This was explicitly required to fix Windows 11 localhost connection issues

### 3. Chart Design Requirements
- Three markets on ONE chart with overlapping lines (not separate cards)
- Colors MUST be:
  - ASX/AORD: RED (#ff0000)
  - FTSE: BLUE (#0000ff)  
  - S&P 500: PURPLE (#800080)
- Time axis: 09:00 to 16:00 AEST
- Show percentage change from session start
- Include market zone annotations for trading hours

## 📁 Project Structure

```
/home/user/webapp/
├── working_directory/
│   ├── backend_fixed.py          # PROTECTED - DO NOT MODIFY
│   ├── index.html                # Main dashboard
│   └── modules/
│       └── market-tracking/
│           ├── three_markets_chart.html     # Main chart (user's design)
│           ├── market_periods_working_chart.html  # Working version
│           └── mobile_global_tracker.html   # Mobile version (FIXED)
├── prompts/                      # Prompt capture system
├── docs/                         # Documentation
└── archive/                      # Old files (168+ files moved here)
```

## 🔧 Technical Stack

### Backend (backend_fixed.py)
- FastAPI on port 8002
- CORS enabled for all origins
- Endpoints:
  - `/api/quote/{symbol}` - Current quote
  - `/api/historical/{symbol}` - Historical data (returns nested format)
  - `/api/markets` - Multiple markets
  - `/api/search` - Symbol search

### Data Format
Historical endpoint returns NESTED format:
```json
{
  "symbol": "^AORD",
  "period": "5d",
  "data": [...],  // Array is nested inside
  "dataPoints": 100
}
```

Frontend must handle: `const data = result.data || result;`

### Percentage Calculation
Correct formula using previous close:
```python
if len(hist) > 1:
    prev_close = hist['Close'].iloc[-2]
    change_pct = ((current_price - prev_close) / prev_close) * 100
```

## 🕐 Market Hours (AEST)

| Market | Open  | Close | Zone Color |
|--------|-------|-------|------------|
| ASX    | 10:00 | 16:00 | Red        |
| London | 18:00 | 02:30 | Blue       |
| NY     | 00:30 | 07:00 | Purple     |

## ⚠️ Common Mistakes to Avoid

1. **DO NOT** add synthetic data "for testing" or "as fallback"
2. **DO NOT** modify backend_fixed.py - it's working correctly
3. **DO NOT** use separate cards when user wants ONE chart
4. **DO NOT** forget to use AEST timezone
5. **DO NOT** use dynamic localhost URLs on Windows

## 🎯 User's Core Requirements

The user spent a month dealing with regressions and explicitly wants:
1. Real data only (10+ requests made about this)
2. Chart matching their hand-drawn design (3 overlapping lines)
3. Windows localhost fix maintained
4. Comprehensive documentation to avoid re-prompting
5. Git tracking of all changes

## 📊 Chart Implementation

The correct implementation is in `three_markets_chart.html`:
- Uses Chart.js with annotation plugin
- Shows three overlapping performance lines
- Calculates percentage change from first data point
- Displays in AEST timezone
- Includes market zone annotations
- Updates every 30 seconds with real data

## 🔴 Final Warning

**NEVER ADD SYNTHETIC DATA** - The user has been explicit about this requirement multiple times. Always use real Yahoo Finance data through the backend API. If the backend is down, show an error message rather than generating fake data.

---
Last Updated: October 2024
User's explicit requirement: NO DEMO OR SYNTHETIC DATA