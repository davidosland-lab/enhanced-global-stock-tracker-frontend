# 📊 Real-Time Market Plotting Code Review - GSMT v3.0

**Source:** global_indices_tracker_enhanced.html  
**Location:** /home/user/webapp/working_directory/modules/market-tracking/  
**Date:** January 2, 2026

---

## 🎯 Key Features for Real-Time Market Movement Plotting

### 1. **Chart.js Implementation**
The GSMT uses Chart.js library for all visualizations:

```html
<!-- Chart.js for plotting -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<!-- Chart.js date adapter for time series -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
```

---

## 📈 Four Chart Types Implemented

### 1. Line Chart (Real-Time Price Movement)
```javascript
function plotLineChart(ctx, data, name) {
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: name,
                data: data.map(d => d.close),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointRadius: 0,           // No points for smooth line
                pointHoverRadius: 5       // Show points on hover
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'             // Show all values at same x-position
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: currentTimeframe === '1d' ? 'hour' : 'day'
                    },
                    grid: { display: false }
                },
                y: {
                    position: 'right',
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                }
            }
        }
    });
}
```

**Key Features:**
- Time-based X-axis with automatic scaling
- Smooth line with tension: 0.1
- Filled area under line
- Right-side Y-axis
- Responsive and interactive

---

### 2. Performance Chart (% Change from Start)
```javascript
function plotPerformanceChart(ctx, data, name) {
    // Calculate percentage change from first point
    const firstPrice = data[0].close;
    const performanceData = data.map(d => ({
        x: d.date,
        y: ((d.close - firstPrice) / firstPrice) * 100
    }));
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: '% Change',
                data: performanceData,
                borderColor: performanceData[performanceData.length - 1].y >= 0 
                    ? '#48bb78'  // Green for positive
                    : '#f56565', // Red for negative
                backgroundColor: performanceData[performanceData.length - 1].y >= 0 
                    ? 'rgba(72, 187, 120, 0.1)' 
                    : 'rgba(245, 101, 101, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointRadius: 0,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: currentTimeframe === '1d' ? 'hour' : 'day'
                    }
                },
                y: {
                    position: 'right',
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}
```

**Key Features:**
- Calculates % change from starting price
- Dynamic color based on performance (green/red)
- Y-axis labels formatted as percentages
- Perfect for comparing performance over time

---

### 3. Comparison Chart (Multiple Indices)
```javascript
function plotComparisonChart() {
    const canvas = document.getElementById('marketChart');
    const ctx = canvas.getContext('2d');
    
    // Prepare datasets for comparison
    const datasets = selectedIndices.map((symbol, index) => {
        const data = historicalData[symbol] || generateSampleHistoricalData(symbol, 30);
        const firstPrice = data[0].close;
        
        return {
            label: INDEX_DETAILS[symbol].name,
            data: data.map(d => ({
                x: d.date,
                y: ((d.close - firstPrice) / firstPrice) * 100
            })),
            borderColor: CHART_COLORS[index],      // Different color per index
            backgroundColor: 'transparent',
            borderWidth: 2,
            tension: 0.1,
            pointRadius: 0,
            pointHoverRadius: 5
        };
    });
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: { datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'                      // Show all series at same point
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'              // Legend at bottom
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                x: { type: 'time', time: { unit: 'day' } },
                y: {
                    position: 'right',
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}
```

**Key Features:**
- Multiple datasets on same chart
- Each index gets unique color
- Normalized to percentage change
- Interactive legend
- Up to 5 indices at once

---

