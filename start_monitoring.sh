#!/bin/bash
# Script para iniciar Dashboard y Healthcheck en el VPS

echo "🚀 Iniciando servicios de monitoreo..."

# Instalar dependencias si no están
pip3 install -q streamlit plotly flask psutil pyyaml requests pandas 2>/dev/null

# Iniciar Healthcheck en background
echo "📊 Iniciando Healthcheck API en puerto 5000..."
nohup python3 /root/sol-bot-200/healthcheck.py > /root/sol-bot-200/healthcheck.log 2>&1 &
echo $! > /root/sol-bot-200/healthcheck.pid

# Esperar un poco
sleep 2

# Iniciar Dashboard
echo "📈 Iniciando Dashboard en puerto 8501..."
nohup streamlit run /root/sol-bot-200/dashboard.py --server.port 8501 --server.address 0.0.0.0 > /root/sol-bot-200/dashboard.log 2>&1 &
echo $! > /root/sol-bot-200/dashboard.pid

echo ""
echo "✅ Servicios iniciados!"
echo "   Dashboard:   http://107.174.133.37:8501"
echo "   Healthcheck: http://107.174.133.37:5000/health"
echo ""
echo "Para ver logs:"
echo "   tail -f /root/sol-bot-200/dashboard.log"
echo "   tail -f /root/sol-bot-200/healthcheck.log"
