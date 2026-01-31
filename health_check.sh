#!/bin/bash

echo "🔍 RTA Nexus System Check"
echo "========================================"

# Check Backend
echo ""
echo "1️⃣  Backend API Check..."
SCHOOLS=$(curl -s http://localhost:8000/api/schools 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data))" 2>/dev/null)
if [ -z "$SCHOOLS" ]; then
    echo "   ❌ Backend not responding on http://localhost:8000"
    echo "   👉 Start backend: cd backend && python -m uvicorn main:app --port 8000"
else
    echo "   ✅ Backend running - Found $SCHOOLS schools"
fi

# Check Routes
echo ""
echo "2️⃣  Routes API Check..."
ROUTES=$(curl -m 60 -s "http://localhost:8000/api/routes?peak_hours=true" 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('total_routes', 0))" 2>/dev/null)
if [ -z "$ROUTES" ]; then
    echo "   ❌ Routes endpoint not responding"
else
    echo "   ✅ Routes API working - Generated $ROUTES routes"
fi

# Check Frontend
echo ""
echo "3️⃣  Frontend Check..."
FRONTEND=$(curl -s http://localhost:8081 2>/dev/null | wc -c)
if [ "$FRONTEND" -lt 100 ]; then
    echo "   ❌ Frontend not responding on http://localhost:8081"
    echo "   👉 Start frontend: cd frontend && npm run dev"
else
    echo "   ✅ Frontend running - HTML size: ${FRONTEND} bytes"
fi

# Database check
echo ""
echo "4️⃣  Database Check..."
if [ -f "/Users/akramjemal/Downloads/the bounty challenge/jack-sparrow/backend/nexus.db" ]; then
    echo "   ✅ Database file exists"
else
    echo "   ❌ Database file not found - run init_db.py"
fi

echo ""
echo "========================================"
echo "🚀 Visit: http://localhost:8081"
echo ""
