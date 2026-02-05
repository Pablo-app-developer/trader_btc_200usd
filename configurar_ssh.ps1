# Script para configurar autenticación SSH sin contraseña
# Versión corregida para PowerShell

Write-Host ""
Write-Host "=== CONFIGURACIÓN DE LLAVE SSH ===" -ForegroundColor Cyan
Write-Host "Este script configurará autenticación automática sin contraseña" -ForegroundColor Yellow
Write-Host ""

$VPS_IP = "107.174.133.37"
$VPS_USER = "root"
$SSH_DIR = "$env:USERPROFILE\.ssh"
$SSH_KEY_PATH = "$SSH_DIR\id_rsa"

# Crear directorio .ssh si no existe
if (-not (Test-Path $SSH_DIR)) {
    New-Item -ItemType Directory -Path $SSH_DIR | Out-Null
}

# Paso 1: Verificar si ya existe una llave SSH
if (Test-Path "$SSH_KEY_PATH.pub") {
    Write-Host "[OK] Ya tienes una llave SSH en: $SSH_KEY_PATH" -ForegroundColor Green
    Write-Host ""
}
else {
    Write-Host "[1] Generando nueva llave SSH..." -ForegroundColor Yellow
    Write-Host "IMPORTANTE: Cuando te pida passphrase, presiona ENTER (déjalo vacío)" -ForegroundColor White
    Write-Host ""
    
    ssh-keygen -t rsa -b 4096 -f $SSH_KEY_PATH -N '""'
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Llave SSH generada exitosamente" -ForegroundColor Green
        Write-Host ""
    }
    else {
        Write-Host ""
        Write-Host "[ERROR] No se pudo generar la llave SSH" -ForegroundColor Red
        exit 1
    }
}

# Paso 2: Copiar llave al VPS
Write-Host "[2] Copiando llave pública al VPS..." -ForegroundColor Yellow
Write-Host "Se te pedirá la contraseña del VPS UNA ÚLTIMA VEZ" -ForegroundColor White
Write-Host ""

# Leer la llave pública
$publicKey = Get-Content "$SSH_KEY_PATH.pub" -Raw
$publicKey = $publicKey.Trim()

# Comando para ejecutar en el VPS (sin operadores && que PowerShell no entiende)
Write-Host "Ejecutando comandos en el VPS..." -ForegroundColor Gray

# Ejecutar comandos uno por uno
ssh "$VPS_USER@$VPS_IP" "mkdir -p ~/.ssh"
ssh "$VPS_USER@$VPS_IP" "chmod 700 ~/.ssh"
ssh "$VPS_USER@$VPS_IP" "echo '$publicKey' >> ~/.ssh/authorized_keys"
ssh "$VPS_USER@$VPS_IP" "chmod 600 ~/.ssh/authorized_keys"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Configuración completada!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ahora puedes conectarte sin contraseña:" -ForegroundColor Cyan
    Write-Host "  ssh $VPS_USER@$VPS_IP" -ForegroundColor White
    Write-Host ""
    Write-Host "Probando conexión automática..." -ForegroundColor Yellow
    
    $testResult = ssh "$VPS_USER@$VPS_IP" "echo 'Conexion exitosa sin contraseña'"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] $testResult" -ForegroundColor Green
        Write-Host ""
        Write-Host "Ahora todos los scripts funcionarán sin pedir contraseña!" -ForegroundColor Cyan
    }
}
else {
    Write-Host ""
    Write-Host "[ERROR] No se pudo copiar la llave. Verifica la contraseña." -ForegroundColor Red
}

Write-Host ""
