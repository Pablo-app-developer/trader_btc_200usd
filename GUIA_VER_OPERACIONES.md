# 📊 Guía: Cómo Ver las Operaciones del Bot en el VPS

## 🚀 Opción 1: Conexión Manual (Recomendado)

### Paso 1: Conectarse al VPS
```bash
ssh root@107.174.133.202
```
Te pedirá la contraseña del VPS.

### Paso 2: Una vez conectado, ejecuta estos comandos

#### Ver estado general de los bots:
```bash
docker ps -a
```
✅ Verifica que los contenedores estén "Up"

---

#### Ver las últimas operaciones de cada bot:

**BTC:**
```bash
docker logs trader_btc | grep -E "COMPRA|VENTA|SEÑAL" | tail -20
```

**ETH:**
```bash
docker logs trader_eth | grep -E "COMPRA|VENTA|SEÑAL" | tail -20
```

**SOL:**
```bash
docker logs trader_sol | grep -E "COMPRA|VENTA|SEÑAL" | tail -20
```

---

#### Ver balance y performance:

**BTC:**
```bash
docker logs trader_btc | grep -E "Balance|WinRate|PnL" | tail -10
```

**ETH:**
```bash
docker logs trader_eth | grep -E "Balance|WinRate|PnL" | tail -10
```

**SOL:**
```bash
docker logs trader_sol | grep -E "Balance|WinRate|PnL" | tail -10
```

---

#### Ver logs en tiempo real (monitoreo en vivo):
```bash
# Elige uno de estos:
docker logs -f trader_btc    # BTC en vivo
docker logs -f trader_eth    # ETH en vivo
docker logs -f trader_sol    # SOL en vivo
```
*Presiona `Ctrl+C` para salir*

---

## 🚀 Opción 2: Script Automático

Si tienes configurado SSH sin contraseña o con clave, puedes usar:

### En Windows (Git Bash o WSL):
```bash
bash revisar_operaciones.sh
```

### En Linux/Mac:
```bash
chmod +x revisar_operaciones.sh
./revisar_operaciones.sh
```

---

## 📈 Opción 3: Ver TensorBoard (Visual)

Abre tu navegador y visita:
```
http://107.174.133.202:6006
```

Aquí verás:
- 📊 Gráficas de balance
- 📈 Win Rate
- 📉 Drawdown
- 🔄 Trades ejecutados

---

## 🔍 Comandos Útiles Adicionales

### Ver solo trades del día de hoy:
```bash
docker logs trader_btc | grep "$(date +%Y-%m-%d)" | grep -E "COMPRA|VENTA"
```

### Ver los últimos 100 logs completos:
```bash
docker logs --tail 100 trader_btc
```

### Ver errores de las últimas 24 horas:
```bash
docker logs --since 24h trader_btc 2>&1 | grep -i "error\|exception"
```

### Ver estadísticas de recursos:
```bash
docker stats trader_btc trader_eth trader_sol
```

### Buscar trades específicos con beneficio:
```bash
docker logs trader_btc | grep "PnL:" | grep -E "\+[0-9]"
```

---

## 📝 Qué Buscar en los Logs

### ✅ Señales Positivas:
```
🟢 [COMPRA] SEÑAL DETECTADA
🔴 [VENTA] SEÑAL DETECTADA
💰 Cierre. PnL: +2.5%
📊 ESTADO: WinRate: 60.0%
Balance Sim: $102,500.00
```

### ⚠️ Señales de Atención:
```
❄️ Enfriamiento activo
🛡️ STOP LOSS ACTIVADO
⚠️ PELIGRO PROP FIRM: Drawdown Diario al 4.5%
Error descargando datos
```

### 💤 Estado Normal (Sin actividad):
```
⏳ Analizando mercado
Hold
Esperando condiciones de mercado
```

---

## 🎯 Interpretación de Resultados

### Balance Simulado:
- **Inicio**: $100,000
- **Meta mensual**: > $103,000 (+3%)
- **Alerta**: < $95,000 (-5%)

### Win Rate:
- **Excelente**: > 60%
- **Bueno**: 50-60%
- **Regular**: 40-50%
- **Preocupante**: < 40%

### Drawdown Diario:
- **Seguro**: < 2%
- **Aceptable**: 2-4%
- **Límite**: 5%
- **PELIGRO**: > 5%

---

## 💡 Tips

1. **Revisa al menos 2 veces al día** (mañana y noche)
2. **Monitorea TensorBoard** para ver tendencias
3. **Si ves muchos errores**, considera reiniciar el bot
4. **Si el Win Rate < 40%**, revisa la estrategia
5. **Si Drawdown > 5%**, considera detener el bot

---

## 🆘 Si Algo Sale Mal

```bash
# Reiniciar un bot específico
docker restart trader_btc

# Reiniciar todos
docker restart trader_btc trader_eth trader_sol

# Ver qué pasó antes del problema
docker logs --tail 200 trader_btc

# Detener todo si es necesario
docker stop trader_btc trader_eth trader_sol
```

---

## 📞 Acceso Rápido

**VPS IP**: 107.174.133.202  
**Usuario**: root  
**TensorBoard**: http://107.174.133.202:6006

---

💡 *Guía creada por Antigravity Agent - Monitoreo Profesional de Trading Bots*
