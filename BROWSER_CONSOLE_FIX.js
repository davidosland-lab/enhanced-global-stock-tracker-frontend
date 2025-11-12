// ============================================
// BROWSER CONSOLE FIX FOR ML PREDICTIONS
// ============================================
// Copy and paste this entire code into your browser console
// while on the Stock Analysis page to fix the ML predictions

console.log('Applying ML Predictions Fix...');

// Override the broken fetchPredictions function
window.fetchPredictions = async function() {
    console.log('Using FIXED fetchPredictions function');
    
    const symbol = document.getElementById('symbol').value.toUpperCase();
    
    if (!symbol) {
        alert('Please enter a symbol');
        return;
    }
    
    // Show loading status
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.className = 'status-message loading';
        statusDiv.textContent = 'Generating ML predictions... This may take a moment.';
        statusDiv.style.display = 'block';
    }
    
    // Switch to predictions tab WITHOUT using event
    const predictionsTab = Array.from(document.querySelectorAll('.tab')).find(
        tab => tab.textContent.includes('ML Predictions')
    );
    if (predictionsTab) {
        // Remove active from all tabs
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        predictionsTab.classList.add('active');
        
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Show predictions tab
        const predictionsContent = document.getElementById('predictions-tab');
        if (predictionsContent) {
            predictionsContent.classList.add('active');
        }
    }
    
    try {
        console.log(`Fetching predictions for ${symbol}...`);
        const response = await fetch(`/api/predict/${symbol}`);
        const data = await response.json();
        console.log('ML Response:', data);
        
        if (response.ok) {
            if (data.available) {
                // Show success
                if (statusDiv) {
                    statusDiv.className = 'status-message success';
                    statusDiv.textContent = '✓ Predictions generated successfully!';
                    setTimeout(() => {
                        statusDiv.style.display = 'none';
                    }, 3000);
                }
                
                // Display predictions
                const predictionsDiv = document.getElementById('predictions-content');
                if (predictionsDiv && data.predictions) {
                    let html = '<div style="margin-top: 20px;">';
                    html += `<p style="margin-bottom: 15px;">Current Price: <strong>$${data.current_price.toFixed(2)}</strong></p>`;
                    html += '<h4>Price Predictions</h4>';
                    
                    data.predictions.forEach(pred => {
                        const changeClass = pred.return >= 0 ? 'positive' : 'negative';
                        const symbol = pred.return >= 0 ? '+' : '';
                        
                        html += `
                            <div class="prediction-item">
                                <div><strong>${pred.days} Day${pred.days > 1 ? 's' : ''}</strong></div>
                                <div><span class="${changeClass}">$${pred.price.toFixed(2)}</span></div>
                                <div>
                                    <span class="${changeClass}">${symbol}${pred.return.toFixed(2)}%</span>
                                    <br><small>Confidence: ${pred.confidence}%</small>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    predictionsDiv.innerHTML = html;
                }
                
                console.log('✅ ML Predictions displayed successfully!');
            } else {
                // ML not available
                if (statusDiv) {
                    statusDiv.className = 'status-message error';
                    statusDiv.textContent = data.error || 'ML predictions not available';
                }
                console.error('ML not available:', data.error);
            }
        } else {
            // Error response
            if (statusDiv) {
                statusDiv.className = 'status-message error';
                statusDiv.textContent = data.error || 'Failed to generate predictions';
            }
            console.error('ML prediction failed:', data);
        }
    } catch (error) {
        console.error('Network error:', error);
        if (statusDiv) {
            statusDiv.className = 'status-message error';
            statusDiv.textContent = 'Network error: ' + error.message;
        }
    }
};

console.log('✅ ML Predictions Fix Applied!');
console.log('You can now click the "ML Predictions" button and it should work.');
console.log('First click "Get Data" to load stock data, then "ML Predictions".');

// Also fix the switchTab function
window.switchTab = function(event, tab) {
    // Handle both with and without event
    if (typeof event === 'string') {
        tab = event;
        event = null;
    }
    
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        // Find and activate the right tab
        document.querySelectorAll('.tab').forEach(t => {
            if (t.textContent.toLowerCase().includes(tab.toLowerCase()) ||
                (tab === 'predictions' && t.textContent.includes('ML'))) {
                t.classList.add('active');
            }
        });
    }
    
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const tabContent = document.getElementById(`${tab}-tab`);
    if (tabContent) {
        tabContent.classList.add('active');
    }
};

console.log('✅ Tab switching also fixed!');

// Test that the fix is working
if (document.getElementById('symbol')) {
    console.log('Ready to use! Symbol input found.');
    console.log('Current symbol:', document.getElementById('symbol').value);
}