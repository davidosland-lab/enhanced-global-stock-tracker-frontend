#!/usr/bin/env python3
"""
Minimal Chart.js + Flask test to verify charts work
"""

from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Chart Test</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <h1>Simple Chart.js Test</h1>
    <div style="max-width: 600px; margin: 20px;">
        <canvas id="myChart"></canvas>
    </div>
    
    <button onclick="createChart()">Create Chart</button>
    <button onclick="fetchAndChart()">Fetch & Chart</button>
    
    <script>
        let chart = null;
        
        function createChart() {
            console.log('Creating chart...');
            
            // Destroy existing
            if (chart) {
                chart.destroy();
            }
            
            const ctx = document.getElementById('myChart').getContext('2d');
            
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                    datasets: [{
                        label: 'Test Data',
                        data: [10, 20, 15, 25, 30],
                        borderColor: 'blue',
                        fill: false
                    }]
                },
                options: {
                    responsive: true
                }
            });
            
            console.log('Chart created');
        }
        
        async function fetchAndChart() {
            console.log('Fetching data...');
            
            const response = await fetch('/api/data');
            const data = await response.json();
            
            console.log('Data received:', data);
            
            // Destroy existing
            if (chart) {
                chart.destroy();
            }
            
            const ctx = document.getElementById('myChart').getContext('2d');
            
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Stock Price',
                        data: data.values,
                        borderColor: 'green',
                        fill: false
                    }]
                },
                options: {
                    responsive: true
                }
            });
            
            console.log('Chart created from API data');
        }
        
        // Auto-create chart on load
        window.addEventListener('load', function() {
            if (typeof Chart !== 'undefined') {
                console.log('Chart.js loaded successfully');
                createChart();
            } else {
                console.error('Chart.js not loaded!');
            }
        });
    </script>
</body>
</html>"""

@app.route("/api/data")
def api_data():
    """Return sample data for chart"""
    return jsonify({
        'labels': ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
        'values': [random.randint(100, 200) for _ in range(5)]
    })

if __name__ == "__main__":
    print("Test server at http://localhost:5001")
    app.run(port=5001, debug=True)