/**
 * Live Trading Dashboard JavaScript
 * Handles real-time updates and user interactions
 */

// Configuration
const CONFIG = {
    updateInterval: 5000,  // Update every 5 seconds
    apiBaseUrl: '/api',
    charts: {}
};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Live Trading Dashboard initialized');
    
    // Initialize charts
    initializeCharts();
    
    // Start periodic updates
    startPeriodicUpdates();
    
    // Initial data fetch
    refreshAll();
});

// ============================================================================
// PERIODIC UPDATES
// ============================================================================

function startPeriodicUpdates() {
    // Update status every 5 seconds
    setInterval(() => {
        refreshStatus();
        refreshPositions();
        refreshAlerts();
        refreshIntraday();
    }, CONFIG.updateInterval);
    
    // Update performance charts every 30 seconds
    setInterval(() => {
        refreshPerformance();
    }, 30000);
}

// ============================================================================
// DATA FETCHING
// ============================================================================

async function refreshAll() {
    await refreshStatus();
    await refreshPositions();
    await refreshTrades();
    await refreshPerformance();
    await refreshAlerts();
    await refreshIntraday();
}

async function refreshStatus() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/status`);
        const data = await response.json();
        
        if (data.status === 'online') {
            updateStatusBadge('Online', 'success');
            updateSummaryCards(data);
            updateMarketContext(data.market_context);
        } else {
            updateStatusBadge('Offline', 'danger');
        }
        
        // Update last update time
        document.getElementById('last-update').textContent = 
            `Last update: ${new Date(data.timestamp).toLocaleTimeString()}`;
            
    } catch (error) {
        console.error('Error fetching status:', error);
        updateStatusBadge('Error', 'danger');
    }
}

async function refreshPositions() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/positions`);
        const data = await response.json();
        
        updatePositionsTable(data.positions);
        
    } catch (error) {
        console.error('Error fetching positions:', error);
    }
}

async function refreshTrades() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/trades?limit=20`);
        const data = await response.json();
        
        updateTradesTable(data.trades);
        
    } catch (error) {
        console.error('Error fetching trades:', error);
    }
}

async function refreshPerformance() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/performance`);
        const data = await response.json();
        
        updatePerformanceCharts(data);
        
    } catch (error) {
        console.error('Error fetching performance:', error);
    }
}

async function refreshAlerts() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/alerts?limit=20`);
        const data = await response.json();
        
        updateAlertsFeed(data.alerts);
        
    } catch (error) {
        console.error('Error fetching alerts:', error);
    }
}

async function refreshIntraday() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/intraday`);
        const data = await response.json();
        
        updateIntradayStats(data);
        
    } catch (error) {
        console.error('Error fetching intraday status:', error);
    }
}

// ============================================================================
// UI UPDATES
// ============================================================================

function updateStatusBadge(status, type) {
    const badge = document.getElementById('status-badge');
    badge.className = `badge badge-${type}`;
    badge.innerHTML = `<i class="fas fa-circle"></i> ${status}`;
}

function updateSummaryCards(data) {
    const portfolio = data.portfolio;
    
    // Total Capital
    document.getElementById('total-capital').textContent = 
        formatCurrency(portfolio.capital.total_value);
    
    const returnPct = portfolio.capital.total_return_pct;
    const returnElement = document.getElementById('total-return');
    returnElement.textContent = formatPercent(returnPct);
    returnElement.className = `metric-change ${returnPct >= 0 ? 'positive' : 'negative'}`;
    
    // Positions
    document.getElementById('position-count').textContent = portfolio.positions.count;
    document.getElementById('swing-count').textContent = portfolio.positions.swing;
    document.getElementById('intraday-count').textContent = portfolio.positions.intraday;
    
    // Performance
    document.getElementById('win-rate').textContent = 
        formatPercent(portfolio.performance.win_rate);
    document.getElementById('win-count').textContent = portfolio.performance.winning_trades;
    document.getElementById('loss-count').textContent = portfolio.performance.losing_trades;
    
    // P&L
    const pnl = portfolio.performance.total_realized_pnl;
    const pnlElement = document.getElementById('total-pnl');
    pnlElement.textContent = formatCurrency(pnl);
    pnlElement.className = `metric-large ${pnl >= 0 ? 'text-success' : 'text-danger'}`;
    
    document.getElementById('max-drawdown').textContent = 
        formatPercent(portfolio.performance.max_drawdown);
}

function updateMarketContext(context) {
    // Sentiment Score
    const sentiment = context.sentiment_score || 50;
    document.getElementById('sentiment-score').textContent = `${sentiment.toFixed(0)} / 100`;
    document.getElementById('sentiment-indicator').style.width = `${sentiment}%`;
    
    // Market Status
    const marketStatus = context.market_open ? 'OPEN' : 'CLOSED';
    document.getElementById('market-status').textContent = marketStatus;
}

function updatePositionsTable(positions) {
    const tbody = document.getElementById('positions-tbody');
    
    if (!positions || positions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">No open positions</td></tr>';
        return;
    }
    
    tbody.innerHTML = positions.map(pos => {
        const pnlClass = pos.unrealized_pnl >= 0 ? 'text-success' : 'text-danger';
        
        return `
            <tr>
                <td><strong>${pos.symbol}</strong></td>
                <td><span class="badge badge-info">${pos.position_type}</span></td>
                <td>${formatDate(pos.entry_date)}</td>
                <td>${formatCurrency(pos.entry_price)}</td>
                <td>${formatCurrency(pos.current_price)}</td>
                <td>${pos.shares.toLocaleString()}</td>
                <td class="${pnlClass}">${formatCurrency(pos.unrealized_pnl)}</td>
                <td class="${pnlClass}">${formatPercent(pos.unrealized_pnl_pct)}</td>
                <td>${formatCurrency(pos.trailing_stop)}</td>
                <td>${pos.target_exit_date ? formatDate(pos.target_exit_date) : '--'}</td>
            </tr>
        `;
    }).join('');
}

