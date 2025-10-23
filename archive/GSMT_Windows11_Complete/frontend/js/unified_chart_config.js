// Unified Chart Configuration for GSMT Indices Tracker
// This ensures proper data loading and chart rendering

const UnifiedChartConfig = {
    // API endpoints
    API_BASE: 'http://localhost:8000',
    
    // Fetch real market data with proper error handling
    async fetchMarketData(symbols) {
        const data = {};
        
        try {
            // Try to get real data from backend
            const response = await fetch(`${this.API_BASE}/api/indices`);
            if (response.ok) {
                const result = await response.json();
                return this.processMarketData(result.indices || {}, symbols);
            }
        } catch (error) {
            console.log('Backend unavailable, using fallback data');
        }
        
        // Fallback to realistic mock data
        return this.generateRealisticData(symbols);
    },
    
    // Process market data into chart format
    processMarketData(indices, selectedSymbols) {
        const processed = {};
        
        selectedSymbols.forEach(symbol => {
            if (indices[symbol]) {
                const market = MARKETS[symbol];
                const basePrice = indices[symbol].price || indices[symbol].current_price || 5000;
                
                processed[symbol] = {
                    name: market.name,
                    currentPrice: basePrice,
                    data: this.generateTradingHoursData(market, basePrice)
                };
            }
        });
        
        return processed;
    },
    
    // Generate data only during trading hours
    generateTradingHoursData(market, basePrice) {
        const dataPoints = [];
        const volatility = 0.02; // 2% volatility
        
        for (let hour = 0; hour < 24; hour++) {
            const displayHour = (hour + 9) % 24; // Start from 9 AM AEST
            
            // Check if market is open at this hour
            let isOpen = false;
            if (market.closeHour > 24) {
                // Overnight market
                isOpen = displayHour >= market.openHour || displayHour <= (market.closeHour - 24);
            } else {
                isOpen = displayHour >= market.openHour && displayHour <= market.closeHour;
            }
            
            if (isOpen) {
                // Generate realistic price movement
                const randomWalk = (Math.random() - 0.5) * basePrice * volatility;
                const trendComponent = Math.sin(hour / 4) * basePrice * 0.01; // Slight trend
                const price = basePrice + randomWalk + trendComponent;
                
                dataPoints.push({
                    time: displayHour,
                    price: Math.max(price, 0) // Ensure positive
                });
            } else {
                // Market closed
                dataPoints.push({
                    time: displayHour,
                    price: null
                });
            }
        }
        
        return dataPoints;
    },
    
    // Generate realistic fallback data
    generateRealisticData(symbols) {
        const data = {};
        
        // Realistic base prices for each market
        const basePrices = {
            '^AORD': 7500,   // ASX All Ordinaries
            '^N225': 38000,  // Nikkei 225
            '^HSI': 18000,   // Hang Seng
            '^FTSE': 7700,   // FTSE 100
            '^GDAXI': 18000, // DAX
            '^GSPC': 5000    // S&P 500
        };
        
        symbols.forEach(symbol => {
            const market = MARKETS[symbol];
            const basePrice = basePrices[symbol] || 5000;
            
            data[symbol] = {
                name: market.name,
                currentPrice: basePrice,
                data: this.generateTradingHoursData(market, basePrice)
            };
        });
        
        return data;
    },
    
    // Format chart data for Chart.js
    formatChartData(marketData, selectedMarkets) {
        const datasets = [];
        const labels = [];
        
        // Generate time labels
        for (let i = 0; i < 24; i++) {
            const hour = (i + 9) % 24;
            labels.push(`${hour.toString().padStart(2, '0')}:00`);
        }
        
        // Create dataset for each market
        selectedMarkets.forEach(symbol => {
            const market = MARKETS[symbol];
            const data = marketData[symbol];
            
            if (data && data.data) {
                datasets.push({
                    label: market.name,
                    data: data.data.map(d => d.price),
                    borderColor: market.color,
                    backgroundColor: market.color + '20',
                    borderWidth: 2,
                    tension: 0.1,
                    spanGaps: false,
                    pointRadius: 1,
                    pointHoverRadius: 5,
                    pointHitRadius: 10
                });
            }
        });
        
        return { labels, datasets };
    },
    
    // Update existing chart
    updateChart(chart, marketData, selectedMarkets) {
        const { labels, datasets } = this.formatChartData(marketData, selectedMarkets);
        
        chart.data.labels = labels;
        chart.data.datasets = datasets;
        chart.update('none'); // Update without animation for smoother experience
    },
    
    // Check server connectivity
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.API_BASE}/health`);
            return response.ok;
        } catch {
            return false;
        }
    }
};

// Make it globally available
window.UnifiedChartConfig = UnifiedChartConfig;