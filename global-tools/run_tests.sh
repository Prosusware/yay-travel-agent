#!/bin/bash

# Global Tools API Test Runner
echo "🚀 Global Tools API Test Runner"
echo "================================"

# Check if API server is running
echo "📡 Checking if API server is running..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ API server is running"
else
    echo "❌ API server not detected at http://localhost:8000"
    echo ""
    echo "To start the API server, run:"
    echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    read -p "Start API server in background? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Starting API server in background..."
        uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
        API_PID=$!
        echo "API server started with PID: $API_PID"
        echo "Waiting for server to start..."
        sleep 5
    else
        echo "Please start the API server manually and run tests again."
        exit 1
    fi
fi

# Install test dependencies if needed
echo ""
echo "📦 Installing test dependencies..."
pip install -r test_requirements.txt > /dev/null 2>&1

# Run tests
echo ""
echo "🧪 Running comprehensive API tests..."
echo "================================"
python3 test_api.py "$@"

# Clean up
if [ ! -z "$API_PID" ]; then
    echo ""
    read -p "Stop API server? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $API_PID
        echo "API server stopped."
    else
        echo "API server still running with PID: $API_PID"
        echo "To stop: kill $API_PID"
    fi
fi 