
Write-Host "🔍 Verificando estado de servicios en VPS..." -ForegroundColor Cyan

$server = "107.174.133.37"

# Check Dashboard
try {
    $response = Invoke-WebRequest -Uri "http://$server:8501" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Dashboard:  ONLINE (http://$server:8501)" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Dashboard:  OFFLINE" -ForegroundColor Red
}

# Check Healthcheck API
try {
    $response = Invoke-WebRequest -Uri "http://$server:5000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Healthcheck: ONLINE (http://$server:5000/health)" -ForegroundColor Green
        
        # Show JSON
        $json = $response.Content | ConvertFrom-Json
        Write-Host "   📊 Estado Sistema:" -ForegroundColor Yellow
        Write-Host "      CPU: $($json.system.cpu_percent)%" 
        Write-Host "      RAM: $($json.system.memory_percent)%"
        
        Write-Host "   🤖 Bots:" -ForegroundColor Yellow
        $json.bots | Get-Member -MemberType NoteProperty | ForEach-Object {
            $bot = $_.Name
            $status = $json.bots.$bot.status
            Write-Host "      $bot : $status"
        }
    }
}
catch {
    Write-Host "❌ Healthcheck: OFFLINE" -ForegroundColor Red
}