function updateTradesTable(trades) {
    const tbody = document.getElementById('trades-tbody');
    
    if (!trades || trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">No closed trades</td></tr>';
        return;
    }
    
    tbody.innerHTML = trades.map(trade => {
        const pnlClass = trade.pnl >= 0 ? 'text-success' : 'text-danger';
        
        return `
            <tr>
                <td><strong>${trade.symbol}</strong></td>
                <td><span class="badge badge-info">${trade.position_type}</span></td>
                <td>${formatDate(trade.entry_date)}</td>
                <td>${formatDate(trade.exit_date)}</td>
                <td>${trade.holding_days}d</td>
                <td>${formatCurrency(trade.entry_price)}</td>
                <td>${formatCurrency(trade.exit_price)}</td>
                <td class="${pnlClass}">${formatCurrency(trade.pnl)}</td>
                <td class="${pnlClass}">${formatPercent(trade.pnl_pct)}</td>
                <td><span class="badge badge-warning">${trade.exit_reason}</span></td>
            </tr>
        `;
    }).join('');
}

function updateAlertsFeed(alerts) {
    const feed = document.getElementById('alerts-feed');
    
    if (!alerts || alerts.length === 0) {
        feed.innerHTML = `
            <div class="alert-item alert-info">
                <span class="alert-time">--:--:--</span>
                <span class="alert-message">No recent alerts</span>
            </div>
        `;
        return;
    }
    
    feed.innerHTML = alerts.map(alert => {
        const time = new Date(alert.timestamp).toLocaleTimeString();
        const severityClass = `alert-${alert.severity}`;
        
        return `
            <div class="alert-item ${severityClass}">
                <span class="alert-time">${time}</span>
                <strong>${alert.symbol || ''}</strong>
                <span class="alert-message">${alert.message}</span>
            </div>
        `;
    }).join('');
}

function updateIntradayStats(data) {
    if (!data.stats) return;
    
    const stats = data.stats;
    
    document.getElementById('rescan-count').textContent = stats.rescan_count || 0;
    
    // Update scheduler status
    const statusBadge = document.getElementById('intraday-status');
    if (data.scheduler_running) {
        statusBadge.textContent = 'Active';
        statusBadge.className = 'badge badge-success';
    } else {
        statusBadge.textContent = 'Inactive';
        statusBadge.className = 'badge badge-danger';
    }
    
    // Update opportunities
    updateOpportunities(data.opportunities);
}

function updateOpportunities(opportunities) {
    const container = document.getElementById('opportunities-list');
    
    if (!opportunities || opportunities.length === 0) {
        container.innerHTML = '<p class="text-center">No opportunities detected</p>';
        return;
    }
    
    container.innerHTML = opportunities.map(opp => {
        return `
            <div class="opportunity-item">
                <div class="opportunity-header">
                    <span class="opportunity-symbol">${opp.symbol}</span>
                    <span class="opportunity-strength">Strength: ${opp.highest_strength.toFixed(1)}</span>
                </div>
                <div class="opportunity-details">
                    Signals: ${opp.signals.length} | 
                    First Detected: ${formatDateTime(opp.first_detected)}
                </div>
            </div>
        `;
    }).join('');
}

// ============================================================================
// CHARTS
// ============================================================================

function initializeCharts() {
    // Cumulative Returns Chart
    const returnsCtx = document.getElementById('returns-chart').getContext('2d');
    CONFIG.charts.returns = new Chart(returnsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Cumulative Return %',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
    
    // Daily P&L Chart
    const pnlCtx = document.getElementById('pnl-chart').getContext('2d');
    CONFIG.charts.pnl = new Chart(pnlCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Daily P&L',
                data: [],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    return value >= 0 ? '#10b981' : '#ef4444';
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function updatePerformanceCharts(data) {
    // Update Returns Chart
    if (data.cumulative_returns && data.cumulative_returns.length > 0) {
        const labels = data.cumulative_returns.map(r => r.date);
        const values = data.cumulative_returns.map(r => r.return_pct);
        
        CONFIG.charts.returns.data.labels = labels;
        CONFIG.charts.returns.data.datasets[0].data = values;
        CONFIG.charts.returns.update();
    }
    
    // Update P&L Chart
    if (data.daily_pnl) {
        const dates = Object.keys(data.daily_pnl).sort();
        const pnls = dates.map(date => data.daily_pnl[date]);
        
        CONFIG.charts.pnl.data.labels = dates;
        CONFIG.charts.pnl.data.datasets[0].data = pnls;
        CONFIG.charts.pnl.update();
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatCurrency(value) {
    if (value === null || value === undefined) return '--';
    const sign = value >= 0 ? '' : '';
    return sign + '$' + Math.abs(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatPercent(value) {
    if (value === null || value === undefined) return '--';
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(2) + '%';
}

function formatDate(dateString) {
    if (!dateString) return '--';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return '--';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================================================
// EXPORTS (for manual refresh buttons)
// ============================================================================

window.refreshPositions = refreshPositions;
window.refreshTrades = refreshTrades;
window.refreshAll = refreshAll;
