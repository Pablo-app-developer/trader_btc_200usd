# Script de despliegue automatico al VPS (Windows PowerShell) - VERSION RESILIENTE
# Fecha: 28 Enero 2026

Write-Host ""
Write-Host ">>> DESPLIEGUE AUTOMATICO AL VPS (REPARADOR) <<<" -ForegroundColor Green
Write-Host ""

$vps_ip = "107.174.133.37"
$vps_user = "root"
$vps_dir = "/root/sol-bot-200"

# 1. Preparar el servidor e instalar dependencias
Write-Host "[*] Preparando servidor (instalando unzip/docker)..." -ForegroundColor Yellow
$setup_cmd = "mkdir -p ${vps_dir} && apt-get update -y && apt-get install -y unzip docker-compose"
ssh -o ConnectTimeout=10 "${vps_user}@${vps_ip}" $setup_cmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Error al preparar el servidor. Verifica conexion y permisos root." -ForegroundColor Red
    exit 1
}

# 2. Comprimir archivos locales
Write-Host ""
Write-Host "[*] Comprimiendo archivos..." -ForegroundColor Yellow
$zipFile = "deploy_temp.zip"
if (Test-Path $zipFile) { Remove-Item $zipFile }
Compress-Archive -Path "config", "models", "*.py", "*.sh", "docker-compose.yml", "requirements.txt", "manage_bot.sh" -DestinationPath $zipFile

# 3. Transferir de nuevo
Write-Host ""
Write-Host "[*] Enviando archivos al VPS..." -ForegroundColor Yellow
scp $zipFile "${vps_user}@${vps_ip}:${vps_dir}/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Error en la transferencia" -ForegroundColor Red
    exit 1
}

# 4. Descomprimir (solo si existe el archivo)
Write-Host ""
Write-Host "[*] Descomprimiendo en el servidor..." -ForegroundColor Yellow
$unpack_cmd = "cd ${vps_dir} && if [ -f deploy_temp.zip ]; then unzip -o deploy_temp.zip && rm deploy_temp.zip; else echo 'Archivo no encontrado'; exit 1; fi"
ssh "${vps_user}@${vps_ip}" $unpack_cmd

# Limpiar local
Remove-Item $zipFile

# 5. Reiniciar bots
Write-Host ""
$resp = Read-Host "Desea levantar los bots en Docker ahora? (s/n)"
if ($resp -eq "s" -or $resp -eq "S") {
    Write-Host "[*] Levantando contenedores 200usd..." -ForegroundColor Yellow
    # Usamos docker-compose (con guion) que es el que instalamos en el paso 1
    ssh "${vps_user}@${vps_ip}" "cd ${vps_dir} && docker-compose up -d --force-recreate"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] TODO OK: Bots activos y aislados" -ForegroundColor Green
    }
    else {
        Write-Host "[!] Error al iniciar Docker. Revisa 'docker ps' en el VPS." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ">>> DESPLIEGUE FINALIZADO CON EXITO <<<" -ForegroundColor Green
Write-Host "Acceso TensorBoard: http://${vps_ip}:6007"
Write-Host ""
