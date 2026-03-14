#!/bin/bash

# Kill any existing processes
lsof -i :8000 -t | xargs kill -9 2>/dev/null
lsof -i :3000 -t | xargs kill -9 2>/dev/null

echo "🚀 Starting INDMoney Insights Analyzer..."

# Start Backend
echo "📡 Starting FastAPI Backend on port 8000..."
mkdir -p logs
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BE_PID=$!

# Start Frontend
echo "🎨 Starting Next.js Frontend on port 3000..."
cd web
export PATH="$PWD/../node-bin/bin:$PATH"
npm run dev > ../logs/frontend.log 2>&1 &
FE_PID=$!

echo "✅ Backend and Frontend are running!"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services."

# Handle shutdown
trap "kill $BE_PID $FE_PID $SCHEDULER_PID; exit" INT

# Keep script running
wait
