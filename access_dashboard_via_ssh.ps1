# Script para acceder al Dashboard via SSH Port Forwarding
# Esto crea un túnel SSH que redirige el puerto 8501 del VPS a tu máquina local

Write-Host "🔐 Creando túnel SSH para acceder al Dashboard..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Instrucciones:" -ForegroundColor Yellow
Write-Host "1. Este script creará un túnel SSH"
Write-Host "2. Deja esta ventana abierta mientras uses el dashboard"
Write-Host "3. Abre tu navegador en: http://localhost:8501"
Write-Host "4. Presiona Ctrl+C aquí para cerrar el túnel"
Write-Host ""
Write-Host "Iniciando túnel..." -ForegroundColor Green
Write-Host ""

# Crear túnel SSH
# -L 8501:localhost:8501 = Redirige puerto 8501 del VPS al puerto 8501 local
# -L 5000:localhost:5000 = Redirige puerto 5000 del VPS al puerto 5000 local
ssh -L 8501:localhost:8501 -L 5000:localhost:5000 root@107.174.133.37 "echo '✅ Túnel SSH activo!' && echo 'Dashboard: http://localhost:8501' && echo 'Healthcheck: http://localhost:5000/health' && echo '' && echo 'Presiona Ctrl+C para cerrar el túnel' && tail -f /dev/null"
