# Backtest Results Storage & Retrieval Feature

## Overview

All backtest and optimization results are now automatically saved to JSON files and can be retrieved through dedicated API endpoints.

## 📂 Where Results Are Saved

**Location:** `models/backtest_results/`

**File Naming Convention:**
- Backtests: `backtest_{SYMBOL}_{TIMESTAMP}.json`
- Optimizations: `optimization_{SYMBOL}_{TIMESTAMP}.json`

**Example:**
```
models/backtest_results/
├── backtest_AAPL_20251105_143022.json
├── backtest_CBA.AX_20251105_143155.json
├── optimization_AAPL_20251105_144530.json
└── optimization_MSFT_20251105_145012.json
```

## 🎯 What Gets Saved

### Backtest Results
When you run a backtest (`POST /api/backtest/run`), the following is automatically saved:

```json
{
  "symbol": "AAPL",
  "backtest_period": {
    "start": "2024-01-01",
    "end": "2024-10-31"
  },
  "model_type": "ensemble",
  "data_points": 210,
  "predictions_generated": 210,
  "performance": {
    "initial_capital": 10000,
    "final_equity": 11523.45,
    "total_return_pct": 15.23,
    "total_trades": 42,
    "winning_trades": 28,
    "losing_trades": 14,
    "win_rate": 66.67,
    "sharpe_ratio": 1.85,
    "sortino_ratio": 2.34,
    "max_drawdown_pct": -5.67,
    "profit_factor": 2.15,
    "total_commission_paid": 52.30,
    "avg_hold_time_days": 5.2
  },
  "prediction_accuracy": {
    "total_predictions": 210,
    "actionable_predictions": 126,
    "buy_signals": 84,
    "sell_signals": 42,
    "overall_accuracy": 72.5
  },
  "equity_curve": [...],
  "timestamp": "2025-11-05T14:30:22",
  "results_file": "models/backtest_results/backtest_AAPL_20251105_143022.json"
}
```

### Optimization Results
When you run parameter optimization (`POST /api/backtest/optimize`), the following is saved:

```json
{
  "symbol": "AAPL",
  "optimization_method": "random",
  "iterations_completed": 50,
  "best_parameters": {
    "confidence_threshold": 0.65,
    "lookback_days": 80,
    "max_position_size": 0.25,
    "stop_loss_pct": 0.04,
    "take_profit_pct": 0.12
  },
  "best_performance": {
    "total_return_pct": 18.45,
    "sharpe_ratio": 2.12,
    "max_drawdown_pct": -4.32,
    "total_trades": 38,
    "win_rate": 71.05
  },
  "parameter_grid": {...},
  "start_date": "2024-01-01",
  "end_date": "2024-10-31",
  "initial_capital": 10000,
  "timestamp": "2025-11-05T14:45:30",
  "all_results": [
    // All iteration results included for analysis
  ],
  "results_file": "models/backtest_results/optimization_AAPL_20251105_144530.json"
}
```

## 🔌 API Endpoints

### 1. List All Results

**Endpoint:** `GET /api/backtest/results`

**Query Parameters:**
- `type`: Filter by type ('backtest', 'optimization', or 'all') - default: 'all'
- `symbol`: Filter by stock symbol (optional)
- `limit`: Number of results to return - default: 50

**Examples:**

```bash
# List all results (most recent first)
GET http://localhost:5001/api/backtest/results

# List only backtests
GET http://localhost:5001/api/backtest/results?type=backtest

# List only optimizations
GET http://localhost:5001/api/backtest/results?type=optimization

# List results for specific symbol
GET http://localhost:5001/api/backtest/results?symbol=AAPL

# List last 10 AAPL backtests
GET http://localhost:5001/api/backtest/results?type=backtest&symbol=AAPL&limit=10
```

**Response:**
```json
{
  "results": [
    {
      "filename": "backtest_AAPL_20251105_143022.json",
      "filepath": "/path/to/models/backtest_results/backtest_AAPL_20251105_143022.json",
      "symbol": "AAPL",
      "type": "backtest",
      "size_bytes": 45632,
      "modified": "2025-11-05T14:30:22",
      "age_hours": 2.5
    },
    {
      "filename": "optimization_AAPL_20251105_144530.json",
      "filepath": "/path/to/models/backtest_results/optimization_AAPL_20251105_144530.json",
      "symbol": "AAPL",
      "type": "optimization",
      "size_bytes": 128456,
      "modified": "2025-11-05T14:45:30",
      "age_hours": 1.2
    }
  ],
  "count": 2,
  "results_directory": "/path/to/models/backtest_results"
}
```

