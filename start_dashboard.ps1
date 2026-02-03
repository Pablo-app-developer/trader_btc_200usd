# Quick Start Scripts for Phase 3

Write-Host "`n=== TRADING BOT DASHBOARD & MONITORING ===" -ForegroundColor Cyan
Write-Host ""

# Install dependencies
Write-Host "[1] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements_phase3.txt

Write-Host "`n[2] Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start healthcheck in background
Write-Host "   Starting Healthcheck API on port 5000..." -ForegroundColor Gray
Start-Process python -ArgumentList "healthcheck.py" -WindowStyle Hidden

Start-Sleep -Seconds 2

# Start dashboard
Write-Host "   Starting Dashboard on port 8501..." -ForegroundColor Gray
Write-Host ""

Write-Host "="*60 -ForegroundColor Green
Write-Host "SERVICES STARTED!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard:   http://localhost:8501" -ForegroundColor Cyan
Write-Host "Healthcheck: http://localhost:5000/health" -ForegroundColor Cyan
Write-Host "Metrics:     http://localhost:5000/metrics" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start dashboard (this will block)
streamlit run dashboard.py
