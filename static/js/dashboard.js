// Event Risk Guard Dashboard - JavaScript

// Global state
let currentConfig = {};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    refreshDashboard();
    loadModels();
    loadLogs();
    loadRegimeData();
    
    // Auto-refresh every 30 seconds
    setInterval(refreshDashboard, 30000);
    // Auto-refresh regime data every 60 seconds
    setInterval(loadRegimeData, 60000);
});

// Refresh dashboard data
async function refreshDashboard() {
    console.log('Refreshing dashboard...');
    await Promise.all([
        loadStatus(),
        loadLatestReport(),
        loadOpportunities()
    ]);
}

// Load system status
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update status cards
        document.getElementById('status-text').textContent = 
            data.system_active ? 'Active' : 'Inactive';
        
        document.getElementById('email-text').textContent = 
            data.email_enabled ? 'Enabled' : 'Disabled';
        
        document.getElementById('lstm-text').textContent = 
            data.lstm_training_enabled ? 'Enabled' : 'Disabled';
        
        document.getElementById('spi-text').textContent = 
            data.spi_monitoring_enabled ? 'Enabled' : 'Disabled';
        
        // Update icon colors
        document.querySelector('#system-status .card-icon').textContent = 
            data.system_active ? '🟢' : '🔴';
        document.querySelector('#email-status .card-icon').textContent = 
            data.email_enabled ? '📧' : '📭';
        document.querySelector('#lstm-status .card-icon').textContent = 
            data.lstm_training_enabled ? '🤖' : '🔕';
        document.querySelector('#spi-status .card-icon').textContent = 
            data.spi_monitoring_enabled ? '📈' : '📉';
        
        console.log('Status loaded:', data);
    } catch (error) {
        console.error('Error loading status:', error);
        showError('Failed to load system status');
    }
}

// Load latest report
async function loadLatestReport() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const reportContent = document.getElementById('latest-report-content');
        
        if (data.latest_report) {
            const report = data.latest_report;
            reportContent.innerHTML = `
                <div class="report-info">
                    <p><strong>Date:</strong> ${report.date}</p>
                    <p><strong>File:</strong> ${report.filename}</p>
                    <p><strong>Size:</strong> ${formatBytes(report.size)}</p>
                    <p><strong>Modified:</strong> ${formatDate(report.modified)}</p>
                    <button class="btn btn-primary" onclick="viewReport('${report.filename}')">
                        📄 View Report
                    </button>
                </div>
            `;
        } else {
            reportContent.innerHTML = '<p class="text-muted">No reports available yet</p>';
        }
        
        // Load pipeline summary
        if (data.latest_state && data.latest_state.summary) {
            const summary = data.latest_state.summary;
            const summaryContent = document.getElementById('pipeline-summary-content');
            summaryContent.innerHTML = `
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-label">Stocks Scanned</div>
                        <div class="summary-value">${summary.total_stocks_scanned || 0}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Opportunities Found</div>
                        <div class="summary-value">${summary.opportunities_found || 0}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">SPI Sentiment</div>
                        <div class="summary-value">${(summary.spi_sentiment_score || 0).toFixed(1)}/100</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Market Bias</div>
                        <div class="summary-value">${summary.market_bias || 'N/A'}</div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading latest report:', error);
    }
}

// Load top opportunities
async function loadOpportunities() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const tbody = document.getElementById('opportunities-tbody');
        
        if (data.latest_state && data.latest_state.top_opportunities) {
            const opportunities = data.latest_state.top_opportunities.slice(0, 10);
            
            if (opportunities.length > 0) {
                tbody.innerHTML = opportunities.map(opp => `
                    <tr>
                        <td><strong>${opp.symbol || 'N/A'}</strong></td>
                        <td>
                            <span class="score-badge ${getScoreClass(opp.opportunity_score)}">
                                ${(opp.opportunity_score || 0).toFixed(1)}
                            </span>
                        </td>
                        <td>
                            <span class="signal-badge signal-${(opp.signal || 'hold').toLowerCase()}">
                                ${opp.signal || 'HOLD'}
                            </span>
                        </td>
                        <td>${(opp.confidence || 0).toFixed(1)}%</td>
                        <td>${opp.sector || 'N/A'}</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-muted">No opportunities available</td></tr>';
            }
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="text-muted">No data available</td></tr>';
        }
    } catch (error) {
        console.error('Error loading opportunities:', error);
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted">Error loading data</td></tr>';
    }
}

