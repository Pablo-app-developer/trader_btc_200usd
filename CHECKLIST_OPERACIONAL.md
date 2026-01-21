# ✅ Checklist Operacional - Bot de Trading

## 📅 Rutina Diaria Recomendada

### 🌅 Inicio del Día

- [ ] **Verificar estado del sistema**
  ```bash
  ./manage_bot.sh status
  ```
  ✅ Todos los bots deben estar "RUNNING"

- [ ] **Health check completo**
  ```bash
  ./manage_bot.sh health
  ```
  ✅ Sin errores en última hora  
  ✅ Espacio en disco > 10%  
  ✅ Memoria libre > 20%

- [ ] **Revisar TensorBoard**
  ```
  http://107.174.133.37:6006
  ```
  ✅ Gráfica de balance ascendente  
  ✅ Win rate > 50%  
  ✅ Drawdown < 5%

- [ ] **Revisar logs**
  ```bash
  ./manage_bot.sh logs btc | tail -20
  ./manage_bot.sh logs eth | tail -20
  ./manage_bot.sh logs sol | tail -20
  ```
  ✅ Sin errores críticos  
  ✅ Bots ejecutando trades normalmente

---

### 🕐 Durante el Día

- [ ] **Monitoreo cada 4-6 horas**
  ```bash
  # Estado rápido
  ./manage_bot.sh status
  ```

- [ ] **Verificar notificaciones** (si están configuradas)
  - Telegram
  - Email
  - Discord

- [ ] **Revisar métricas clave en TensorBoard**
  - Balance actual
  - Trades ejecutados hoy
  - Drawdown diario

---

### 🌙 Fin del Día

- [ ] **Reporte de performance diaria**
  ```bash
  # Ver logs del día
  ssh root@107.174.133.37 'cd /root/sol-bot-200 && grep "$(date +%Y-%m-%d)" live_trader.log'
  ```

- [ ] **Backup semanal (viernes)**
  ```bash
  ./manage_bot.sh backup
  ```

- [ ] **Verificar uso de recursos**
  ```bash
  ./manage_bot.sh stats
  ```
  ✅ CPU < 80%  
  ✅ RAM < 80%  
  ✅ Disco < 90%

---

## 🚨 Checklist de Emergencia

### ❌ Bot Detenido

1. [ ] Verificar logs
   ```bash
   ./manage_bot.sh logs <bot>
   ```

2. [ ] Reiniciar bot
   ```bash
   ./manage_bot.sh restart <bot>
   ```

3. [ ] Si persiste, redesplegar
   ```bash
   ./manage_bot.sh deploy
   ```

### ❌ VPS No Responde

1. [ ] Verificar conectividad
   ```bash
   ./verify_vps.sh
   ```

2. [ ] Intentar conexión SSH
   ```bash
   ./connect_vps.sh
   ```

3. [ ] Contactar proveedor de VPS si no hay respuesta

### ❌ Errores de API

1. [ ] Verificar que Yahoo Finance esté funcionando
   ```bash
   curl -I https://finance.yahoo.com
   ```

2. [ ] Revisar logs para errores específicos
   ```bash
   ./manage_bot.sh logs <bot> | grep -i "error\|exception"
   ```

3. [ ] Reiniciar bot afectado
   ```bash
   ./manage_bot.sh restart <bot>
   ```

### ❌ Pérdidas Excesivas

1. [ ] **DETENER INMEDIATAMENTE**
   ```bash
   ./manage_bot.sh stop all
   ```

2. [ ] Revisar logs y TensorBoard
   ```bash
   # Analizar últimos trades
   ./manage_bot.sh logs <bot> | tail -100
   ```

3. [ ] Analizar configuración
   ```python
   # Revisar config/assets.py
   # Verificar parámetros de riesgo
   ```

4. [ ] Hacer backtesting con datos recientes
   ```bash
   python backtest.py <ASSET>
   ```

5. [ ] Ajustar estrategia si es necesario

---

## 📊 Checklist de Mantenimiento

### Semanal

- [ ] **Lunes**: Revisar performance de la semana anterior
- [ ] **Miércoles**: Health check profundo
  ```bash
  ./manage_bot.sh health
  ```
- [ ] **Viernes**: Backup de modelos
  ```bash
  ./manage_bot.sh backup
  ```

### Mensual

- [ ] **Actualizar dependencias**
  ```bash
  ssh root@107.174.133.37 'cd /root/sol-bot-200 && pip3 install -r requirements.txt --upgrade'
  ```

