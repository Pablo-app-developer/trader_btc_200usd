# Script para revisar operaciones del bot en el VPS
# Ejecuta este script DESPUÉS de conectarte al VPS con SSH

Write-Host "`n🤖 === REVISIÓN DE OPERACIONES DEL BOT ===" -ForegroundColor Cyan
Write-Host "Ejecuta estos comandos en el VPS:`n" -ForegroundColor Yellow

$commands = @"
# 1. Ver estado de los contenedores Docker
echo "=== ESTADO DE DOCKER ==="
docker ps -a

echo ""
echo "=== LOGS DEL BOT BTC (últimas 50 líneas) ==="
docker logs --tail 50 trader_btc

echo ""
echo "=== LOGS DEL BOT ETH (últimas 50 líneas) ==="
docker logs --tail 50 trader_eth

echo ""
echo "=== LOGS DEL BOT SOL (últimas 50 líneas) ==="
docker logs --tail 50 trader_sol

echo ""
echo "=== BUSCAR OPERACIONES EJECUTADAS (COMPRA/VENTA) ==="
docker logs trader_btc | grep -E "COMPRA|VENTA|BUY|SELL" | tail -20
docker logs trader_eth | grep -E "COMPRA|VENTA|BUY|SELL" | tail -20
docker logs trader_sol | grep -E "COMPRA|VENTA|BUY|SELL" | tail -20

echo ""
echo "=== BALANCE Y PERFORMANCE ==="
docker logs trader_btc | grep -E "Balance|PnL|WinRate" | tail -10
docker logs trader_eth | grep -E "Balance|PnL|WinRate" | tail -10
docker logs trader_sol | grep -E "Balance|PnL|WinRate" | tail -10

echo ""
echo "=== ERRORES RECIENTES ==="
docker logs --since 24h trader_btc 2>&1 | grep -i "error\|exception\|failed" | tail -10
docker logs --since 24h trader_eth 2>&1 | grep -i "error\|exception\|failed" | tail -10
docker logs --since 24h trader_sol 2>&1 | grep -i "error\|exception\|failed" | tail -10

echo ""
echo "=== ARCHIVO DE LOGS (si existe) ==="
ls -lh /root/sol-bot-200/*.log 2>/dev/null || echo "No log files found"
"@

Write-Host $commands -ForegroundColor Gray
Write-Host "`n" -ForegroundColor White
Write-Host "📋 PASOS:" -ForegroundColor Cyan
Write-Host "  1. Conéctate al VPS:" -ForegroundColor White
Write-Host "     ssh root@107.174.133.202" -ForegroundColor Yellow
Write-Host "`n  2. Copia y pega los comandos de arriba" -ForegroundColor White
Write-Host "`n  3. O si prefieres, ejecuta comando por comando" -ForegroundColor White

Write-Host "`n💡 COMANDOS RÁPIDOS MÁS ÚTILES:" -ForegroundColor Cyan
Write-Host "  Ver operaciones de hoy:" -ForegroundColor White
Write-Host "    docker logs trader_btc | grep -E 'COMPRA|VENTA|Balance'" -ForegroundColor Yellow
Write-Host "`n  Ver logs en tiempo real:" -ForegroundColor White  
Write-Host "    docker logs -f trader_btc" -ForegroundColor Yellow
Write-Host "`n  Ver solo trades:" -ForegroundColor White
Write-Host "    docker logs trader_btc | grep 'SEÑAL'" -ForegroundColor Yellow
Write-Host ""
