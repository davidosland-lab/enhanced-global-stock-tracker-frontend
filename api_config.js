/**
 * API Configuration for Enhanced Global Stock Tracker
 * Handles both local development and production deployment
 */

function getAPIBaseURL() {
    // Check environment
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        // Local development
        return 'http://localhost:8000';
    } else if (hostname.includes('netlify') || hostname.includes('netlifyapp')) {
        // Netlify deployment - Check if backend exists, otherwise use mock
        // NOTE: Backend is NOT currently deployed!
        // TODO: Deploy backend on Render.com and update this URL
        console.warn('⚠️ Backend not deployed. Using frontend URL as fallback.');
        return window.location.origin;  // This will use mock API if available
    } else if (hostname.includes('github.io')) {
        // GitHub Pages deployment
        return window.location.origin;  // Use mock API
    } else {
        // Default fallback to current origin
        return window.location.origin;
    }
}

// Export for use in modules
const API_BASE_URL = getAPIBaseURL();

// Log configuration for debugging
console.log(`🌐 API Configuration:
- Environment: ${window.location.hostname}
- API Base URL: ${API_BASE_URL}
- Time: ${new Date().toISOString()}`);

// Make available globally
window.API_CONFIG = {
    BASE_URL: API_BASE_URL,
    ENDPOINTS: {
        // Stock Data
        STOCK_DATA: (symbol, period = '1d', interval = '5m') => 
            `${API_BASE_URL}/api/stock/${symbol}?period=${period}&interval=${interval}`,
        
        // Technical Analysis
        TECHNICAL_ANALYSIS: (symbol) => 
            `${API_BASE_URL}/api/technical/analysis/${symbol}`,
        TECHNICAL_CANDLESTICK: (symbol, period = '1mo', interval = '1d') =>
            `${API_BASE_URL}/api/technical/candlestick-data/${symbol}?period=${period}&interval=${interval}`,
        TECHNICAL_RSI: (symbol) => 
            `${API_BASE_URL}/api/technical/indicators/rsi/${symbol}`,
        TECHNICAL_MACD: (symbol) => 
            `${API_BASE_URL}/api/technical/indicators/macd/${symbol}`,
        TECHNICAL_BOLLINGER: (symbol) => 
            `${API_BASE_URL}/api/technical/indicators/bollinger/${symbol}`,
        TECHNICAL_SIGNALS: (symbol) => 
            `${API_BASE_URL}/api/technical/signals/${symbol}`,
        
        // Predictions
        UNIFIED_PREDICTION: (symbol, timeframe = '5d') => 
            `${API_BASE_URL}/api/unified-prediction/${symbol}?timeframe=${timeframe}`,
        GNN_PREDICTION: (symbol) => 
            `${API_BASE_URL}/api/phase4-gnn-prediction/${symbol}`,
        PHASE3_PREDICTION: (symbol, timeframe = '5d') => 
            `${API_BASE_URL}/api/extended-phase3-prediction/${symbol}?timeframe=${timeframe}&enable_advanced_features=true`,
        
        // Dashboard
        DASHBOARD_DATA: (timeframe = '24h') => 
            `${API_BASE_URL}/api/dashboard/comprehensive-data?timeframe=${timeframe}`,
        DASHBOARD_METRICS: (metric_type = 'accuracy') => 
            `${API_BASE_URL}/api/dashboard/metrics/${metric_type}`,
        DASHBOARD_PERFORMANCE: () => 
            `${API_BASE_URL}/api/dashboard/performance-summary`,
        
        // System
        HEALTH: () => `${API_BASE_URL}/api/health`,
        SYMBOLS: () => `${API_BASE_URL}/api/symbols`,
        
        // CBA Specific
        CBA_ENHANCED: () => `${API_BASE_URL}/api/cba/enhanced-prediction`,
        CBA_ANALYSIS: () => `${API_BASE_URL}/api/cba/comprehensive-analysis`
    }
};