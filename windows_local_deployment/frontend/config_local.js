// Local configuration for Windows deployment
window.APP_CONFIG = {
    // Local API Backend URL
    API_BASE_URL: 'http://localhost:8000',
    
    // API Endpoints
    ENDPOINTS: {
        health: '/health',
        unifiedPrediction: '/api/unified-prediction',
        technicalAnalysis: '/api/technical/analysis',
        backtest: '/api/backtest',
    },
    
    // Default settings
    DEFAULTS: {
        timeframe: '5d',
        symbol: 'AAPL'
    },
    
    // Feature flags
    FEATURES: {
        enableDebugMode: true,
        enableAutoRefresh: false,
        refreshInterval: 30000 // 30 seconds
    }
};

// Log configuration on load
console.log('🔧 Local Configuration Loaded:', {
    API_URL: window.APP_CONFIG.API_BASE_URL,
    Environment: 'Local Windows Deployment'
});