// Error handling for missing data - Fixed version
function handleDataError(error, context) {
    // Only log to console, don't show popups for every error
    console.warn(`Data issue in ${context}:`, error.message || error);
    
    // Only show user message for critical errors, not health checks
    if (context === 'critical' || (error.message && error.message.includes('Real data not available'))) {
        const errorMessages = {
            'price': 'Unable to fetch current price. Please check market hours and connection.',
            'historical': 'Historical data unavailable. Please try again later.',
            'prediction': 'Cannot generate prediction without real market data.',
            'training': 'Training requires real historical data. Please ensure market data is accessible.'
        };
        
        const message = errorMessages[context] || 'Unable to fetch required data. Please try again.';
        
        // Show user-friendly error only for critical issues
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = 'background: #ff4444; color: white; padding: 15px; border-radius: 5px; margin: 10px 0;';
        errorDiv.innerHTML = `<strong>Error:</strong> ${message}`;
        
        const container = document.querySelector('.main-content') || document.querySelector('.container') || document.body;
        if (container && container.querySelector) {
            container.insertBefore(errorDiv, container.firstChild);
            setTimeout(() => errorDiv.remove(), 10000);
        }
    }
}

// Don't override fetch globally - it causes too many issues
// Only handle critical errors
window.handleCriticalError = handleDataError;
