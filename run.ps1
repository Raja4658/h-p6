# Windows PowerShell deployment script
Write-Host "🚀 Auto-Grader API - Deployment Script" -ForegroundColor Cyan

# Step 1: Check Python
Write-Host "`n[1/3] Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not installed!" -ForegroundColor Red
    exit 1
}

# Step 2: Install dependencies
Write-Host "`n[2/3] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Step 3: Kill existing process on port 8000/8080
Write-Host "`n[3/3] Checking ports..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "⚠️  Killing process on port 8000..." -ForegroundColor Yellow
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Step 4: Start the API
Write-Host "`n✅ Starting API server..." -ForegroundColor Green
Write-Host "📍 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📍 Health: http://localhost:8000/api/v1/health" -ForegroundColor Cyan
Write-Host "`nPress CTRL+C to stop...`n" -ForegroundColor Yellow

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
