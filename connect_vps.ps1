# Script de conexión SSH al VPS
# IP del VPS
$VPS_IP = "107.174.133.202"
$VPS_USER = "root"

Write-Host "🚀 Conectando al VPS en $VPS_IP..." -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tip: Una vez conectado, puedes usar estos comandos:" -ForegroundColor Cyan
Write-Host "  - Ver logs del bot: docker logs -f trader_eth" -ForegroundColor Yellow
Write-Host "  - Ver contenedores: docker ps -a" -ForegroundColor Yellow
Write-Host "  - Reiniciar bot: docker restart trader_eth" -ForegroundColor Yellow
Write-Host ""

# Conectar via SSH
ssh "$VPS_USER@$VPS_IP"
