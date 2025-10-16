#!/bin/bash

echo "========================================"
echo "Stock Tracker V7 - Service Status Check"
echo "========================================"

# Check Main Backend (8002)
echo -n "Main Backend (8002): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/ | grep -q "200"; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

# Check ML Backend (8003)
echo -n "ML Backend (8003): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/api/ml/status | grep -q "200"; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

# Check FinBERT Backend (8004)
echo -n "FinBERT Backend (8004): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/api/sentiment | grep -q "405\|200"; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

# Check Web Server (8080)
echo -n "Web Server (8080): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep -q "200"; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo ""
echo "Active Python processes:"
ps aux | grep python | grep -E "(backend|http.server)" | grep -v grep | awk '{print "  - " $11 " " $12}'

echo ""
echo "Listening ports:"
netstat -tulpn 2>/dev/null | grep -E ":(8002|8003|8004|8080)" | grep LISTEN | awk '{print "  - Port " $4}'