#!/bin/bash

echo "🔧 INICIANDO AUTO-REPARACIÓN DEL BOT..."

# 1. Parar contenedores viejos
echo "🛑 Deteniendo contenedores antiguos..."
docker stop bot_eth
docker rm bot_eth

# 2. Arreglar dependencias
echo "💊 Añadiendo 'tensorboard' a requirements.txt..."
if ! grep -q "tensorboard" requirements.txt; then
    echo "tensorboard>=2.10.0" >> requirements.txt
fi

# 3. Reconstruir imagen Docker
echo "🏗️ Reconstruyendo imagen Docker (esto puede tardar un poco)..."
docker compose build bot

# 4. Verificar Swap (Memoria)
echo "🧠 Verificando memoria swap..."
if [ ! -f /swapfile ]; then
    echo "   Creando 4GB de Swap de emergencia..."
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
else
    echo "   ✅ Swap ya existe."
fi

# 5. Lanzar de nuevo
echo "🚀 LANZANDO BOT ETH V2.0..."
docker compose run -d --name bot_eth bot python train_production.py ETH

echo "✅ ¡LISTO! Espera 30 segundos y recarga http://$(curl -s ifconfig.me):6006"
echo "📜 Viendo logs en tiempo real (Presiona Ctrl+C para salir)..."
sleep 5
docker logs -f bot_eth
