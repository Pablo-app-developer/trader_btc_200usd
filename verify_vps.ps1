# Script de verificación rápida de conectividad VPS
# Prueba la conexión SSH y los servicios principales

$VPS_IP = "107.174.133.37"
$VPS_USER = "root"

Write-Host "🔍 === VERIFICACIÓN DE CONECTIVIDAD VPS ===" -ForegroundColor Cyan
Write-Host "📡 IP: $VPS_IP" -ForegroundColor Yellow
Write-Host ""

# Test 1: Ping básico
Write-Host "1️⃣ Probando conectividad de red (ping)..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $VPS_IP -Count 2 -Quiet
if ($pingResult) {
    Write-Host "   ✅ El VPS responde a ping" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️ El VPS no responde a ping (puede estar bloqueado por firewall)" -ForegroundColor Yellow
}
Write-Host ""

# Test 2: Conexión SSH
Write-Host "2️⃣ Probando conexión SSH..." -ForegroundColor Yellow
try {
    $sshOutput = ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "hostname && uptime" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Conexión SSH exitosa" -ForegroundColor Green
        Write-Host "   📊 Info del servidor:" -ForegroundColor Cyan
        Write-Host "   $sshOutput" -ForegroundColor Gray
    }
    else {
        Write-Host "   ❌ Error en conexión SSH" -ForegroundColor Red
        Write-Host "   Verifica que tengas acceso SSH configurado" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ❌ No se pudo conectar por SSH" -ForegroundColor Red
}
Write-Host ""

# Test 3: Docker
Write-Host "3️⃣ Verificando Docker en el VPS..." -ForegroundColor Yellow
try {
    $dockerCheck = ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "docker --version && docker ps -a" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Docker está instalado y funcionando" -ForegroundColor Green
        Write-Host "   $dockerCheck" -ForegroundColor Gray
    }
    else {
        Write-Host "   ⚠️ Docker no está disponible o no responde" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ⚠️ No se pudo verificar Docker" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: TensorBoard
Write-Host "4️⃣ Verificando puerto de TensorBoard (6006)..." -ForegroundColor Yellow
try {
    $tensorboardUrl = "http://$VPS_IP:6006"
    $webRequest = Invoke-WebRequest -Uri $tensorboardUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($webRequest.StatusCode -eq 200) {
        Write-Host "   ✅ TensorBoard está accesible en $tensorboardUrl" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️ TensorBoard no responde en $tensorboardUrl" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ⚠️ TensorBoard no está accesible (puede que no esté corriendo)" -ForegroundColor Yellow
    Write-Host "   URL: $tensorboardUrl" -ForegroundColor Gray
}
Write-Host ""

# Test 5: Espacio en disco
Write-Host "5️⃣ Verificando espacio en disco..." -ForegroundColor Yellow
try {
    $diskSpace = ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "df -h /" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Espacio en disco:" -ForegroundColor Green
        Write-Host "   $diskSpace" -ForegroundColor Gray
    }
    else {
        Write-Host "   ⚠️ No se pudo verificar el espacio en disco" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ⚠️ No se pudo verificar el espacio en disco" -ForegroundColor Yellow
}
Write-Host ""

# Resumen
Write-Host "🎯 === RESUMEN ===" -ForegroundColor Cyan
Write-Host "✅ = Funcionando correctamente" -ForegroundColor Green
Write-Host "⚠️ = Advertencia o no disponible" -ForegroundColor Yellow
Write-Host "❌ = Error crítico" -ForegroundColor Red
Write-Host ""
Write-Host "💡 Para más información, consulta VPS_INFO.md" -ForegroundColor Cyan
