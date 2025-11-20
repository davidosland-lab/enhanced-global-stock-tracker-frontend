// Event Risk Guard Dashboard - JavaScript

// Global state
let currentConfig = {};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    refreshDashboard();
    loadModels();
    loadLogs();
    
    // Auto-refresh every 30 seconds
    setInterval(refreshDashboard, 30000);
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
        const summaryContent = document.getElementById('pipeline-summary-content');
        const factorContent = document.getElementById('factor-view-content');

        // Latest report
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

        // Pipeline summary
        if (data.latest_state && data.latest_state.summary && summaryContent) {
            const summary = data.latest_state.summary;
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
        } else if (summaryContent) {
            summaryContent.innerHTML = '<p class="text-muted">No pipeline summary available</p>';
        }

        // Factor View & risk mode
        if (factorContent) {
            const state = data.latest_state || {};
            const fv = state.factor_view || {};
            const fvSummary = fv.summary || {};
            const overall = fvSummary.overall || {};
            const sectorAvg = fvSummary.sector_avg_opportunity || {};
            const betaXBySector = fvSummary.beta_xjo_by_sector || {};
            const betaLBySector = fvSummary.beta_lithium_by_sector || {};

            if (!Object.keys(sectorAvg).length && !Object.keys(overall).length) {
                factorContent.innerHTML = `
                    <p class="text-muted">
                        Run the overnight screener to generate factor data
                        (sector averages and macro betas).
                    </p>
                `;
            } else {
                const risk = getRiskMode(overall);

                const sectorRows = Object.keys(sectorAvg).map(sector => {
                    const avg = sectorAvg[sector] || 0;
                    const bx  = betaXBySector[sector] || 0;
                    const bl  = betaLBySector[sector] || 0;
                    return { sector, avg, bx, bl };
                }).sort((a, b) => b.avg - a.avg);

                const topSectors = sectorRows.slice(0, 6);

                const rowsHtml = topSectors.length
                    ? topSectors.map(row => `
                        <tr>
                            <td>${row.sector}</td>
                            <td>${row.avg.toFixed(1)}</td>
                            <td>${row.bx.toFixed(2)}</td>
                            <td>${row.bl.toFixed(2)}</td>
                        </tr>
                      `).join('')
                    : '<tr><td colspan="4" class="text-muted">No sector data available</td></tr>';

                factorContent.innerHTML = `
                    <div class="factor-risk-mode">
                        <div class="risk-badge risk-${risk.level.toLowerCase()}">
                            Risk mode: <strong>${risk.level}</strong>
                        </div>
                        <p class="risk-description">${risk.description}</p>
                    </div>
                    <div class="factor-overall">
                        <div class="summary-grid">
                            <div class="summary-item">
                                <div class="summary-label">Avg Opportunity Score</div>
                                <div class="summary-value">
                                    ${(overall.avg_opportunity_score || 0).toFixed(1)}
                                </div>
                            </div>
                            <div class="summary-item">
                                <div class="summary-label">Avg Market Beta (XJO)</div>
                                <div class="summary-value">
                                    ${(overall.avg_beta_xjo || 0).toFixed(2)}
                                </div>
                            </div>
                            <div class="summary-item">
                                <div class="summary-label">Avg Lithium Beta</div>
                                <div class="summary-value">
                                    ${(overall.avg_beta_lithium || 0).toFixed(2)}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="factor-table-wrapper">
                        <h4>Top Sectors by Opportunity</h4>
                        <table class="opportunities-table factor-table">
                            <thead>
                                <tr>
                                    <th>Sector</th>
                                    <th>Avg Score</th>
                                    <th>β XJO</th>
                                    <th>β Lithium</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                `;
            }
        }

    } catch (error) {
        console.error('Error loading latest report:', error);
        const factorContent = document.getElementById('factor-view-content');
        if (factorContent) {
            factorContent.innerHTML = '<p class="text-error">Failed to load factor view.</p>';
        }
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
                tbody.innerHTML = opportunities.map((opp, index) => {
                    const symbol = opp.symbol || 'N/A';
                    const name = opp.name || symbol;
                    const score = (opp.opportunity_score || 0).toFixed(1);
                    const confidence = (opp.confidence || 0).toFixed(1);
                    const sector = opp.sector || 'N/A';
                    const signal = (opp.signal || 'HOLD').toUpperCase();

                    const betaX = opp.beta_xjo != null ? opp.beta_xjo :
                        (opp.macro_betas && opp.macro_betas.xjo);
                    const betaLi = opp.beta_lithium != null ? opp.beta_lithium :
                        (opp.macro_betas && opp.macro_betas.lithium);

                    const betaXClass = classifyBeta(betaX);
                    const betaLiClass = classifyBeta(betaLi);

                    const trendX = classifyBetaTrend(betaX);
                    const trendLi = classifyBetaTrend(betaLi);

                    const betaXHtml = (betaX != null)
                        ? `<span class="beta-badge ${betaXClass}">
                               <span class="beta-label">βXJO</span>
                               <span class="beta-value">${betaX.toFixed(2)}</span>
                               <span class="beta-trend ${trendX.cls}">${trendX.arrow}</span>
                           </span>`
                        : `<span class="beta-badge beta-none">
                               <span class="beta-label">βXJO</span>
                               <span class="beta-value">n/a</span>
                           </span>`;

                    const betaLiHtml = (betaLi != null)
                        ? `<span class="beta-badge ${betaLiClass}">
                               <span class="beta-label">βLi</span>
                               <span class="beta-value">${betaLi.toFixed(2)}</span>
                               <span class="beta-trend ${trendLi.cls}">${trendLi.arrow}</span>
                           </span>`
                        : `<span class="beta-badge beta-none">
                               <span class="beta-label">βLi</span>
                               <span class="beta-value">n/a</span>
                           </span>`;

                    return `
                        <tr>
                            <td><strong>${symbol}</strong><br><span class="symbol-name">${name}</span></td>
                            <td>
                                <span class="score-badge ${getScoreClass(opp.opportunity_score)}">
                                    ${score}
                                </span>
                            </td>
                            <td>
                                <span class="signal-badge signal-${signal.toLowerCase()}">
                                    ${signal}
                                </span>
                            </td>
                            <td>${confidence}%</td>
                            <td>${sector}</td>
                            <td>
                                <div class="beta-badges">
                                    ${betaXHtml}
                                    ${betaLiHtml}
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="6" class="text-muted">No opportunities available</td></tr>';
            }
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-muted">No data available</td></tr>';
        }
    } catch (error) {
        console.error('Error loading opportunities:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted">Error loading data</td></tr>';
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

function classifyBeta(beta) {
    if (beta == null || isNaN(beta)) return "beta-none";

    const b = Math.abs(beta);

    if (b < 0.6) return "beta-low";       // defensive
    if (b < 1.0) return "beta-normal";    // neutral
    if (b < 1.3) return "beta-elevated";  // sensitive
    return "beta-high";                   // volatile
}

// Determine arrow direction for beta relative to neutral (1.0)
function classifyBetaTrend(beta) {
    if (beta == null || isNaN(beta)) return { arrow: "→", cls: "trend-flat" };

    if (beta < 0.9) return { arrow: "↓", cls: "trend-down" };
    if (beta > 1.1) return { arrow: "↑", cls: "trend-up" };
    return { arrow: "→", cls: "trend-flat" };
}

// Simple risk mode classification based on average betas
function getRiskMode(overall) {
    const avgX = overall.avg_beta_xjo || 0;
    const avgLi = overall.avg_beta_lithium || 0;

    let level = "Normal";
    let description = "Balanced exposure to market and lithium factors.";

    if (avgX < 0.9 && avgLi < 0.5) {
        level = "Low";
        description = "Portfolio tilted to lower beta names; less sensitive to broad swings.";
    } else if ((avgX >= 0.9 && avgX < 1.1) && (avgLi >= 0.5 && avgLi < 0.9)) {
        level = "Normal";
        description = "Typical beta profile; moves broadly with the market.";
    } else if (avgX >= 1.1 || avgLi >= 0.9) {
        level = "Elevated";
        description = "Heightened sensitivity to market or lithium; expect amplified moves.";
    }
    if (avgX >= 1.3 || avgLi >= 1.2) {
        level = "High";
        description = "Portfolio is strongly pro-cyclical vs these factors; consider hedging or de-risking.";
    }

    return { level, description, avgX, avgLi };
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