### 2. Get Specific Result

**Endpoint:** `GET /api/backtest/results/<filename>`

**Example:**
```bash
GET http://localhost:5001/api/backtest/results/backtest_AAPL_20251105_143022.json
```

**Response:**
```json
{
  // Full backtest or optimization result
  "symbol": "AAPL",
  "performance": {...},
  // ... all saved data
  "_metadata": {
    "filename": "backtest_AAPL_20251105_143022.json",
    "filepath": "/path/to/file",
    "size_bytes": 45632,
    "modified": "2025-11-05T14:30:22"
  }
}
```

### 3. Delete Result

**Endpoint:** `DELETE /api/backtest/results/<filename>`

**Example:**
```bash
DELETE http://localhost:5001/api/backtest/results/backtest_AAPL_20251105_143022.json
```

**Response:**
```json
{
  "success": true,
  "message": "Result file deleted: backtest_AAPL_20251105_143022.json"
}
```

## 📊 Usage Examples

### Example 1: Run Backtest and View Saved Results

```python
import requests
import json

# Step 1: Run a backtest
backtest_data = {
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-10-31",
    "model_type": "ensemble",
    "initial_capital": 10000
}

response = requests.post('http://localhost:5001/api/backtest/run', json=backtest_data)
result = response.json()

# Get the saved filename
results_file = result.get('results_file')
print(f"Results saved to: {results_file}")

# Step 2: List all AAPL backtests
list_response = requests.get('http://localhost:5001/api/backtest/results?symbol=AAPL&type=backtest')
all_results = list_response.json()

print(f"\nFound {all_results['count']} AAPL backtests:")
for r in all_results['results']:
    print(f"  - {r['filename']} (Return: {r.get('performance', {}).get('total_return_pct', 'N/A')}%)")

# Step 3: Retrieve specific result
if all_results['results']:
    filename = all_results['results'][0]['filename']
    detail_response = requests.get(f'http://localhost:5001/api/backtest/results/{filename}')
    detailed_result = detail_response.json()
    
    print(f"\nDetailed Results for {filename}:")
    print(f"  Total Return: {detailed_result['performance']['total_return_pct']}%")
    print(f"  Win Rate: {detailed_result['performance']['win_rate']}%")
    print(f"  Sharpe Ratio: {detailed_result['performance']['sharpe_ratio']}")
```

### Example 2: Run Optimization and Compare Results

```python
import requests

# Run optimization
opt_data = {
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-10-31",
    "optimization_method": "random",
    "max_iterations": 50
}

response = requests.post('http://localhost:5001/api/backtest/optimize', json=opt_data)
result = response.json()

print(f"✓ Optimization complete!")
print(f"Best Parameters: {json.dumps(result['best_parameters'], indent=2)}")
print(f"Best Return: {result['best_performance']['total_return_pct']}%")

# View all optimizations for comparison
all_opts = requests.get('http://localhost:5001/api/backtest/results?type=optimization&symbol=AAPL')
optimizations = all_opts.json()

print(f"\nComparing {optimizations['count']} optimizations:")
for opt in optimizations['results'][:5]:
    # Get detailed results
    details = requests.get(f'http://localhost:5001/api/backtest/results/{opt["filename"]}').json()
    best_perf = details.get('best_performance', {})
    
    print(f"\n{opt['filename']}:")
    print(f"  Method: {details.get('optimization_method')}")
    print(f"  Iterations: {details.get('iterations_completed')}")
    print(f"  Best Return: {best_perf.get('total_return_pct')}%")
    print(f"  Best Sharpe: {best_perf.get('sharpe_ratio')}")
```

### Example 3: Clean Up Old Results

```python
import requests
from datetime import datetime, timedelta

# Get all results
response = requests.get('http://localhost:5001/api/backtest/results')
all_results = response.json()

# Delete results older than 30 days
cutoff = datetime.now() - timedelta(days=30)

for result in all_results['results']:
    modified = datetime.fromisoformat(result['modified'])
    
    if modified < cutoff:
        filename = result['filename']
        delete_response = requests.delete(f'http://localhost:5001/api/backtest/results/{filename}')
        
        if delete_response.status_code == 200:
            print(f"✓ Deleted old result: {filename}")
        else:
            print(f"✗ Failed to delete: {filename}")

print(f"\nCleanup complete!")
```

