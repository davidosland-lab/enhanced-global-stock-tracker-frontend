/**
 * Paper Trading Platform JavaScript Functions
 * Add these functions to the <script> section of finbert_v4_enhanced_ui.html
 */

// Trading Platform Variables
let tradingAccount = null;
let tradingPositions = [];
let tradingTrades = [];

// Modal Functions
function openTradingModal() {
    document.getElementById('tradingModal').style.display = 'flex';
    loadTradingDashboard();
}

function closeTradingModal() {
    document.getElementById('tradingModal').style.display = 'none';
}

// Load Trading Dashboard
async function loadTradingDashboard() {
    try {
        // Load account summary
        await refreshTradingAccount();
        
        // Load positions
        await loadPositions();
        
        // Load recent trades
        await loadRecentTrades();
        
        // Load statistics
        await loadTradeStatistics();
        
        // Check if there's a current prediction to display
        if (currentSymbol && window.lastPrediction) {
            updateTradingPrediction(window.lastPrediction);
        }
    } catch (error) {
        console.error('Error loading trading dashboard:', error);
        showTradeMessage('Error loading dashboard: ' + error.message, 'error');
    }
}

// Account Management
async function refreshTradingAccount() {
    try {
        const response = await fetch(`${API_BASE}/api/trading/account`);
        const data = await response.json();
        
        if (data.success) {
            tradingAccount = data.account;
            updateAccountDisplay();
        } else {
            throw new Error(data.error || 'Failed to load account');
        }
    } catch (error) {
        console.error('Error loading account:', error);
        showTradeMessage('Error loading account: ' + error.message, 'error');
    }
}

function updateAccountDisplay() {
    if (!tradingAccount) return;
    
    document.getElementById('tradingTotalValue').textContent = 
        `$${tradingAccount.total_value.toFixed(2)}`;
    document.getElementById('tradingCashBalance').textContent = 
        `$${tradingAccount.cash_balance.toFixed(2)}`;
    
    const pnl = tradingAccount.total_pnl;
    const pnlPercent = tradingAccount.total_pnl_percent;
    const pnlColor = pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
    const pnlSign = pnl >= 0 ? '+' : '';
    
    document.getElementById('tradingTotalPnL').innerHTML = 
        `<span class="${pnlColor}">${pnlSign}$${pnl.toFixed(2)} (${pnlSign}${pnlPercent.toFixed(2)}%)</span>`;
    
    document.getElementById('tradingPositionCount').textContent = tradingPositions.length;
}

async function resetTradingAccount() {
    if (!confirm('Are you sure you want to reset your paper trading account? All positions and history will be lost.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/trading/account/reset`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        
        if (data.success) {
            showTradeMessage('Account reset successfully to $10,000', 'success');
            await loadTradingDashboard();
        } else {
            throw new Error(data.error || 'Failed to reset account');
        }
    } catch (error) {
        console.error('Error resetting account:', error);
        showTradeMessage('Error resetting account: ' + error.message, 'error');
    }
}

// Trade Execution
async function placeTrade(side) {
    const symbol = document.getElementById('tradeSymbol').value.trim().toUpperCase();
    const quantity = parseInt(document.getElementById('tradeQuantity').value);
    const orderType = document.getElementById('tradeOrderType').value;
    const price = parseFloat(document.getElementById('tradePrice').value);
    
    // Validation
    if (!symbol) {
        showTradeMessage('Please enter a symbol', 'error');
        return;
    }
    
    if (!quantity || quantity <= 0) {
        showTradeMessage('Please enter a valid quantity', 'error');
        return;
    }
    
    if ((orderType === 'LIMIT' || orderType === 'STOP') && (!price || price <= 0)) {
        showTradeMessage('Please enter a valid price', 'error');
        return;
    }
    
    try {
        const orderData = {
            symbol: symbol,
            side: side,
            quantity: quantity,
            order_type: orderType
        };
        
        if (orderType === 'LIMIT') {
            orderData.limit_price = price;
        } else if (orderType === 'STOP') {
            orderData.stop_price = price;
        }
        
        const response = await fetch(`${API_BASE}/api/trading/orders`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(orderData)
        });
        const data = await response.json();
        
        if (data.success) {
            const orderTypeText = orderType === 'MARKET' ? 'Market' : 
                                 orderType === 'LIMIT' ? 'Limit' : 'Stop';
            const priceText = orderType === 'MARKET' ? 
                            `@ $${data.price.toFixed(2)}` :
                            `@ $${price.toFixed(2)} (pending)`;
            
            showTradeMessage(
                `✅ ${orderTypeText} order placed: ${side} ${quantity} ${symbol} ${priceText}`,
                'success'
            );
            
            // Clear form
            document.getElementById('tradeSymbol').value = '';
            document.getElementById('tradeQuantity').value = '';
            
            // Refresh data
            await refreshTradingAccount();
            await loadPositions();
            await loadRecentTrades();
        } else {
            throw new Error(data.error || 'Failed to place order');
        }
    } catch (error) {
        console.error('Error placing trade:', error);
        showTradeMessage('❌ Error placing trade: ' + error.message, 'error');
    }
}

