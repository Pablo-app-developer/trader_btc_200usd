#!/bin/bash
# Script de despliegue automático al VPS
# Este script sincroniza el código local con el VPS y reinicia el bot

VPS_IP="107.174.133.202"
VPS_USER="root"
VPS_DIR="/root/sol-bot-200"

echo "🚀 === DESPLIEGUE AUTOMÁTICO AL VPS ==="
echo "📡 IP: $VPS_IP"
echo "📂 Directorio remoto: $VPS_DIR"
echo ""

# 1. Verificar conexión SSH
echo "🔍 Verificando conexión SSH..."
if ! ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "echo 'Conexión exitosa'" > /dev/null 2>&1; then
    echo "❌ Error: No se puede conectar al VPS. Verifica:"
    echo "   - La IP es correcta: $VPS_IP"
    echo "   - Tienes acceso SSH configurado"
    exit 1
fi
echo "✅ Conexión SSH verificada"
echo ""

# 2. Crear directorio si no existe
echo "📁 Verificando directorio remoto..."
ssh "$VPS_USER@$VPS_IP" "mkdir -p $VPS_DIR"
echo "✅ Directorio listo"
echo ""

# 3. Sincronizar archivos (excluyendo archivos pesados)
echo "📦 Sincronizando archivos al VPS..."
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='*.csv' \
    --exclude='models/' \
    --exclude='tensorboard_logs/' \
    --exclude='*.png' \
    --exclude='*.log' \
    . "$VPS_USER@$VPS_IP:$VPS_DIR/"

if [ $? -eq 0 ]; then
    echo "✅ Archivos sincronizados correctamente"
else
    echo "❌ Error al sincronizar archivos"
    exit 1
fi
echo ""

# 4. Instalar/actualizar dependencias
echo "📚 Instalando dependencias en el VPS..."
ssh "$VPS_USER@$VPS_IP" "cd $VPS_DIR && pip3 install -r requirements.txt"
echo ""

# 5. Preguntar si reiniciar el bot
read -p "¿Quieres reiniciar el bot ahora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "🔄 Reiniciando bot..."
    ssh "$VPS_USER@$VPS_IP" "pkill -f sol_sniper_bot.py; cd $VPS_DIR && nohup python3 sol_sniper_bot.py > bot_output.log 2>&1 &"
    echo "✅ Bot reiniciado"
    echo ""
    echo "📊 Para ver los logs en tiempo real, ejecuta:"
    echo "   ssh $VPS_USER@$VPS_IP 'tail -f $VPS_DIR/bot_output.log'"
fi

echo ""
echo "🎉 ¡Despliegue completado!"
echo "🌐 TensorBoard: http://$VPS_IP:6006"
