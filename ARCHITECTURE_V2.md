# 🏗️ ARQUITECTURA DEPLOYMENT V2

Hemos migrado a una arquitectura basada en **imágenes inmutables** para mayor estabilidad.

## 📦 Componentes

1. **Dockerfile.bot**: Imagen base para los traders.
   - Base: `pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime`
   - Incluye: `pandas`, `yfinance`, `stable-baselines3`, `pyyaml`, etc.
   - Configurado para ejecutar `run_live_trader.py`

2. **Dockerfile.dashboard**: Imagen para monitoreo.
   - Base: `python:3.10-slim`
   - Incluye: `streamlit`, `plotly`, `flask`, `psutil`
   - Ejecuta Dashboard + Healthcheck

3. **docker-compose.yml**: Orquestador.
   - Construye ambas imágenes localmente en el VPS.
   - Monta el volumen `./:/app` para compartir código y bases de datos.
   - Define límites de memoria (2GB por bot).

## 🔄 Flujo de Datos

```
[Trader SOL] --> Escribe --> /app/trading_bot_sol.db (Host)
[Trader ETH] --> Escribe --> /app/trading_bot_eth.db (Host)
[Trader BTC] --> Escribe --> /app/trading_bot_btc.db (Host)

[Dashboard]  --> Lee --> /app/trading_bot_*.db (Host)
```

## 🛠️ Comandos de Mantenimiento

**Reconstruir y reiniciar todo:**
```bash
cd /root/sol-bot-200
docker-compose down
docker-compose up -d --build
```

**Ver logs de un bot:**
```bash
docker logs trader_sol_200usd --tail 50 -f
```

**Ver logs del dashboard:**
```bash
docker logs dashboard_200usd --tail 50 -f
```
