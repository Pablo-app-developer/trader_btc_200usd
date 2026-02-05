# Script de Diagnóstico VPS
# Ejecuta este script para verificar el estado del VPS y los bots

$VPS_IP = "107.174.133.37"
$VPS_USER = "root"

Write-Host "`n=== DIAGNÓSTICO VPS ===" -ForegroundColor Cyan
Write-Host "IP: $VPS_IP" -ForegroundColor Yellow
Write-Host ""

# Test 1: Ping
Write-Host "[1] Probando conectividad (ping)..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $VPS_IP -Count 2 -Quiet
if ($ping) {
    Write-Host "✓ Servidor responde a ping" -ForegroundColor Green
}
else {
    Write-Host "✗ Servidor NO responde a ping" -ForegroundColor Red
}

# Test 2: Puerto SSH
Write-Host "`n[2] Verificando puerto SSH (22)..." -ForegroundColor Yellow
$tcpTest = Test-NetConnection -ComputerName $VPS_IP -Port 22 -WarningAction SilentlyContinue
if ($tcpTest.TcpTestSucceeded) {
    Write-Host "✓ Puerto 22 abierto" -ForegroundColor Green
}
else {
    Write-Host "✗ Puerto 22 cerrado o bloqueado" -ForegroundColor Red
}

# Test 3: Intentar conexión SSH
Write-Host "`n[3] Intentando conexión SSH..." -ForegroundColor Yellow
Write-Host "Comando: ssh $VPS_USER@$VPS_IP" -ForegroundColor Gray
Write-Host ""
Write-Host "INSTRUCCIONES:" -ForegroundColor Cyan
Write-Host "1. Si pide contraseña, ingrésala manualmente" -ForegroundColor White
Write-Host "2. Una vez conectado, ejecuta estos comandos:" -ForegroundColor White
Write-Host ""
Write-Host "   # Ver procesos del bot:" -ForegroundColor Yellow
Write-Host "   ps aux | grep python" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Ver contenedores Docker:" -ForegroundColor Yellow
Write-Host "   docker ps -a" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Ver logs del bot:" -ForegroundColor Yellow
Write-Host "   tail -50 ~/sol-bot-200/bot.log" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Ver logs de Docker:" -ForegroundColor Yellow
Write-Host "   docker logs sol-sniper-bot" -ForegroundColor Gray
Write-Host ""
Write-Host "Presiona ENTER para abrir conexión SSH manual..." -ForegroundColor Cyan
Read-Host

# Abrir SSH interactivo
ssh "$VPS_USER@$VPS_IP"
