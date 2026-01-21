# 🚀 Guía de Inicio Rápido - VPS

**Nueva IP del VPS**: `107.174.133.37`

## ⚡ Comandos Rápidos

### 1️⃣ Verificar si el VPS está funcionando
```powershell
# Windows
.\verify_vps.ps1
```

```bash
# Linux/Mac
./verify_vps.sh
```

### 2️⃣ Conectarse al VPS
```powershell
# Windows
.\connect_vps.ps1
```

```bash
# Linux/Mac  
./connect_vps.sh

# O directamente
ssh root@107.174.133.37
```

### 3️⃣ Desplegar el bot al VPS
```powershell
# Windows
.\deploy_to_vps.ps1
```

```bash
# Linux/Mac
./deploy_to_vps.sh
```

### 4️⃣ Ver logs del bot
Una vez conectado al VPS:
```bash
# Ver logs en tiempo real
tail -f /root/sol-bot-200/bot_output.log

# Ver logs de Docker
docker logs -f trader_eth
```

### 5️⃣ Monitorear entrenamiento
Abre en tu navegador:
```
http://107.174.133.37:6006
```

## 📊 Comandos Útiles en el VPS

```bash
# Ver contenedores Docker
docker ps -a

# Reiniciar un contenedor
docker restart trader_eth

# Ver uso de recursos
htop
# o
docker stats

# Limpiar espacio en disco
docker system prune -a --volumes -f

# Verificar espacio disponible
df -h

# Ver uso de memoria
free -h
```

## 🔧 Solución Rápida de Problemas

### ❌ "No se puede conectar por SSH"
```bash
# Verifica la IP
ping 107.174.133.37

# Verifica que tengas acceso SSH
ssh -v root@107.174.133.37
```

### ❌ "El bot no arranca"
```bash
# Conéctate al VPS
ssh root@107.174.133.37

# Ve al directorio del bot
cd /root/sol-bot-200

# Revisa los logs
tail -n 50 bot_output.log

# Reinicia el bot
pkill -f sol_sniper_bot.py
nohup python3 sol_sniper_bot.py > bot_output.log 2>&1 &
```

### ❌ "TensorBoard no carga"
```bash
# Verifica que el contenedor esté corriendo
docker ps | grep tensorboard

# Si no está corriendo, inícialo
docker compose up -d tensorboard
```

### ❌ "Sin espacio en disco"
```bash
# Limpia Docker
docker system prune -a --volumes -f

# Limpia logs antiguos
find /root -name "*.log" -mtime +7 -delete
```

## 📁 Archivos Importantes

- `VPS_INFO.md` - Documentación completa del VPS
- `CAMBIOS_IP_VPS.md` - Registro de cambios de IP
- `README.md` - Documentación general del proyecto

## 🔐 Seguridad

- 🔑 Usa claves SSH en lugar de contraseñas
- 🔒 Mantén el firewall activo
- 📝 No compartas la IP públicamente
- 🔄 Mantén el sistema actualizado

## 💡 Tips

1. **Antes de hacer cambios grandes**, haz un snapshot del VPS
2. **Monitorea el uso de recursos** regularmente con `htop`
3. **Revisa los logs** periódicamente para detectar problemas
4. **Documenta cualquier cambio** en la configuración

---

**¿Primera vez usando el VPS?**
1. Ejecuta `.\verify_vps.ps1` para verificar que todo funciona
2. Conéctate con `.\connect_vps.ps1`
3. Explora con `ls` y `cd`
4. Lee `VPS_INFO.md` para más detalles

💡 *Generado por Antigravity Agent*