- [ ] **Limpiar logs antiguos**
  ```bash
  ssh root@107.174.133.37 'find /root/sol-bot-200 -name "*.log" -mtime +30 -delete'
  ```

- [ ] **Reentrenar modelos** (opcional)
  ```bash
  # En local
  python train_production.py BTC --steps 200000
  python train_production.py ETH --steps 200000
  python train_production.py SOL --steps 200000
  
  # Desplegar al VPS
  ./deploy_to_vps.sh
  ```

- [ ] **Limpiar Docker**
  ```bash
  ./manage_bot.sh clean
  ```

- [ ] **Auditoría de seguridad**
  - Cambiar contraseñas SSH si es necesario
  - Revisar logs de acceso
  - Verificar firewall

---

## 🎯 Métricas Clave a Monitorear

### Performance del Bot

| Métrica | Objetivo | Alerta si |
|---------|----------|-----------|
| **Win Rate** | > 55% | < 45% |
| **Drawdown Diario** | < 3% | > 5% |
| **Sharpe Ratio** | > 1.0 | < 0.5 |
| **ROI Mensual** | > 3% | < 0% |
| **Trades por día** | 5-15 | < 2 o > 30 |

### Sistema

| Métrica | Objetivo | Alerta si |
|---------|----------|-----------|
| **Uptime** | > 99% | < 95% |
| **CPU Usage** | < 70% | > 85% |
| **RAM Usage** | < 70% | > 85% |
| **Disk Usage** | < 80% | > 90% |
| **Errores por día** | < 5 | > 20 |

---

## 📱 Comandos de Acceso Rápido

### En Cualquier Momento

```bash
# Estado general
./manage_bot.sh status

# Logs en vivo
./manage_bot.sh logs btc -f

# Health check
./manage_bot.sh health

# Estadísticas
./manage_bot.sh stats
```

### Desde el VPS

```bash
# Conectar
ssh root@107.174.133.37

# Ver procesos
docker ps

# Logs de un bot específico
docker logs -f trader_btc

# Reiniciar Docker
systemctl restart docker
```

---

## 🔔 Configurar Alertas (Recomendado)

### Opción 1: Telegram Bot (Recomendado)
- [ ] Crear bot en Telegram (@BotFather)
- [ ] Obtener token y chat_id
- [ ] Agregar al código de notificaciones
- [ ] Probar envío de mensajes

### Opción 2: Email
- [ ] Configurar SMTP
- [ ] Agregar email de destino
- [ ] Configurar alertas críticas

### Opción 3: Discord Webhook
- [ ] Crear webhook en Discord
- [ ] Integrar en el código
- [ ] Testear notificaciones

---

## 🎓 Mejores Prácticas

### ✅ DO (Hacer)
- ✅ Revisar bots al menos 2 veces al día
- ✅ Hacer backup semanal de modelos
- ✅ Mantener logs actualizados
- ✅ Monitorear TensorBoard regularmente
- ✅ Documentar cambios importantes
- ✅ Testear en backtesting antes de deploy

### ❌ DON'T (No Hacer)
- ❌ Dejar bots sin supervisión por más de 24h
- ❌ Hacer cambios en producción sin testear
- ❌ Ignorar errores repetidos
- ❌ Usar todo el capital en un solo activo
- ❌ Desactivar stop-loss
- ❌ Subir API keys o passwords a GitHub

---

## 📝 Template de Reporte Diario

```markdown
# Reporte Diario - [Fecha]

## Estado General
- ✅/❌ Todos los bots corriendo
- ✅/❌ Sin errores críticos
- ✅/❌ Rendimiento dentro de objetivos

## Métricas del Día
- **BTC**: [Win Rate] | [PnL] | [Trades]
- **ETH**: [Win Rate] | [PnL] | [Trades]
- **SOL**: [Win Rate] | [PnL] | [Trades]

## Eventos Importantes
- [Listar eventos: trades grandes, errores, cambios]

## Acciones Tomadas
- [Listar acciones: reinicio, ajustes, etc.]

## Próximos Pasos
- [Tareas pendientes]
```

---

## 🚀 Quick Start - Tu Primera Vez

Si es tu primera vez usando el sistema:

1. [ ] Leer `MAPA_SISTEMA.md` para entender la arquitectura
2. [ ] Ejecutar `./verify_vps.sh` para verificar todo está OK
3. [ ] Ejecutar `./manage_bot.sh status` para ver el estado
4. [ ] Abrir TensorBoard en http://107.174.133.37:6006
5. [ ] Ejecutar `./manage_bot.sh help` para ver todos los comandos

---

💡 *Checklist creado por Antigravity Agent - Operación Profesional de Trading Bots*
