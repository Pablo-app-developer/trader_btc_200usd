#!/bin/bash
# Script de verificación rápida de conectividad VPS
# Prueba la conexión SSH y los servicios principales

VPS_IP="107.174.133.202"
VPS_USER="root"

echo "🔍 === VERIFICACIÓN DE CONECTIVIDAD VPS ==="
echo "📡 IP: $VPS_IP"
echo ""

# Test 1: Ping básico
echo "1️⃣ Probando conectividad de red (ping)..."
if ping -c 2 -W 3 $VPS_IP > /dev/null 2>&1; then
    echo "   ✅ El VPS responde a ping"
else
    echo "   ⚠️ El VPS no responde a ping (puede estar bloqueado por firewall)"
fi
echo ""

# Test 2: Conexión SSH
echo "2️⃣ Probando conexión SSH..."
if ssh_output=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "hostname && uptime" 2>&1); then
    echo "   ✅ Conexión SSH exitosa"
    echo "   📊 Info del servidor:"
    echo "   $ssh_output"
else
    echo "   ❌ Error en conexión SSH"
    echo "   Verifica que tengas acceso SSH configurado"
fi
echo ""

# Test 3: Docker
echo "3️⃣ Verificando Docker en el VPS..."
if docker_check=$(ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "docker --version && docker ps -a" 2>&1); then
    echo "   ✅ Docker está instalado y funcionando"
    echo "   $docker_check"
else
    echo "   ⚠️ Docker no está disponible o no responde"
fi
echo ""

# Test 4: TensorBoard
echo "4️⃣ Verificando puerto de TensorBoard (6006)..."
tensorboard_url="http://$VPS_IP:6006"
if curl -s -f -m 5 "$tensorboard_url" > /dev/null 2>&1; then
    echo "   ✅ TensorBoard está accesible en $tensorboard_url"
else
    echo "   ⚠️ TensorBoard no está accesible (puede que no esté corriendo)"
    echo "   URL: $tensorboard_url"
fi
echo ""

# Test 5: Espacio en disco
echo "5️⃣ Verificando espacio en disco..."
if disk_space=$(ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "df -h /" 2>&1); then
    echo "   ✅ Espacio en disco:"
    echo "   $disk_space"
else
    echo "   ⚠️ No se pudo verificar el espacio en disco"
fi
echo ""

# Test 6: Memoria RAM
echo "6️⃣ Verificando uso de memoria..."
if mem_info=$(ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "free -h" 2>&1); then
    echo "   ✅ Uso de memoria:"
    echo "   $mem_info"
else
    echo "   ⚠️ No se pudo verificar el uso de memoria"
fi
echo ""

# Resumen
echo "🎯 === RESUMEN ==="
echo "✅ = Funcionando correctamente"
echo "⚠️ = Advertencia o no disponible"
echo "❌ = Error crítico"
echo ""
echo "💡 Para más información, consulta VPS_INFO.md"
