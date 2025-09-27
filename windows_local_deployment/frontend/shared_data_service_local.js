// Shared Data Service - Connects all modules
class SharedDataService {
    constructor() {
        this.API_BASE = 'http://localhost:8000';
        this.currentPrediction = null;
        this.predictionHistory = [];
        this.backtestResults = null;
        this.performanceMetrics = null;
        
        // Load from localStorage
        this.loadStoredData();
        
        // Event system for module communication
        this.listeners = {};
    }
    
    // Load stored data
    loadStoredData() {
        try {
            const stored = localStorage.getItem('sharedPredictionData');
            if (stored) {
                const data = JSON.parse(stored);
                this.currentPrediction = data.currentPrediction;
                this.predictionHistory = data.predictionHistory || [];
                this.backtestResults = data.backtestResults;
                this.performanceMetrics = data.performanceMetrics;
            }
        } catch (e) {
            console.error('Error loading stored data:', e);
        }
    }
    
    // Save data to localStorage
    saveData() {
        try {
            const data = {
                currentPrediction: this.currentPrediction,
                predictionHistory: this.predictionHistory,
                backtestResults: this.backtestResults,
                performanceMetrics: this.performanceMetrics,
                lastUpdated: new Date().toISOString()
            };
            localStorage.setItem('sharedPredictionData', JSON.stringify(data));
        } catch (e) {
            console.error('Error saving data:', e);
        }
    }
    
    // Event system
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
    
    // API Methods
    async generatePrediction(symbol, timeframe = '5d') {
        try {
            const url = `${this.API_BASE}/api/unified-prediction/${symbol}?timeframe=${timeframe}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Store prediction
            this.currentPrediction = {
                symbol: symbol,
                timeframe: timeframe,
                timestamp: new Date().toISOString(),
                data: data
            };
            
            // Add to history
            this.predictionHistory.unshift(this.currentPrediction);
            if (this.predictionHistory.length > 50) {
                this.predictionHistory = this.predictionHistory.slice(0, 50);
            }
            
            // Save and emit
            this.saveData();
            this.emit('predictionGenerated', this.currentPrediction);
            
            return data;
            
        } catch (error) {
            console.error('Prediction error:', error);
            this.emit('predictionError', error);
            throw error;
        }
    }
    
    async runBacktest(symbol, startDate, endDate, capital = 100000) {
        try {
            const response = await fetch(`${this.API_BASE}/api/backtest`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    start_date: startDate,
                    end_date: endDate,
                    initial_capital: capital
                })
            });
            
            const data = await response.json();
            
            this.backtestResults = {
                symbol: symbol,
                timestamp: new Date().toISOString(),
                results: data
            };
            
            this.saveData();
            this.emit('backtestCompleted', this.backtestResults);
            
            return data;
            
        } catch (error) {
            console.error('Backtest error:', error);
            this.emit('backtestError', error);
            throw error;
        }
    }
    
    async getPerformanceMetrics(symbol) {
        try {
            const response = await fetch(`${this.API_BASE}/api/model-performance/${symbol}`);
            const data = await response.json();
            
            this.performanceMetrics = data;
            this.saveData();
            this.emit('performanceUpdated', data);
            
            return data;
            
        } catch (error) {
            console.error('Performance metrics error:', error);
            throw error;
        }
    }
    
    async getTechnicalAnalysis(symbol) {
        try {
            const response = await fetch(`${this.API_BASE}/api/technical/analysis/${symbol}`);
            const data = await response.json();
            
            this.emit('technicalAnalysisUpdated', data);
            return data;
            
        } catch (error) {
            console.error('Technical analysis error:', error);
            throw error;
        }
    }
    
    // Get current prediction
    getCurrentPrediction() {
        return this.currentPrediction;
    }
    
    // Get prediction for specific symbol from history
    getPredictionForSymbol(symbol) {
        return this.predictionHistory.find(p => p.symbol === symbol);
    }
    
    // Get all predictions for a symbol
    getAllPredictionsForSymbol(symbol) {
        return this.predictionHistory.filter(p => p.symbol === symbol);
    }
    
    // Clear all data
    clearData() {
        this.currentPrediction = null;
        this.predictionHistory = [];
        this.backtestResults = null;
        this.performanceMetrics = null;
        localStorage.removeItem('sharedPredictionData');
        this.emit('dataCleared', {});
    }
    
    // Export data
    exportData() {
        const data = {
            currentPrediction: this.currentPrediction,
            predictionHistory: this.predictionHistory,
            backtestResults: this.backtestResults,
            performanceMetrics: this.performanceMetrics,
            exportedAt: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        const exportFileName = `gsmt_data_export_${new Date().toISOString()}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileName);
        linkElement.click();
        
        this.emit('dataExported', {});
    }
    
    // Import data
    importData(jsonData) {
        try {
            const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
            
            if (data.currentPrediction) this.currentPrediction = data.currentPrediction;
            if (data.predictionHistory) this.predictionHistory = data.predictionHistory;
            if (data.backtestResults) this.backtestResults = data.backtestResults;
            if (data.performanceMetrics) this.performanceMetrics = data.performanceMetrics;
            
            this.saveData();
            this.emit('dataImported', data);
            
            return true;
        } catch (error) {
            console.error('Import error:', error);
            return false;
        }
    }
}

// Create global instance
window.sharedDataService = new SharedDataService();

// Helper functions for backwards compatibility
window.getSharedPrediction = function() {
    return window.sharedDataService.getCurrentPrediction();
};

window.setSharedPrediction = function(data) {
    window.sharedDataService.currentPrediction = data;
    window.sharedDataService.saveData();
    window.sharedDataService.emit('predictionUpdated', data);
};

console.log('📊 Shared Data Service initialized');
console.log('   API:', window.sharedDataService.API_BASE);
console.log('   History:', window.sharedDataService.predictionHistory.length, 'predictions loaded');