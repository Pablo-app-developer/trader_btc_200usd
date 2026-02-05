# Script para ver resumen de operaciones de los bots
Write-Host "`n=== RESUMEN DE OPERACIONES DE LOS BOTS ===" -ForegroundColor Cyan
Write-Host ""

$VPS_IP = "107.174.133.37"

Write-Host "[1] Estado de los bots..." -ForegroundColor Yellow
ssh root@$VPS_IP "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

Write-Host "`n[2] TensorBoard disponible en:" -ForegroundColor Yellow
Write-Host "    http://$VPS_IP:6006" -ForegroundColor Green

Write-Host "`n[3] Abriendo TensorBoard en el navegador..." -ForegroundColor Yellow
Start-Process "http://$VPS_IP:6006"

Write-Host "`n[OK] Listo! Revisa el navegador para ver las métricas" -ForegroundColor Green
Write-Host ""
