# Script de despliegue automático al VPS (Windows PowerShell)
# Este script sincroniza el código local con el VPS y reinicia el bot

$VPS_IP = "107.174.133.202"
$VPS_USER = "root"
$VPS_DIR = "/root/sol-bot-200"

Write-Host "🚀 === DESPLIEGUE AUTOMÁTICO AL VPS ===" -ForegroundColor Green
Write-Host "📡 IP: $VPS_IP" -ForegroundColor Cyan
Write-Host "📂 Directorio remoto: $VPS_DIR" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que SSH está disponible
Write-Host "🔍 Verificando SSH..." -ForegroundColor Yellow
try {
    ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "echo 'Conexión exitosa'" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Error de conexión"
    }
    Write-Host "✅ Conexión SSH verificada" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error: No se puede conectar al VPS. Verifica:" -ForegroundColor Red
    Write-Host "   - La IP es correcta: $VPS_IP" -ForegroundColor Yellow
    Write-Host "   - Tienes acceso SSH configurado" -ForegroundColor Yellow
    Write-Host "   - OpenSSH está instalado en Windows" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# 2. Crear directorio remoto si no existe
Write-Host "📁 Verificando directorio remoto..." -ForegroundColor Yellow
ssh "$VPS_USER@$VPS_IP" "mkdir -p $VPS_DIR"
Write-Host "✅ Directorio listo" -ForegroundColor Green
Write-Host ""

# 3. Verificar si SCP está disponible
Write-Host "📦 Preparando sincronización de archivos..." -ForegroundColor Yellow
Write-Host "ℹ️  Nota: Este proceso puede tardar varios minutos" -ForegroundColor Cyan
Write-Host ""

# Comprimir archivos para transferencia más rápida
Write-Host "📦 Comprimiendo archivos..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipFile = "deploy_$timestamp.zip"

# Crear archivo zip (excluyendo archivos pesados automáticamente)
Compress-Archive -Path * -DestinationPath $zipFile -Force -CompressionLevel Optimal 2>$null

Write-Host "✅ Archivos comprimidos: $zipFile" -ForegroundColor Green
Write-Host ""

# 4. Transferir archivo zip
Write-Host "🚀 Transfiriendo archivos al VPS..." -ForegroundColor Yellow
scp $zipFile "$VPS_USER@${VPS_IP}:$VPS_DIR/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Archivos transferidos correctamente" -ForegroundColor Green
}
else {
    Write-Host "❌ Error al transferir archivos" -ForegroundColor Red
    Remove-Item $zipFile -Force
    exit 1
}
Write-Host ""

# 5. Descomprimir en el VPS y limpiar
Write-Host "📂 Descomprimiendo en el VPS..." -ForegroundColor Yellow
ssh "$VPS_USER@$VPS_IP" @"
cd $VPS_DIR
unzip -o $zipFile
rm $zipFile
"@
Write-Host "✅ Archivos descomprimidos" -ForegroundColor Green
Write-Host ""

# Limpiar archivo zip local
Remove-Item $zipFile -Force

# 6. Instalar/actualizar dependencias
Write-Host "📚 Instalando dependencias en el VPS..." -ForegroundColor Yellow
ssh "$VPS_USER@$VPS_IP" "cd $VPS_DIR && pip3 install -r requirements.txt --upgrade"
Write-Host ""

# 7. Preguntar si reiniciar el bot
$restart = Read-Host "¿Quieres reiniciar el bot ahora? (s/n)"
if ($restart -eq "s" -or $restart -eq "S") {
    Write-Host "🔄 Reiniciando bot..." -ForegroundColor Yellow
    ssh "$VPS_USER@$VPS_IP" @"
pkill -f sol_sniper_bot.py
cd $VPS_DIR
nohup python3 sol_sniper_bot.py > bot_output.log 2>&1 &
"@
    Write-Host "✅ Bot reiniciado" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Para ver los logs en tiempo real, ejecuta:" -ForegroundColor Cyan
    Write-Host "   .\connect_vps.ps1" -ForegroundColor Yellow
    Write-Host "   Luego: tail -f $VPS_DIR/bot_output.log" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 ¡Despliegue completado!" -ForegroundColor Green
Write-Host "🌐 TensorBoard: http://$VPS_IP:6006" -ForegroundColor Cyan
Write-Host "📡 SSH: ssh $VPS_USER@$VPS_IP" -ForegroundColor Cyan
