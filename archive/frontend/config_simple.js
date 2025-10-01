// Simple configuration with direct URL
window.APP_CONFIG = {
    // Direct API Backend URL for this specific sandbox
    API_BASE_URL: 'https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
    
    // API Endpoints
    ENDPOINTS: {
        health: '/health',
        unifiedPrediction: '/api/unified-prediction',
        technicalAnalysis: '/api/technical/analysis',
        stockData: '/api/stock',
        cbaEnhanced: '/api/prediction/cba/enhanced',
        dashboard: '/api/dashboard/comprehensive-data',
        indices: '/api/indices',
        backtest: '/api/backtest',
        trainModels: '/api/train-models'
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
console.log('🔧 App Configuration Loaded (Simple):', {
    API_URL: window.APP_CONFIG.API_BASE_URL,
    Host: window.location.hostname,
    Environment: 'E2B Sandbox'
});