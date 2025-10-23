// Global configuration for all frontend modules
window.APP_CONFIG = {
    // API Backend URL - automatically detects sandbox or local environment
    API_BASE_URL: (function() {
        // Check if we're in E2B sandbox
        const hostname = window.location.hostname;
        
        if (hostname.includes('e2b.dev')) {
            // We're in sandbox - replace the port number in the hostname
            // Format: 3000-sandboxid.e2b.dev -> 8000-sandboxid.e2b.dev
            const backendHost = hostname.replace(/^3000-/, '8000-');
            return `https://${backendHost}`;
        } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
            // Local development
            return 'http://localhost:8000';
        } else {
            // Fallback to current protocol and host on port 8000
            return `${window.location.protocol}//${window.location.hostname}:8000`;
        }
    })(),
    
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
console.log('🔧 App Configuration Loaded:', {
    API_URL: window.APP_CONFIG.API_BASE_URL,
    Host: window.location.hostname,
    Environment: window.location.hostname.includes('e2b.dev') ? 'E2B Sandbox' : 'Local'
});