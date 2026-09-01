#!/bin/bash
# Linux/macOS deployment script

echo "🚀 Auto-Grader API - Deployment Script"

# Step 1: Check Python
echo -e "\n[1/3] Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python not installed!"
    exit 1
fi

# Step 2: Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "\n[2/3] Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Step 3: Install dependencies
echo -e "\n[3/3] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Kill existing process on port 8000
echo -e "\n[4/4] Checking ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Step 5: Start the API
echo -e "\n✅ Starting API server..."
echo "📍 API: http://localhost:8000"
echo "📍 Docs: http://localhost:8000/docs"
echo "📍 Health: http://localhost:8000/api/v1/health"
echo -e "\nPress CTRL+C to stop...\n"

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
