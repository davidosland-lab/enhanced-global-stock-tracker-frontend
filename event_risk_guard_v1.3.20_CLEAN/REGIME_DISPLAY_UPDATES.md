# Market Regime Engine Display Updates
## Event Risk Guard v1.3.20 - 2025-11-21

### Overview
Added Market Regime Engine results display to both the **Web UI Dashboard** and **Morning HTML Reports**.

---

## Changes Made

### 1. Report Generator (`models/screening/report_generator.py`)

**Purpose**: Add regime data section to HTML morning reports

**Changes**:
- Added `event_risk_data: Dict = None` parameter to `generate_morning_report()` method
- Added `event_risk_data` parameter to `_build_html_report()` method
- Created new method `_build_market_regime_section()` to render regime HTML
- Updated `_save_json_data()` to include event_risk_data in saved JSON

**New Section Includes**:
- Current market regime (Low/Medium/High Volatility) with color-coded badges
- Crash risk score with risk level (LOW/MODERATE/HIGH/CRITICAL)
- Daily and annualized volatility metrics
- Regime state probabilities with visual progress bars
- Analysis window information
- HMM methodology note

### 2. Overnight Pipeline (`models/screening/overnight_pipeline.py`)

**Purpose**: Pass event risk data to report generator

**Changes**:
- Updated `generate_morning_report()` call (line 688) to include `event_risk_data` parameter
- This ensures regime analysis results flow from EventRiskGuard to the report

### 3. Web UI Backend (`web_ui.py`)

**Purpose**: Provide API endpoint for regime data

**Changes**:
- Added new route `/api/regime` (line 320)
- Searches for regime data in multiple locations:
  - Latest JSON report data files (`*_data.json`)
  - Pipeline state files
- Returns regime data with availability status and timestamp
- Handles missing data gracefully

### 4. Web UI Template (`templates/dashboard.html`)

**Purpose**: Display regime data on dashboard

**Changes**:
- Added new "Market Regime Section" before main content area
- Includes:
  - 4-metric grid: Current Regime, Crash Risk Score, Daily/Annual Volatility
  - Regime state probabilities with 3 visual progress bars
  - Analysis window and methodology information
- Section is hidden by default, shown only when regime data is available

### 5. Dashboard Styles (`static/css/dashboard.css`)

**Purpose**: Style the new regime section

**Changes**:
- Added `.market-regime-section` and `.regime-card` styles
- Added `.regime-grid` for 4-column metric layout
- Added `.regime-metric` for metric cards
- Added `.regime-probabilities` section styles
- Added `.prob-bar` and `.prob-bar-container` for progress bars
- Added risk level badge styles (`.risk-low`, `.risk-moderate`, `.risk-high`, `.risk-critical`)
- Added responsive styles for mobile devices

### 6. Dashboard JavaScript (`static/js/dashboard.js`)

**Purpose**: Fetch and display regime data dynamically

**Changes**:
- Added `loadRegimeData()` function to fetch from `/api/regime` endpoint
- Added `refreshRegime()` function for manual refresh
- Integrated into initialization: called on page load
- Auto-refresh every 60 seconds
- Updates all regime metrics, probabilities, and risk badges
- Handles missing data by hiding the section

---

## Data Flow

```
Pipeline Execution:
    ↓
[EventRiskGuard._assess_event_risks()]
    ↓ (creates event_risk_data with market_regime)
[OvernightPipeline]
    ↓ (passes to report generator)
[ReportGenerator.generate_morning_report()]
    ↓ (saves in JSON and renders in HTML)
[Morning Report HTML + JSON Data File]
```

```
Web UI Display:
    ↓
[web_ui.py /api/regime endpoint]
    ↓ (reads from JSON data or pipeline state)
[dashboard.js loadRegimeData()]
    ↓ (updates DOM elements)
[Dashboard HTML Display]
```

---

## Market Regime Data Structure

The regime data from `MarketRegimeEngine.analyse()` contains:

```python
{
    'regime_label': 'high_vol',           # str: 'low_vol', 'medium_vol', or 'high_vol'
    'regime_probabilities': {             # dict: State probabilities
        0: 0.000001,                      # Low volatility probability
        1: 0.0001,                        # Medium volatility probability
        2: 0.9999                         # High volatility probability
    },
    'vol_1d': 0.00753,                    # float: Daily volatility (0.753%)
    'vol_annual': 0.1196,                 # float: Annualized volatility (11.96%)
    'vol_method': 'ewma',                 # str: Volatility calculation method
    'crash_risk_score': 0.6259,           # float: Crash risk 0-1 scale (62.59%)
    'data_window': {
        'start': '2025-05-25',            # str: Analysis start date
        'end': '2025-11-21'               # str: Analysis end date
    }
}
```

---

## Display Features

### HTML Morning Report

- **Prominent Section**: Displayed after Market Overview, before Opportunities
- **Visual Design**: Consistent with existing report styling
- **Color Coding**: 
  - Green (🟢) for Low Volatility
  - Yellow (🟡) for Medium Volatility
  - Red (🔴) for High Volatility
- **Risk Badges**: Color-coded (green/yellow/orange/red) based on crash risk level
- **Progress Bars**: Visual representation of regime state probabilities
- **Professional Layout**: Grid-based metric cards with clear labels

### Web UI Dashboard

- **Dynamic Section**: Appears only when regime data is available
- **Real-Time Updates**: Auto-refreshes every 60 seconds
- **Manual Refresh**: Dedicated refresh button
- **Responsive Design**: Adapts to mobile devices
- **Consistent Styling**: Matches dashboard theme
- **Interactive Elements**: Hover effects on cards

---

## Risk Level Thresholds

| Crash Risk Score | Risk Level | Badge Color | Description |
|------------------|------------|-------------|-------------|
| 0% - 30%         | LOW        | Green       | Normal market conditions |
| 30% - 50%        | MODERATE   | Yellow      | Elevated risk, monitor closely |
| 50% - 70%        | HIGH       | Orange      | Significant risk, reduce exposure |
| 70% - 100%       | CRITICAL   | Red         | Extreme risk, defensive positions |

---

## Files Modified

1. `models/screening/report_generator.py` - Added regime HTML section
2. `models/screening/overnight_pipeline.py` - Pass event_risk_data to report
3. `web_ui.py` - Added `/api/regime` endpoint
4. `templates/dashboard.html` - Added regime display section
5. `static/css/dashboard.css` - Added regime styles
6. `static/js/dashboard.js` - Added regime data loading

---

## Testing

To verify the implementation:

1. **Run the pipeline**:
   ```bash
   python models/screening/overnight_pipeline.py
   ```

2. **Check morning report**:
   - Open latest HTML report in `reports/html/`
   - Look for "Market Regime Analysis" section after Market Overview
   - Verify regime label, crash risk, volatility, and probabilities are displayed

3. **Check Web UI**:
   ```bash
   python web_ui.py
   ```
   - Access http://localhost:5000
   - Look for "Market Regime Analysis" section at top of page
   - Verify all metrics and probabilities are displayed
   - Test refresh button

4. **Check API endpoint**:
   ```bash
   curl http://localhost:5000/api/regime
   ```
   - Should return JSON with regime data if available

---

## Benefits

✅ **Transparency**: Users can now see market regime analysis results  
✅ **Risk Awareness**: Clear crash risk indicators help with decision-making  
✅ **Data Validation**: Visual display helps verify regime engine is working  
✅ **Professional Presentation**: Clean, organized display in both HTML and web UI  
✅ **Real-Time Monitoring**: Dashboard provides live updates  
✅ **Historical Record**: Reports preserve regime analysis for each run  

---

## Notes

- Regime section is **optional** - if no regime data exists, the section is gracefully hidden
- Data is sourced from both JSON report data and pipeline state files
- All volatility values are displayed as percentages (multiplied by 100)
- Crash risk score is displayed as percentage (0-100%) for clarity
- HMM methodology is explained in the info section
- Color scheme is consistent across report and dashboard

---

## Future Enhancements

Potential improvements for future versions:

- Historical regime chart showing regime changes over time
- Regime transition probabilities display
- Alerts when regime shifts to high volatility
- Export regime data to CSV
- Regime-based stock filtering in opportunities section
- Integration with email notifications for critical risk levels

---

**Implementation Date**: 2025-11-21  
**Version**: Event Risk Guard v1.3.20  
**Status**: ✅ Complete and Tested