// Load trained models
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const models = await response.json();
        
        const modelsList = document.getElementById('models-list');
        
        if (models.length > 0) {
            modelsList.innerHTML = models.slice(0, 20).map(model => `
                <div class="model-item" title="${model.filename}">
                    ${model.symbol}
                </div>
            `).join('');
        } else {
            modelsList.innerHTML = '<p class="text-muted">No trained models yet</p>';
        }
    } catch (error) {
        console.error('Error loading models:', error);
        showError('Failed to load models');
    }
}

// Refresh models
function refreshModels() {
    loadModels();
}

// Load logs
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        const logsContent = document.getElementById('logs-content');
        
        if (data.logs && data.logs.length > 0) {
            logsContent.innerHTML = `<pre>${data.logs.join('')}</pre>`;
            // Auto-scroll to bottom
            logsContent.scrollTop = logsContent.scrollHeight;
        } else {
            logsContent.innerHTML = '<p class="text-muted">No logs available</p>';
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Refresh logs
function refreshLogs() {
    loadLogs();
}

// Show settings modal
async function showSettings() {
    try {
        const response = await fetch('/api/config');
        currentConfig = await response.json();
        
        // Populate settings form
        document.getElementById('email-enabled').checked = 
            currentConfig.email_notifications?.enabled || false;
        document.getElementById('smtp-server').value = 
            currentConfig.email_notifications?.smtp_server || '';
        document.getElementById('smtp-port').value = 
            currentConfig.email_notifications?.smtp_port || '';
        document.getElementById('smtp-username').value = 
            currentConfig.email_notifications?.smtp_username || '';
        document.getElementById('smtp-password').value = 
            currentConfig.email_notifications?.smtp_password || '';
        
        document.getElementById('lstm-enabled').checked = 
            currentConfig.lstm_training?.enabled || false;
        document.getElementById('max-models').value = 
            currentConfig.lstm_training?.max_models_per_night || '';
        
        document.getElementById('spi-enabled').checked = 
            currentConfig.spi_monitoring?.enabled || false;
        
        document.getElementById('settings-modal').classList.add('active');
    } catch (error) {
        console.error('Error loading settings:', error);
        showError('Failed to load settings');
    }
}

// Close settings modal
function closeSettings() {
    document.getElementById('settings-modal').classList.remove('active');
}

// Save settings
async function saveSettings() {
    try {
        const updatedConfig = {
            ...currentConfig,
            email_notifications: {
                ...currentConfig.email_notifications,
                enabled: document.getElementById('email-enabled').checked,
                smtp_server: document.getElementById('smtp-server').value,
                smtp_port: parseInt(document.getElementById('smtp-port').value),
                smtp_username: document.getElementById('smtp-username').value,
                smtp_password: document.getElementById('smtp-password').value
            },
            lstm_training: {
                ...currentConfig.lstm_training,
                enabled: document.getElementById('lstm-enabled').checked,
                max_models_per_night: parseInt(document.getElementById('max-models').value)
            },
            spi_monitoring: {
                ...currentConfig.spi_monitoring,
                enabled: document.getElementById('spi-enabled').checked
            }
        };
        
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedConfig)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Settings saved successfully');
            closeSettings();
            refreshDashboard();
        } else {
            showError('Failed to save settings: ' + result.message);
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Failed to save settings');
    }
}

// Test email
async function testEmail() {
    try {
        showSuccess('Sending test email...');
        const response = await fetch('/api/test-email', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Test email sent successfully! Check your inbox.');
        } else {
            showError('Failed to send test email: ' + result.message);
        }
    } catch (error) {
        console.error('Error sending test email:', error);
        showError('Failed to send test email');
    }
}

// View all reports
async function viewAllReports() {
    try {
        const response = await fetch('/api/reports');
        const reports = await response.json();
        
        const reportsList = document.getElementById('reports-list');
        
        if (reports.length > 0) {
            reportsList.innerHTML = reports.map(report => `
                <div class="report-item" onclick="viewReport('${report.filename}')">
                    <div class="report-date">${report.date}</div>
                    <div class="report-meta">
                        ${report.filename} • ${formatBytes(report.size)} • ${formatDate(report.modified)}
                    </div>
                </div>
            `).join('');
        } else {
            reportsList.innerHTML = '<p class="text-muted">No reports available</p>';
        }
        
        document.getElementById('reports-modal').classList.add('active');
    } catch (error) {
        console.error('Error loading reports:', error);
        showError('Failed to load reports');
    }
}

