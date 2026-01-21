# 🗺️ Mapa del Sistema de Trading - Bot Antigravity

## 📊 Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                     TU MÁQUINA LOCAL                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📁 Proyecto: bot-ml-antigravity-200usd/                        │
│  ├── 🤖 Bots                                                    │
│  │   ├── sol_sniper_bot.py     (Breakout Strategy)             │
│  │   └── run_live_trader.py    (RL Multi-Asset)                │
│  │                                                               │
│  ├── 🧠 Modelos IA                                              │
│  │   └── models/PRODUCTION/                                     │
│  │       ├── BTC/ppo_btc_final.zip                              │
│  │       ├── ETH/ppo_eth_final.zip                              │
│  │       └── SOL/ppo_sol_final.zip                              │
│  │                                                               │
│  ├── ⚙️  Configuración                                           │
│  │   ├── config/assets.py      (Parámetros por cripto)         │
│  │   └── docker-compose.yml    (Orquestación)                  │
│  │                                                               │
│  └── 🛠️ Scripts de Gestión                                      │
│      ├── manage_bot.sh         (🆕 NUEVO - Gestión unificada)  │
│      ├── deploy_to_vps.sh      (🆕 Deploy automático)          │
│      ├── connect_vps.sh        (🆕 Conexión rápida)            │
│      └── verify_vps.sh         (🆕 Verificación completa)      │
│                                                                  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   │ 🌐 SSH/SCP
                   │ (107.174.133.37)
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VPS (107.174.133.37)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🐳 Docker Containers                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ trader_btc   │  │ trader_eth   │  │ trader_sol   │         │
│  │              │  │              │  │              │         │
│  │ 🪙 BTC Bot  │  │ 💎 ETH Bot  │  │ ☀️  SOL Bot  │         │
│  │ RL Model     │  │ RL Model     │  │ RL Model     │         │
│  │ 1GB RAM      │  │ 1GB RAM      │  │ 1GB RAM      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                  │
│         └─────────────────┼─────────────────┘                  │
│                           │                                     │
│                           ▼                                     │
│                  ┌─────────────────┐                           │
│                  │  TensorBoard    │                           │
│                  │  Port: 6006     │                           │
│                  │  📊 Dashboards  │                           │
│                  └─────────────────┘                           │
│                                                                  │
│  📁 Estructura de Archivos                                      │
│  /root/sol-bot-200/                                             │
│  ├── sol_sniper_bot.py                                          │
│  ├── run_live_trader.py                                         │
│  ├── models/PRODUCTION/                                         │
│  ├── tensorboard_logs/                                          │
│  ├── bot_output.log                                             │
│  └── live_trader.log                                            │
│                                                                  │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    │ 🌍 Internet
                    ▼
           ┌─────────────────┐
           │ Yahoo Finance   │
           │ (Market Data)   │
           └─────────────────┘
```

---

## 🔄 Flujo de Trabajo

### 1️⃣ **Desarrollo Local**
```
[TU PC] 
    │
    ├─► Entrenar modelos: python train_production.py BTC
    ├─► Backtesting: python backtest.py BTC
    ├─► Optimizar: python optimize_eth.py
    └─► Generar reportes: python generate_report.py
```

### 2️⃣ **Despliegue a VPS**
```
[TU PC]
    │
    └─► ./deploy_to_vps.sh
            │
            ├─► Comprime archivos
            ├─► Transfiere via SCP
            ├─► Descomprime en VPS
            ├─► Instala dependencias
            └─► Reinicia bots
                    │
                    ▼
            [VPS] Bots corriendo 24/7
```

### 3️⃣ **Operación en Producción**
```
[VPS - Docker Containers]
    │
    ├─► trader_btc ─┐
    ├─► trader_eth ─┼─► Analizan mercado cada 60s
    └─► trader_sol ─┘        │
                             ▼
                    Modelo RL predice acción
                             │
                             ├─► 🟢 BUY Signal
                             ├─► 🔴 SELL Signal
                             └─► ⚪ HOLD
                                     │
                                     ▼
                             Log en TensorBoard
                             Log en archivos
```

### 4️⃣ **Monitoreo**
```
[TÚ - Desde Cualquier Lugar]
    │
    ├─► 🌐 http://107.174.133.37:6006  (TensorBoard - Gráficas)
    ├─► 💻 ./connect_vps.sh            (SSH al VPS)
    ├─► 📊 ./manage_bot.sh status       (Estado de bots)
    └─► 📜 ./manage_bot.sh logs btc -f  (Logs en vivo)
```

---

## 🎮 Panel de Control (manage_bot.sh)

```
╔════════════════════════════════════════╗
║  🤖 ANTIGRAVITY BOT MANAGEMENT        ║
╚════════════════════════════════════════╝

📱 GESTIÓN:
  └─► start <bot>      ──► Iniciar bots
  └─► stop <bot>       ──► Detener bots
  └─► restart <bot>    ──► Reiniciar bots
  └─► status           ──► Ver estado