### 4. Volume Chart
```javascript
function plotVolumeChart(ctx, data, name) {
    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: 'Volume',
                data: data.map(d => d.volume),
                backgroundColor: data.map(d => 
                    d.close > d.open 
                        ? 'rgba(72, 187, 120, 0.5)'  // Green if price up
                        : 'rgba(245, 101, 101, 0.5)' // Red if price down
                ),
                borderColor: data.map(d => 
                    d.close > d.open ? '#48bb78' : '#f56565'
                ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Volume: ${(context.parsed.y / 1000000000).toFixed(2)}B`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    position: 'right',
                    ticks: {
                        callback: function(value) {
                            return (value / 1000000000).toFixed(1) + 'B';
                        }
                    }
                }
            }
        }
    });
}
```

**Key Features:**
- Bar chart for volume
- Color-coded by price direction
- Y-axis formatted in billions
- Shows trading activity

---

## 🔄 Auto-Refresh System

### 1. Periodic Data Refresh
```javascript
document.addEventListener('DOMContentLoaded', () => {
    loadMarketData();
    setInterval(() => {
        if (document.getElementById('autoRefreshBtn').classList.contains('active')) {
            loadMarketData();
        }
    }, 30000); // Auto-refresh every 30 seconds if enabled
});
```

### 2. Data Loading Function
```javascript
async function loadMarketData() {
    const loadingDiv = document.getElementById('indicesLoading');
    const contentDiv = document.getElementById('indicesContent');
    
    try {
        loadingDiv.style.display = 'block';
        contentDiv.innerHTML = '';
        
        // Fetch from backend API
        const response = await fetch(`${API_URL}/api/indices`);
        if (!response.ok) throw new Error('Failed to fetch market data');
        
        const data = await response.json();
        marketData = data.indices || {};
        
        displayIndices();          // Update index cards
        updateStatus();            // Update status bar
        
        // Update selected chart if any
        if (selectedIndices.length > 0) {
            if (comparisonMode) {
                plotComparisonChart();
            } else {
                plotChart(selectedIndices[0]);
            }
        }
        
    } catch (error) {
        console.error('Error loading market data:', error);
        contentDiv.innerHTML = `<div class="error-message">Failed to load market data: ${error.message}</div>`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}
```

**Key Features:**
- Async/await for non-blocking fetches
- Error handling with fallback
- Updates both data display and charts
- Loading indicator

---

## 📊 Historical Data Fetching

```javascript
async function loadHistoricalData(symbol) {
    try {
        // Fetch real historical data from backend
        const response = await fetch(`${API_URL}/api/historical/${symbol}?period=${currentTimeframe}`);
        
        if (!response.ok) {
            // Fallback to sample data if backend doesn't have historical endpoint
            const days = currentTimeframe === '1d' ? 1 : 
                       currentTimeframe === '5d' ? 5 :
                       currentTimeframe === '1mo' ? 30 :
                       currentTimeframe === '3mo' ? 90 : 365;
            
            const data = generateSampleHistoricalData(symbol, days);
            historicalData[symbol] = data;
        } else {
            const result = await response.json();
            // Convert date strings to Date objects
            const data = result.data.map(d => ({
                ...d,
                date: new Date(d.date)
            }));
            historicalData[symbol] = data;
        }
        
        plotChart(symbol);
        
    } catch (error) {
        console.error('Error loading historical data:', error);
        // Fallback to sample data
        const data = generateSampleHistoricalData(symbol, days);
        historicalData[symbol] = data;
        plotChart(symbol);
    }
}
```

**API Endpoints Used:**
- `GET /api/indices` - Current market data
- `GET /api/historical/{symbol}?period={timeframe}` - Historical data

---

## 🎨 Chart Configuration

### Global Variables
```javascript
let marketData = {};              // Current market data
let selectedIndices = [];         // Currently selected indices
let currentChart = null;          // Chart.js instance
let autoRefreshInterval = null;   // Refresh timer
let comparisonMode = false;       // Single vs comparison mode
let currentChartType = 'line';    // Current chart type
let currentTimeframe = '5d';      // Current timeframe
let historicalData = {};          // Cached historical data
```

### Chart Colors
```javascript
const CHART_COLORS = [
    '#667eea', '#48bb78', '#ed8936', '#e53e3e', '#38b2ac',
    '#d69e2e', '#805ad5', '#dd6b20', '#2d3748', '#319795'
];
```

---

## 🔧 Key Functions for Your Dashboard

### 1. **Chart Destruction & Recreation**
```javascript
// Destroy existing chart before creating new one
if (currentChart) {
    currentChart.destroy();
}
```

**Why:** Prevents memory leaks and canvas errors

### 2. **Time-Based X-Axis**
```javascript
scales: {
    x: {
        type: 'time',
        time: {
            unit: currentTimeframe === '1d' ? 'hour' : 'day'
        },
        grid: { display: false }
    }
}
```

**Why:** Automatically formats dates and handles different timeframes

### 3. **Percentage Calculation**
```javascript
const firstPrice = data[0].close;
const performanceData = data.map(d => ({
    x: d.date,
    y: ((d.close - firstPrice) / firstPrice) * 100
}));
```

**Why:** Normalizes data for comparison (exactly what you need!)

### 4. **Responsive Charts**
```javascript
options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        intersect: false,
        mode: 'index'
    }
}
```

**Why:** Works on any screen size, better interactivity

---

## 🎯 How to Adapt for Your Dashboard

### Step 1: Replace yfinance with Chart.js
Instead of fetching data with yfinance and creating Plotly charts, use:

```javascript
// Fetch data
async function fetchMarketPerformance() {
    const indices = {
        '^AORD': 'ASX All Ords',
        '^GSPC': 'S&P 500',
        '^IXIC': 'NASDAQ',
        '^FTSE': 'FTSE 100'
    };
    
    const performanceData = [];
    
    for (const [symbol, name] of Object.entries(indices)) {
        // Fetch 24h data
        const response = await fetch(`/api/market-data/${symbol}?period=1d`);
        const data = await response.json();
        
        // Calculate 24h % change
        const firstPrice = data[0].close;
        const lastPrice = data[data.length - 1].close;
        const pctChange = ((lastPrice - firstPrice) / firstPrice) * 100;
        
        performanceData.push({
            name: name,
            symbol: symbol,
            change: pctChange
        });
    }
    
    return performanceData;
}