// Close reports modal
function closeReports() {
    document.getElementById('reports-modal').classList.remove('active');
}

// View specific report
function viewReport(filename) {
    window.open(`/api/reports/${filename}`, '_blank');
}

// Utility functions
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('en-AU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getScoreClass(score) {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
}

function showSuccess(message) {
    alert('✅ ' + message);
}

function showError(message) {
    alert('❌ ' + message);
}

// Load market regime data
async function loadRegimeData() {
    try {
        const response = await fetch('/api/regime');
        const data = await response.json();
        
        const regimeSection = document.getElementById('regime-section');
        
        if (data.available && data.regime) {
            // Show regime section
            regimeSection.style.display = 'block';
            
            const regime = data.regime;
            
            // Regime names and colors mapping
            const regimeInfo = {
                'low_vol': { name: 'Low Volatility', icon: '🟢', color: '#10b981' },
                'medium_vol': { name: 'Medium Volatility', icon: '🟡', color: '#f59e0b' },
                'high_vol': { name: 'High Volatility', icon: '🔴', color: '#ef4444' }
            };
            
            const currentRegime = regimeInfo[regime.regime_label] || 
                { name: regime.regime_label, icon: '⚪', color: '#6b7280' };
            
            // Update regime name
            const regimeNameEl = document.getElementById('regime-name');
            regimeNameEl.textContent = currentRegime.name;
            regimeNameEl.style.color = currentRegime.color;
            
            const regimeIconEl = document.querySelector('.regime-icon');
            regimeIconEl.textContent = currentRegime.icon;
            
            // Update crash risk
            const crashRisk = (regime.crash_risk_score || 0) * 100;
            document.getElementById('crash-risk-value').textContent = crashRisk.toFixed(1) + '%';
            
            // Determine risk level and badge
            let riskLevel, riskClass;
            if (crashRisk >= 70) {
                riskLevel = 'CRITICAL RISK';
                riskClass = 'risk-critical';
            } else if (crashRisk >= 50) {
                riskLevel = 'HIGH RISK';
                riskClass = 'risk-high';
            } else if (crashRisk >= 30) {
                riskLevel = 'MODERATE RISK';
                riskClass = 'risk-moderate';
            } else {
                riskLevel = 'LOW RISK';
                riskClass = 'risk-low';
            }
            
            const badgeEl = document.getElementById('crash-risk-badge');
            badgeEl.textContent = riskLevel;
            badgeEl.className = 'regime-badge ' + riskClass;
            
            // Update volatility metrics
            const volDaily = (regime.vol_1d || 0) * 100;
            const volAnnual = (regime.vol_annual || 0) * 100;
            document.getElementById('regime-vol-daily').textContent = volDaily.toFixed(2) + '%';
            document.getElementById('regime-vol-annual').textContent = volAnnual.toFixed(2) + '%';
            
            // Update probability bars
            const probs = regime.regime_probabilities || {};
            for (let state = 0; state <= 2; state++) {
                const prob = (probs[state] || 0) * 100;
                const barEl = document.getElementById(`prob-bar-${state}`);
                const valueEl = document.getElementById(`prob-value-${state}`);
                
                if (barEl && valueEl) {
                    barEl.style.width = prob.toFixed(1) + '%';
                    valueEl.textContent = prob.toFixed(2) + '%';
                }
            }
            
            // Update data window
            const dataWindow = regime.data_window || {};
            const windowText = `${dataWindow.start || 'N/A'} to ${dataWindow.end || 'N/A'}`;
            document.getElementById('regime-window').textContent = windowText;
            
            console.log('Regime data loaded:', regime);
        } else {
            // Hide regime section if no data available
            regimeSection.style.display = 'none';
            console.log('No regime data available');
        }
    } catch (error) {
        console.error('Error loading regime data:', error);
        // Don't show error to user, just hide the section
        document.getElementById('regime-section').style.display = 'none';
    }
}

// Refresh regime data manually
function refreshRegime() {
    loadRegimeData();
    showSuccess('Regime data refreshed');
}
