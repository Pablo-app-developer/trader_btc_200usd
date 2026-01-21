# Script para aplicar la optimizacion de parametros al VPS
# Fecha: 21 Enero 2026

Write-Host ""
Write-Host ">>> APLICANDO OPTIMIZACION DE PARAMETROS <<<" -ForegroundColor Cyan
Write-Host "Objetivo: Aumentar actividad y rentabilidad" -ForegroundColor Yellow
Write-Host ""

# Configuracion del VPS
$vps_host = "107.174.133.202"
$vps_user = "root"
$vps_path = "/root/sol-bot-200"

# Paso 1: Verificar archivo local
$config_file = "config\assets.py"
if (-not (Test-Path $config_file)) {
    Write-Host "[!] ERROR: No se encuentra $config_file" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Archivo de configuracion encontrado" -ForegroundColor Green

# Paso 2: Resumen
Write-Host ""
Write-Host "CAMBIOS PRINCIPALES:" -ForegroundColor Cyan
Write-Host "  * BTC: cooldown 60min -> 45min, risk_aversion 1.5 -> 1.2"
Write-Host "  * ETH: cooldown 90min -> 45min, risk_aversion 1.3 -> 0.9 (MAS ACTIVO)"
Write-Host "  * SOL: cooldown 120min -> 75min, risk_aversion 1.2 -> 1.0"
Write-Host ""

# Paso 3: Confirmacion
$confirm = Read-Host "Desea desplegar esta configuracion al VPS? (s/n)"
if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "[-] Operacion cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host ">>> Iniciando despliegue..." -ForegroundColor Green

# Paso 4: Transferencia
$target = "${vps_user}@${vps_host}:${vps_path}/config/"
Write-Host ">>> Enviando config/assets.py al VPS..." -ForegroundColor Yellow
scp $config_file $target

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] ERROR al transferir archivo" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Transferencia completada" -ForegroundColor Green

# Paso 5: Reinicio
Write-Host ""
Write-Host ">>> Reiniciando bots en el VPS..." -ForegroundColor Yellow
$ssh_cmd = "docker restart trader_btc trader_eth trader_sol"
ssh "${vps_user}@${vps_host}" $ssh_cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] Bots reiniciados exitosamente" -ForegroundColor Green
}
else {
    Write-Host "[!] Hubo un problema al reiniciar los bots" -ForegroundColor Yellow
}

Write-Host ""
Write-Host ">>> Verificando estado (esperando 5s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
ssh "${vps_user}@${vps_host}" "docker ps -a"

Write-Host ""
Write-Host ">>> OPTIMIZACION APLICADA CON EXITO <<<" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "  1. Ver logs de ETH: docker logs -f trader_eth"
Write-Host "  2. Ver TensorBoard: http://$vps_host:6006"
Write-Host ""
Write-Host "Nota: Si ves errores de 'grep', ignoralos. Solo fijate en el balance." -ForegroundColor Gray
Write-Host ""
