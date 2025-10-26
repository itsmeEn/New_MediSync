#!/bin/bash

# MediSync Admin Site Startup Script

echo "🚀 Starting MediSync Admin Site..."
echo "=================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use. Please stop the service using port $1 first."
        return 1
    else
        return 0
    fi
}

# Check if virtual environment exists
if [ ! -d "/Users/judeibardaloza/.local/share/virtualenvs/medisync-WHaJ4sn5" ]; then
    echo "❌ Virtual environment not found. Please set up the project first."
    exit 1
fi

# Check ports
echo "🔍 Checking ports..."
if ! check_port 8001; then
    exit 1
fi

if ! check_port 8080; then
    exit 1
fi

echo "✅ Ports are available"

# Start backend server
echo "🔧 Starting backend server on port 8001..."
source /Users/judeibardaloza/.local/share/virtualenvs/medisync-WHaJ4sn5/bin/activate
python create_admin.py
python manage.py runserver 8001 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting frontend server on port 8080..."
cd admin-frontend
python -m http.server 8080 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

echo ""
echo "🎉 MediSync Admin Site is now running!"
echo "======================================"
echo "📊 Admin Dashboard: http://localhost:8080"
echo "🔌 Backend API: http://localhost:8001/api/admin/"
echo ""
echo "👤 Login Credentials:"
echo "   Email: admin@medisync.com"
echo "   Password: Adminsh1!je590"
echo ""
echo "🛑 To stop the servers, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running
wait