📊 MONITOREO:
  └─► logs <bot> [-f]  ──► Ver logs
  └─► stats            ──► Recursos (CPU/RAM)
  └─► health           ──► Health check completo

🔧 MANTENIMIENTO:
  └─► deploy           ──► Redesplegar todo
  └─► backup           ──► Backup de modelos
  └─► clean            ──► Limpiar sistema
```

---

## 📈 Componentes Clave

### 🤖 **Bots de Trading**

| Bot | Tecnología | Estrategia | Estado |
|-----|------------|------------|--------|
| **sol_sniper_bot.py** | Python + CCXT | Volatility Breakout | ✅ Listo |
| **run_live_trader.py** | RL (PPO) + Yahoo Finance | Machine Learning | ✅ Listo |

### 🧠 **Modelos IA**

```
models/PRODUCTION/
├── BTC/
│   └── ppo_btc_final.zip     (💎 Gold Standard)
├── ETH/
│   └── ppo_eth_final.zip     (⚖️ Elite Rescue)
└── SOL/
    └── ppo_sol_final.zip     (🚀 Elite Hybrid)
```

### ⚙️ **Configuración por Asset**

```python
# config/assets.py
ASSETS = {
    "BTC": {cooldown: 1h,  stop_loss: 3.5%, risk: Conservative},
    "ETH": {cooldown: 1.5h, stop_loss: 2.5%, risk: Balanced},
    "SOL": {cooldown: 2h,  stop_loss: 3.0%, risk: Aggressive}
}
```

---

## 🛠️ Herramientas de Gestión

### Nuevas (🆕)
| Script | Función | Plataforma |
|--------|---------|------------|
| `manage_bot.sh` | Gestión unificada completa | Linux/Mac |
| `deploy_to_vps.sh` | Deploy automático | Linux/Mac |
| `deploy_to_vps.ps1` | Deploy automático | Windows |
| `connect_vps.sh` | Conexión SSH rápida | Linux/Mac |
| `connect_vps.ps1` | Conexión SSH rápida | Windows |
| `verify_vps.sh` | Verificar estado VPS | Linux/Mac |
| `verify_vps.ps1` | Verificar estado VPS | Windows |

### Existentes (✅)
| Script | Función |
|--------|---------|
| `start_bot_vps.sh` | Iniciar SOL Sniper |
| `test_vps.sh` | Probar configuración |
| `fix_deploy.sh` | Reparar despliegue |
| `train_production.py` | Entrenar modelos |
| `backtest.py` | Backtesting |
| `optimize_*.py` | Optimización de hiperparámetros |

---

## 📊 Flujo de Datos

```
Yahoo Finance
     │
     ▼
[run_live_trader.py]
     │
     ├─► Descarga OHLCV (15m)
     ├─► Calcula indicadores (RSI, EMA, BB)
     ├─► Normaliza features
     │
     ▼
[Modelo PPO]
     │
     ├─► Procesa 60 velas históricas
     ├─► Predice acción óptima
     │
     ▼
[Execute Trade Logic]
     │
     ├─► Verifica cooldown
     ├─► Aplica stop loss
     ├─► Calcula riesgo
     │
     ▼
[Logging & Monitoring]
     │
     ├─► TensorBoard (gráficas)
     ├─► live_trader.log (archivo)
     └─► Console output
```

---

## 🔐 Seguridad

```
Archivos Sensibles (en .gitignore):
├── VPS_INFO.md           (IP y configuración)
├── CAMBIOS_IP_VPS.md     (historial de IPs)
├── .env                  (variables secretas)
├── secrets.json          (API keys)
└── deploy_*.zip          (archivos temporales)
```

---

## 📞 Acceso Rápido

### Desde Windows
```powershell
# Conectar al VPS
.\connect_vps.ps1

# Desplegar cambios
.\deploy_to_vps.ps1

# Verificar estado
.\verify_vps.ps1
```

### Desde Linux/Mac
```bash
# Conectar al VPS
./connect_vps.sh

# Desplegar cambios
./deploy_to_vps.sh

# Gestión completa
./manage_bot.sh help
```

### Desde Navegador
```
📊 TensorBoard: http://107.174.133.37:6006
```

---

## 🎯 Resumen en Una Imagen

```
┌────────────┐
│  TU PC     │  ──► Desarrollas & Entrenas modelos
└──────┬─────┘
       │ deploy
       ▼
┌────────────┐
│    VPS     │  ──► Ejecuta bots 24/7
│ (Docker)   │
└──────┬─────┘
       │ logs
       ▼
┌────────────┐
│ TensorBoard│  ──► Monitoreas en tiempo real
│  Dashboard │
└────────────┘
```

---

💡 *Mapa generado por Antigravity Agent - Arquitectura de Trading Profesional*
