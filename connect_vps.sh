#!/bin/bash
# Script de conexión SSH al VPS

VPS_IP="107.174.133.202"
VPS_USER="root"

echo "🚀 Conectando al VPS en $VPS_IP..."
echo ""
echo "💡 Tip: Una vez conectado, puedes usar estos comandos:"
echo "  - Ver logs del bot: docker logs -f trader_eth"
echo "  - Ver contenedores: docker ps -a"
echo "  - Reiniciar bot: docker restart trader_eth"
echo ""

# Conectar via SSH
ssh "$VPS_USER@$VPS_IP"
