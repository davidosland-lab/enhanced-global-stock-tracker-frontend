/**
 * Backtest Visualization Module
 * Handles displaying backtest results with interactive charts
 * Requires Chart.js 4.4.0+
 */

// Global variable to store current backtest data for downloads
let currentBacktestData = null;
let currentPortfolioData = null;

// Chart instances (to destroy before recreating)
let backtestEquityChartInstance = null;
let portfolioEquityChartInstance = null;
let portfolioAllocationChartInstance = null;

/**
 * Show Backtest Results Modal
 * Displays single-stock backtest results with equity curve chart
 */
function showBacktestResultsModal(data) {
    currentBacktestData = data;
    
    // Update modal title
    document.getElementById('backtestModalTitle').innerHTML = 
        `<i class="fas fa-chart-line"></i> Backtest Results - ${data.symbol}`;
    
    // Populate metrics grid
    const perf = data.performance;
    const accuracy = data.prediction_accuracy;
    
    const returnClass = perf.total_return_pct >= 0 ? 'metric-positive' : 'metric-negative';
    const returnIcon = perf.total_return_pct >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
    
    const metricsHTML = `
        <div class="metric-card">
            <div class="metric-label">Initial Capital</div>
            <div class="metric-value">$${perf.initial_capital.toLocaleString()}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Final Equity</div>
            <div class="metric-value">$${perf.final_equity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Return</div>
            <div class="metric-value ${returnClass}">
                <i class="fas ${returnIcon}"></i> ${perf.total_return_pct.toFixed(2)}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Trades</div>
            <div class="metric-value">${perf.total_trades}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Win Rate</div>
            <div class="metric-value">${perf.win_rate.toFixed(1)}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Sharpe Ratio</div>
            <div class="metric-value">${perf.sharpe_ratio.toFixed(3)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Max Drawdown</div>
            <div class="metric-value metric-negative">${perf.max_drawdown_pct.toFixed(2)}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Profit Factor</div>
            <div class="metric-value">${perf.profit_factor.toFixed(2)}</div>
        </div>
    `;
    
    document.getElementById('backtestMetricsGrid').innerHTML = metricsHTML;
    
    // Render equity curve chart
    renderBacktestEquityCurve(data.equity_curve);
    
    // Populate trade statistics
    const tradeStatsHTML = `
        <div class="glass-panel p-6">
            <h3 class="text-xl font-semibold mb-4"><i class="fas fa-chart-bar"></i> Trade Statistics</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div>
                    <div class="text-sm text-gray-400">Winning Trades</div>
                    <div class="text-2xl font-bold text-green-500">${perf.winning_trades} (${((perf.winning_trades/perf.total_trades)*100).toFixed(1)}%)</div>
                </div>
                <div>
                    <div class="text-sm text-gray-400">Losing Trades</div>
                    <div class="text-2xl font-bold text-red-500">${perf.losing_trades} (${((perf.losing_trades/perf.total_trades)*100).toFixed(1)}%)</div>
                </div>
                <div>
                    <div class="text-sm text-gray-400">Avg Hold Time</div>
                    <div class="text-2xl font-bold">${perf.avg_hold_time_days.toFixed(1)} days</div>
                </div>
                <div>
                    <div class="text-sm text-gray-400">Total Commissions</div>
                    <div class="text-2xl font-bold">$${perf.total_commission_paid.toFixed(2)}</div>
                </div>
                <div>
                    <div class="text-sm text-gray-400">Sortino Ratio</div>
                    <div class="text-2xl font-bold">${perf.sortino_ratio.toFixed(3)}</div>
                </div>
                <div>
                    <div class="text-sm text-gray-400">Prediction Accuracy</div>
                    <div class="text-2xl font-bold">${accuracy.overall_accuracy ? accuracy.overall_accuracy.toFixed(1) : 'N/A'}%</div>
                </div>
            </div>
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(148, 163, 184, 0.2);">
                <div class="text-sm text-gray-400">Backtest Period</div>
                <div class="text-lg">${data.backtest_period.start} to ${data.backtest_period.end}</div>
                <div class="text-sm text-gray-400 mt-2">Model Type</div>
                <div class="text-lg">${data.model_type.toUpperCase()}</div>
                <div class="text-sm text-gray-400 mt-2">Data Points</div>
                <div class="text-lg">${data.data_points}</div>
            </div>
        </div>
    `;
    
    document.getElementById('backtestTradeStats').innerHTML = tradeStatsHTML;
    
    // Show modal
    document.getElementById('backtestResultsModal').style.display = 'block';
}