// Plot as bar chart
function plotMarketPerformance(data) {
    const ctx = document.getElementById('marketPerformanceChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                label: '24h % Change',
                data: data.map(d => d.change),
                backgroundColor: data.map(d => 
                    d.change >= 0 ? '#4CAF50' : '#F44336'
                ),
                borderColor: data.map(d => 
                    d.change >= 0 ? '#4CAF50' : '#F44336'
                ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y >= 0 ? '+' : ''}${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}
```

### Step 2: Add to Dashboard Callback
```python
# In unified_trading_dashboard.py

@app.callback(
    Output('market-performance-chart', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_market_performance(n):
    # Instead of dcc.Graph with Plotly figure,
    # return html.Div with canvas:
    
    return html.Div([
        html.Canvas(id='marketPerfCanvas'),
        html.Script('''
            // Fetch and plot using Chart.js
            fetch('/api/market-performance')
                .then(r => r.json())
                .then(data => plotMarketPerformance(data));
        ''')
    ])
```

---

## 📝 Key Takeaways for Your Dashboard

### 1. **Use Chart.js Instead of Plotly**
- Lighter weight
- Better for real-time updates
- More customizable
- Smoother animations

### 2. **Time-Series Configuration**
```javascript
x: {
    type: 'time',
    time: { unit: 'hour' }  // or 'day', 'minute'
}
```

### 3. **Percentage Calculation**
```javascript
const pctChange = ((current - previous) / previous) * 100;
```

### 4. **Color Coding**
```javascript
backgroundColor: value >= 0 ? '#4CAF50' : '#F44336'
```

### 5. **Auto-Refresh**
```javascript
setInterval(() => {
    loadMarketData();
    plotChart();
}, 5000); // Every 5 seconds
```

---

## 🚀 Implementation Plan for Your Dashboard

### Option 1: Keep Dash + Add Chart.js
1. Create HTML template with Chart.js canvas
2. Add JavaScript for chart creation
3. Fetch data via Flask endpoint
4. Update chart every 5 seconds

### Option 2: Migrate to Pure HTML + Chart.js
1. Convert dashboard to static HTML
2. Use Chart.js for all visualizations
3. Fetch from Python backend API
4. More control over animations

### Option 3: Hybrid (Recommended)
1. Keep Dash for main dashboard
2. Use `dcc.Graph` with Plotly for portfolio/performance
3. Add Chart.js for market performance panel
4. Best of both worlds

---

## 📚 Files to Review

1. **global_indices_tracker_enhanced.html** - Full implementation
2. **global_indices_tracker_realdata_only.html** - Real data only version
3. **global_indices_tracker_sandbox.html** - Sandbox demo version

**Location:** `/home/user/webapp/working_directory/modules/market-tracking/`

---

## 🎯 Summary

The GSMT v3.0 code provides:
- ✅ Real-time market data fetching
- ✅ Multiple chart types (line, performance, comparison, volume)
- ✅ Auto-refresh every 30 seconds
- ✅ Time-based X-axis
- ✅ Percentage change calculations
- ✅ Color-coded by direction
- ✅ Interactive tooltips
- ✅ Responsive design

**Key Code Sections:**
- Lines 708-763: Line chart plotting
- Lines 850-914: Performance chart (% change)
- Lines 916-997: Comparison chart (multiple indices)
- Lines 796-848: Volume chart
- Lines 479-511: Data loading with auto-refresh
- Lines 595-632: Historical data fetching

---

**Date:** January 2, 2026  
**Version:** GSMT v3.0 Code Review  
**For:** Phase 3 Trading Dashboard Enhancement

---