// Position Management
async function loadPositions() {
    try {
        const response = await fetch(`${API_BASE}/api/trading/positions`);
        const data = await response.json();
        
        if (data.success) {
            tradingPositions = data.positions;
            displayPositions();
        } else {
            throw new Error(data.error || 'Failed to load positions');
        }
    } catch (error) {
        console.error('Error loading positions:', error);
        showTradeMessage('Error loading positions: ' + error.message, 'error');
    }
}

function displayPositions() {
    const container = document.getElementById('positionsContainer');
    
    if (tradingPositions.length === 0) {
        container.innerHTML = '<div class="text-center text-gray-400 py-8">No open positions</div>';
        return;
    }
    
    let html = '';
    tradingPositions.forEach(pos => {
        const pnlColor = pos.unrealized_pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
        const pnlSign = pos.unrealized_pnl >= 0 ? '+' : '';
        
        html += `
            <div class="position-row">
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <div class="font-bold text-lg mb-1">${pos.symbol}</div>
                        <div class="text-sm text-gray-400">
                            ${pos.quantity} shares @ $${pos.avg_cost.toFixed(2)} avg
                        </div>
                    </div>
                    <div class="flex-1 text-center">
                        <div class="text-sm text-gray-400">Current Price</div>
                        <div class="font-bold">$${pos.current_price ? pos.current_price.toFixed(2) : 'N/A'}</div>
                    </div>
                    <div class="flex-1 text-center">
                        <div class="text-sm text-gray-400">Market Value</div>
                        <div class="font-bold">$${pos.market_value ? pos.market_value.toFixed(2) : 'N/A'}</div>
                    </div>
                    <div class="flex-1 text-center">
                        <div class="text-sm text-gray-400">P&L</div>
                        <div class="${pnlColor}">
                            ${pnlSign}$${pos.unrealized_pnl ? pos.unrealized_pnl.toFixed(2) : '0.00'}
                            (${pnlSign}${pos.unrealized_pnl_percent ? pos.unrealized_pnl_percent.toFixed(2) : '0.00'}%)
                        </div>
                    </div>
                    <div>
                        <button onclick="closePosition('${pos.symbol}')" class="px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm transition">
                            <i class="fas fa-times mr-1"></i> Close
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

async function closePosition(symbol) {
    if (!confirm(`Close entire position in ${symbol}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/trading/positions/${symbol}/close`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        
        if (data.success) {
            const pnl = data.pnl || 0;
            const pnlSign = pnl >= 0 ? '+' : '';
            showTradeMessage(
                `✅ Position closed: ${symbol} - P&L: ${pnlSign}$${pnl.toFixed(2)}`,
                'success'
            );
            
            await refreshTradingAccount();
            await loadPositions();
            await loadRecentTrades();
        } else {
            throw new Error(data.error || 'Failed to close position');
        }
    } catch (error) {
        console.error('Error closing position:', error);
        showTradeMessage('❌ Error closing position: ' + error.message, 'error');
    }
}

// Trade History
async function loadRecentTrades() {
    try {
        const response = await fetch(`${API_BASE}/api/trading/trades?limit=10`);
        const data = await response.json();
        
        if (data.success) {
            tradingTrades = data.trades;
            displayTrades();
        } else {
            throw new Error(data.error || 'Failed to load trades');
        }
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

function displayTrades() {
    const container = document.getElementById('tradesContainer');
    
    if (tradingTrades.length === 0) {
        container.innerHTML = '<div class="text-center text-gray-400 py-8">No trades yet</div>';
        return;
    }
    
    let html = '<div class="space-y-2">';
    tradingTrades.forEach(trade => {
        const date = new Date(trade.entry_date);
        const dateStr = date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        const statusColor = trade.status === 'OPEN' ? 'text-blue-400' : 'text-gray-400';
        const pnlColor = trade.pnl && trade.pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
        
        html += `
            <div class="position-row flex items-center justify-between text-sm">
                <span class="font-medium">${trade.symbol}</span>
                <span class="${trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'}">${trade.side}</span>
                <span>${trade.quantity}</span>
                <span>$${trade.entry_price.toFixed(2)}</span>
                <span class="${statusColor}">${trade.status}</span>
                ${trade.pnl !== null ? 
                    `<span class="${pnlColor}">${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}</span>` : 
                    '<span class="text-gray-500">-</span>'
                }
                <span class="text-gray-500">${dateStr}</span>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Statistics
async function loadTradeStatistics() {
    try {
        const response = await fetch(`${API_BASE}/api/trading/trades/stats`);
        const data = await response.json();
        
        if (data.success) {
            const stats = data.statistics;
            document.getElementById('statTotalTrades').textContent = stats.total_trades;
            document.getElementById('statWinRate').textContent = `${stats.win_rate.toFixed(1)}%`;
            document.getElementById('statProfitFactor').textContent = stats.profit_factor.toFixed(2);
            document.getElementById('statAvgPnL').textContent = `$${stats.avg_pnl.toFixed(2)}`;
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// FinBERT Integration
function updateTradingPrediction(prediction) {
    if (!prediction) return;
    
    document.getElementById('tradingPredictionPanel').style.display = 'none';
    document.getElementById('tradingPredictionData').style.display = 'block';
    
    document.getElementById('predSymbol').textContent = currentSymbol || '-';
    
    const badge = document.getElementById('predSignal');
    badge.textContent = prediction.prediction;
    badge.className = `prediction-badge prediction-${prediction.prediction}`;
    
    document.getElementById('predConfidence').textContent = `${Math.round(prediction.confidence)}%`;
    document.getElementById('predTarget').textContent = `$${prediction.predicted_price.toFixed(2)}`;
    
    // Store for trade execution
    window.lastPrediction = prediction;
}

function tradeFromPrediction() {
    if (!window.lastPrediction || !currentSymbol) {
        showTradeMessage('No prediction available', 'error');
        return;
    }
    
    const pred = window.lastPrediction;
    const side = pred.prediction === 'BUY' ? 'BUY' : pred.prediction === 'SELL' ? 'SELL' : null;
    
    if (!side) {
        showTradeMessage('Cannot trade HOLD signal', 'error');
        return;
    }
    
    // Pre-fill trade form
    document.getElementById('tradeSymbol').value = currentSymbol;
    document.getElementById('tradeQuantity').value = '10';
    document.getElementById('tradeOrderType').value = 'MARKET';
    
    // Auto-execute if high confidence
    if (pred.confidence >= 70) {
        if (confirm(`Execute ${side} order for ${currentSymbol} with ${Math.round(pred.confidence)}% confidence?`)) {
            placeTrade(side);
        }
    }
}

// Order Type Change Handler
document.getElementById('tradeOrderType')?.addEventListener('change', function() {
    const priceContainer = document.getElementById('tradePriceContainer');
    if (this.value === 'LIMIT' || this.value === 'STOP') {
        priceContainer.style.display = 'block';
    } else {
        priceContainer.style.display = 'none';
    }
});

// Message Display
function showTradeMessage(message, type) {
    const container = document.getElementById('tradeMessageContainer');
    const className = type === 'success' ? 'trade-success' : 'trade-error';
    const icon = type === 'success' ? 'check-circle' : 'exclamation-circle';
    
    container.innerHTML = `
        <div class="${className}">
            <i class="fas fa-${icon} mr-2"></i> ${message}
        </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

// Auto-refresh positions every 30 seconds
setInterval(() => {
    if (document.getElementById('tradingModal').style.display === 'flex') {
        loadPositions();
    }
}, 30000);
