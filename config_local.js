// Local development configuration for testing
window.CONFIG = {
    // Use local backend for development
    BACKEND_URL: 'http://localhost:8000',
    
    // Fallback to Render backend if local is not available
    RENDER_BACKEND_URL: 'https://enhanced-global-stock-tracker-frontend.onrender.com',
    
    // Frontend URL
    FRONTEND_URL: window.location.origin,
    
    // Refresh interval (5 minutes)
    REFRESH_INTERVAL: 300000,
    
    // Debug mode
    DEBUG: true,
    
    // API endpoints
    API_ENDPOINTS: {
        // Stock data
        STOCK_DATA: '/api/stock',
        SYMBOLS: '/api/symbols',
        
        // Unified prediction (Phase 3 & 4)
        UNIFIED_PREDICTION: '/api/unified-prediction',
        PREDICTION_STATUS: '/api/prediction-status',
        PERFORMANCE_METRICS: '/api/performance-metrics',
        
        // Phase 4 specific
        GNN_PREDICTION: '/api/phase4-gnn-prediction',
        MULTIMODAL_PREDICTION: '/api/phase4-multimodal-prediction',
        
        // CBA specific
        CBA_PUBLICATIONS: '/api/prediction/cba/publications',
        CBA_NEWS: '/api/prediction/cba/news',
        CBA_ENHANCED: '/api/prediction/cba/enhanced',
        CBA_BANKING: '/api/prediction/cba/banking-sector'
    }
};

// Helper function to get the appropriate backend URL
window.getBackendUrl = function() {
    // Try local first
    return window.CONFIG.BACKEND_URL;
};

// Helper function to build API URL
window.buildApiUrl = function(endpoint, params = {}) {
    const baseUrl = window.getBackendUrl();
    const url = new URL(baseUrl + endpoint);
    
    // Add query parameters
    Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
            url.searchParams.append(key, params[key]);
        }
    });
    
    return url.toString();
};

console.log('🔧 Local configuration loaded');
console.log('📡 Backend URL:', window.CONFIG.BACKEND_URL);
console.log('🌐 Frontend URL:', window.CONFIG.FRONTEND_URL);