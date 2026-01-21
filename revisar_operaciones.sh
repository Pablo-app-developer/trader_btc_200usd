#!/bin/bash
# Script para revisar operaciones del bot
# IP del VPS
VPS_IP="107.174.133.202"

echo "🤖 === REVISIÓN DE OPERACIONES DEL BOT ==="
echo ""
echo "Conectando a VPS: $VPS_IP"
echo ""

ssh root@$VPS_IP << 'ENDSSH'
echo "=== ✅ CONECTADO AL VPS ==="
echo ""

echo "📊 1. ESTADO DE LOS CONTENEDORES DOCKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker ps -a
echo ""

echo "💼 2. OPERACIONES RECIENTES (ÚLTIMAS 20)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🪙 BTC:"
docker logs trader_btc 2>/dev/null | grep -E "COMPRA|VENTA|SEÑAL|Balance" | tail -10 || echo "  No hay logs de BTC"
echo ""
echo "💎 ETH:"
docker logs trader_eth 2>/dev/null | grep -E "COMPRA|VENTA|SEÑAL|Balance" | tail -10 || echo "  No hay logs de ETH"
echo ""
echo "☀️  SOL:"
docker logs trader_sol 2>/dev/null | grep -E "COMPRA|VENTA|SEÑAL|Balance" | tail -10 || echo "  No hay logs de SOL"
echo ""

echo "📈 3. PERFORMANCE Y MÉTRICAS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🪙 BTC - Win Rate y Balance:"
docker logs trader_btc 2>/dev/null | grep -E "WinRate|Balance Sim|PnL:" | tail -5 || echo "  Sin datos"
echo ""
echo "💎 ETH - Win Rate y Balance:"
docker logs trader_eth 2>/dev/null | grep -E "WinRate|Balance Sim|PnL:" | tail -5 || echo "  Sin datos"
echo ""
echo "☀️  SOL - Win Rate y Balance:"
docker logs trader_sol 2>/dev/null | grep -E "WinRate|Balance Sim|PnL:" | tail -5 || echo "  Sin datos"
echo ""

echo "⚠️  4. ERRORES RECIENTES (últimas 24h)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
errors_btc=$(docker logs --since 24h trader_btc 2>&1 | grep -i "error\|exception" | wc -l)
errors_eth=$(docker logs --since 24h trader_eth 2>&1 | grep -i "error\|exception" | wc -l)
errors_sol=$(docker logs --since 24h trader_sol 2>&1 | grep -i "error\|exception" | wc -l)

echo "  BTC: $errors_btc errores"
echo "  ETH: $errors_eth errores"
echo "  SOL: $errors_sol errores"
echo ""

echo "📁 5. ARCHIVOS DE LOG DISPONIBLES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ls -lh /root/sol-bot-200/*.log 2>/dev/null || echo "  No hay archivos .log en directorio"
echo ""

echo "✅ REVISIÓN COMPLETADA"
echo ""
echo "💡 Para ver logs en tiempo real de un bot específico:"
echo "   docker logs -f trader_btc"
echo "   docker logs -f trader_eth"
echo "   docker logs -f trader_sol"
ENDSSH
