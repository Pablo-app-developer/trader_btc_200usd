# Script para conectar al VPS con nueva contraseña
# Ejecuta este script y te pedirá la contraseña

$VPS_IP = "107.174.133.37"
$VPS_USER = "root"

Write-Host "`n=== CONEXIÓN AL VPS ===" -ForegroundColor Cyan
Write-Host "Conectando a: $VPS_USER@$VPS_IP" -ForegroundColor Yellow
Write-Host ""
Write-Host "Se te pedirá la contraseña del VPS..." -ForegroundColor White
Write-Host ""

# Conectar con SSH (pedirá contraseña interactivamente)
ssh "$VPS_USER@$VPS_IP"
