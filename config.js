// Configuration for the frontend application
// Updated: 2025-01-25 - Using Render.com backend
window.CONFIG = {
    // Backend API URL - Render.com deployment (WORKING!)
    // DO NOT USE: enhanced-global-stock-tracker-frontend-production.up.railway.app (Railway deployment failed)
    BACKEND_URL: 'https://enhanced-global-stock-tracker-frontend.onrender.com',
    
    // Refresh interval in milliseconds (5 minutes)
    REFRESH_INTERVAL: 300000,
    
    // Enable debug logging
    DEBUG: false,
    
    // Frontend URL
    FRONTEND_URL: 'https://egsmtver110.netlify.app'
};

// Force cache bust for this configuration
console.log('Config loaded at:', new Date().toISOString());
console.log('Backend URL:', window.CONFIG.BACKEND_URL);