## 🔍 Finding Optimal Parameters

The optimization results include ALL tested configurations, allowing you to:

1. **Compare Top Performers:**
```python
# Get optimization results
response = requests.get('http://localhost:5001/api/backtest/results/optimization_AAPL_20251105_144530.json')
data = response.json()

# Sort all results by return
all_results = data.get('all_results', [])
sorted_results = sorted(all_results, key=lambda x: x.get('total_return_pct', 0), reverse=True)

# Show top 5 configurations
print("Top 5 configurations by return:")
for i, result in enumerate(sorted_results[:5], 1):
    print(f"\n{i}. Parameters: {result.get('parameters')}")
    print(f"   Return: {result.get('total_return_pct')}%")
    print(f"   Sharpe: {result.get('sharpe_ratio')}")
    print(f"   Max DD: {result.get('max_drawdown_pct')}%")
```

2. **Find Balanced Configuration:**
```python
# Find config with best Sharpe ratio (risk-adjusted return)
best_sharpe = max(all_results, key=lambda x: x.get('sharpe_ratio', 0))

print(f"Best risk-adjusted configuration:")
print(f"  Parameters: {best_sharpe.get('parameters')}")
print(f"  Sharpe Ratio: {best_sharpe.get('sharpe_ratio')}")
print(f"  Return: {best_sharpe.get('total_return_pct')}%")
```

3. **Analyze Parameter Sensitivity:**
```python
# Group results by parameter values
import pandas as pd

df = pd.DataFrame(all_results)
print(f"\nPerformance by confidence threshold:")
print(df.groupby('parameters.confidence_threshold')['total_return_pct'].mean())
```

## 📁 File Management

### Manual Access
Results are stored as standard JSON files and can be:
- Opened in any text editor
- Imported into Excel/Google Sheets
- Analyzed with Python pandas
- Backed up to cloud storage
- Versioned in git (if desired)

### Automatic Cleanup
Consider implementing a cron job or scheduled task to:
- Delete results older than X days
- Archive results to separate storage
- Compress older files

### Backup Strategy
```bash
# Backup all results to date-stamped folder
mkdir backtest_backups
cp -r models/backtest_results "backtest_backups/backup_$(date +%Y%m%d)"

# Or create compressed archive
tar -czf "backtest_backup_$(date +%Y%m%d).tar.gz" models/backtest_results/
```

## 🎯 Integration with Existing Workflow

### Before (Results were lost)
```python
# Run backtest
response = requests.post('/api/backtest/run', json=data)
result = response.json()

# Results only in response - if you close browser, data is lost
print(f"Return: {result['performance']['total_return_pct']}%")
```

### After (Results are saved automatically)
```python
# Run backtest - automatically saved
response = requests.post('/api/backtest/run', json=data)
result = response.json()

# Results available anytime via saved file
results_file = result['results_file']
print(f"Results saved to: {results_file}")

# Retrieve later
later_response = requests.get(f'/api/backtest/results/{os.path.basename(results_file)}')
saved_result = later_response.json()
```

## 🔒 Security Considerations

1. **Path Traversal Protection**: The API validates that requested files are within the `backtest_results` directory
2. **File Access**: Only JSON files in the results directory can be accessed
3. **No Execution**: Results are stored as JSON data, not executable code
4. **Local Access Only**: API is designed for localhost access (port 5001)

## 📈 Benefits

1. **Historical Comparison**: Compare backtest results over time
2. **Parameter Analysis**: Review which parameters worked best
3. **Audit Trail**: Keep record of all testing and optimization
4. **Reproducibility**: Re-examine past results without re-running
5. **Documentation**: Export results for reports and presentations
6. **Learning**: Study what configurations worked in different market conditions

## 🚀 Next Steps

With results now saved automatically, you can:

1. Build a dashboard to visualize historical performance
2. Create reports comparing different strategies
3. Track optimization improvements over time
4. Share results with team members
5. Automate parameter selection based on historical best performers

---

## Quick Reference

**Run backtest:** `POST /api/backtest/run`  
**Run optimization:** `POST /api/backtest/optimize`  
**List results:** `GET /api/backtest/results`  
**Get result:** `GET /api/backtest/results/<filename>`  
**Delete result:** `DELETE /api/backtest/results/<filename>`  

**Results location:** `models/backtest_results/`  
**File format:** JSON  
**Naming:** `{type}_{symbol}_{timestamp}.json`

---

**Questions or issues?** Check the logs or open an issue on GitHub.