/**
 * Render Backtest Equity Curve Chart
 */
function renderBacktestEquityCurve(equityCurveData) {
    // Destroy existing chart if it exists
    if (backtestEquityChartInstance) {
        backtestEquityChartInstance.destroy();
    }
    
    const ctx = document.getElementById('backtestEquityChart').getContext('2d');
    
    // Prepare data
    const labels = equityCurveData.map(point => {
        const date = new Date(point.timestamp);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const equityValues = equityCurveData.map(point => point.equity);
    
    // Calculate initial value for reference line
    const initialEquity = equityValues[0];
    
    backtestEquityChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Portfolio Value',
                    data: equityValues,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: 'rgb(59, 130, 246)',
                    pointHoverBorderColor: 'white',
                    pointHoverBorderWidth: 2
                },
                {
                    label: 'Initial Capital',
                    data: Array(equityValues.length).fill(initialEquity),
                    borderColor: 'rgba(148, 163, 184, 0.5)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#e2e8f0',
                        font: {
                            size: 12
                        },
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Close Backtest Modal
 */
function closeBacktestModal() {
    document.getElementById('backtestResultsModal').style.display = 'none';
    if (backtestEquityChartInstance) {
        backtestEquityChartInstance.destroy();
        backtestEquityChartInstance = null;
    }
}

/**
 * Show Portfolio Backtest Results Modal
 */
function showPortfolioBacktestModal(data) {
    currentPortfolioData = data;
    
    // Populate metrics
    const metrics = data.portfolio_metrics;
    const returnClass = metrics.total_return_pct >= 0 ? 'metric-positive' : 'metric-negative';
    const returnIcon = metrics.total_return_pct >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
    
    const metricsHTML = `
        <div class="metric-card">
            <div class="metric-label">Initial Capital</div>
            <div class="metric-value">$${metrics.initial_capital.toLocaleString()}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Final Equity</div>
            <div class="metric-value">$${metrics.final_equity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Return</div>
            <div class="metric-value ${returnClass}">
                <i class="fas ${returnIcon}"></i> ${metrics.total_return_pct.toFixed(2)}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Trades</div>
            <div class="metric-value">${metrics.total_trades}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Win Rate</div>
            <div class="metric-value">${metrics.win_rate.toFixed(1)}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Sharpe Ratio</div>
            <div class="metric-value">${metrics.sharpe_ratio.toFixed(3)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Max Drawdown</div>
            <div class="metric-value metric-negative">${metrics.max_drawdown_pct.toFixed(2)}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Volatility</div>
            <div class="metric-value">${metrics.volatility.toFixed(2)}%</div>
        </div>
    `;
    
    document.getElementById('portfolioMetricsGrid').innerHTML = metricsHTML;
    
    // Render charts
    renderPortfolioEquityCurve(data.equity_curve);
    renderPortfolioAllocation(data.target_allocations);
    
    // Show modal
    document.getElementById('portfolioBacktestModal').style.display = 'block';
}

/**
 * Render Portfolio Equity Curve
 */
function renderPortfolioEquityCurve(equityCurveData) {
    if (portfolioEquityChartInstance) {
        portfolioEquityChartInstance.destroy();
    }
    
    const ctx = document.getElementById('portfolioEquityChart').getContext('2d');
    
    const labels = equityCurveData.map(point => {
        const date = new Date(point.timestamp);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const equityValues = equityCurveData.map(point => point.equity);
    const initialEquity = equityValues[0];
    
    portfolioEquityChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Portfolio Value',
                    data: equityValues,
                    borderColor: 'rgb(139, 92, 246)',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                },
                {
                    label: 'Initial Capital',
                    data: Array(equityValues.length).fill(initialEquity),
                    borderColor: 'rgba(148, 163, 184, 0.5)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#e2e8f0',
                        font: { size: 12 },
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(139, 92, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + 
                                context.parsed.y.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                    ticks: { color: '#94a3b8', maxRotation: 45 }
                },
                y: {
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                    ticks: {
                        color: '#94a3b8',
                        callback: value => '$' + value.toLocaleString()
                    }
                }
            }
        }
    });
}

/**
 * Render Portfolio Allocation Pie Chart
 */
function renderPortfolioAllocation(allocations) {
    if (portfolioAllocationChartInstance) {
        portfolioAllocationChartInstance.destroy();
    }
    
    const ctx = document.getElementById('portfolioAllocationChart').getContext('2d');
    
    const symbols = Object.keys(allocations);
    const weights = Object.values(allocations).map(w => w * 100);
    
    const colors = [
        'rgb(59, 130, 246)',
        'rgb(139, 92, 246)',
        'rgb(236, 72, 153)',
        'rgb(34, 197, 94)',
        'rgb(251, 146, 60)',
        'rgb(234, 179, 8)',
        'rgb(14, 165, 233)',
        'rgb(168, 85, 247)'
    ];
    
    portfolioAllocationChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: symbols,
            datasets: [{
                data: weights,
                backgroundColor: colors.slice(0, symbols.length),
                borderColor: 'rgba(30, 41, 59, 0.8)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#e2e8f0',
                        font: { size: 12 },
                        padding: 15,
                        generateLabels: function(chart) {
                            const data = chart.data;
                            return data.labels.map((label, i) => ({
                                text: `${label}: ${data.datasets[0].data[i].toFixed(1)}%`,
                                fillStyle: data.datasets[0].backgroundColor[i],
                                hidden: false,
                                index: i
                            }));
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e2e8f0',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(59, 130, 246, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Close Portfolio Modal
 */
function closePortfolioModal() {
    document.getElementById('portfolioBacktestModal').style.display = 'none';
    if (portfolioEquityChartInstance) {
        portfolioEquityChartInstance.destroy();
        portfolioEquityChartInstance = null;
    }
    if (portfolioAllocationChartInstance) {
        portfolioAllocationChartInstance.destroy();
        portfolioAllocationChartInstance = null;
    }
}

/**
 * Download Backtest Results as CSV
 */
function downloadBacktestCSV() {
    if (!currentBacktestData) return;
    
    const equity = currentBacktestData.equity_curve;
    let csv = 'Timestamp,Equity\n';
    equity.forEach(point => {
        csv += `${point.timestamp},${point.equity}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backtest_${currentBacktestData.symbol}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Download Backtest Results as JSON
 */
function downloadBacktestJSON() {
    if (!currentBacktestData) return;
    
    const json = JSON.stringify(currentBacktestData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backtest_${currentBacktestData.symbol}_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Download Portfolio Results as CSV
 */
function downloadPortfolioCSV() {
    if (!currentPortfolioData) return;
    
    const equity = currentPortfolioData.equity_curve;
    let csv = 'Timestamp,Equity\n';
    equity.forEach(point => {
        csv += `${point.timestamp},${point.equity}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_backtest_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Download Portfolio Results as JSON
 */
function downloadPortfolioJSON() {
    if (!currentPortfolioData) return;
    
    const json = JSON.stringify(currentPortfolioData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_backtest_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Close modals when clicking outside
window.onclick = function(event) {
    const backtestModal = document.getElementById('backtestResultsModal');
    const portfolioModal = document.getElementById('portfolioBacktestModal');
    
    if (event.target === backtestModal) {
        closeBacktestModal();
    }
    if (event.target === portfolioModal) {
        closePortfolioModal();
    }
}
