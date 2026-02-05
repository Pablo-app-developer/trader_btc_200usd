# 🏆 Antigravity FTMO Challenger

**Objetivo:** Pasar el desafío de fondeo de FTMO ($10,000) utilizando Inteligencia Artificial conservadora y gestión de riesgo estricta.

## 🎯 Metas del Proyecto
1. **Profit Target:** $1,000 (10%)
2. **Protección:** NUNCA perder más de $500 en un día (5%).
3. **Consistencia:** Ganar a través de matemáticas y probabilidad, no suerte.

## 🏗 Arquitectura V2 (Clean & Modular)

Este proyecto es una reingeniería completa basada en la experiencia previa.

```
antigravity-ftmo-10k/
├── config/          # Reglas de riesgo FTMO centralizadas
├── docker/          # Entorno reproducible 100%
├── src/             
│   ├── core/        # Ejecución y Base de Datos (SQLite)
│   ├── strategy/    # Lógica de Trading (PPO/RL)
│   └── dashboard/   # Panel de Control Web
└── data/            # Registros inmutables
```

## 🛡️ Gestión de Riesgo (FTMO Rules)
El sistema está diseñado para **auto-bloquearse** si se acerca a los límites de pérdida.

- **Riesgo por operación:** 0.5% ($50 USD)
- **Límite Diario (Soft):** 4.5% ($450 USD) -> Bot deja de operar.
- **Límite Diario (Hard):** 4.8% ($480 USD) -> Cierra todas las posiciones.

## 🚀 Tecnologías
- **Core:** Python 3.10
- **AI:** Stable-Baselines3 (PPO), PyTorch
- **Data:** SQLite, Pandas
- **Dashboard:** Streamlit + Plotly
- **Deploy:** Docker Compose (VPS)

## 🚦 Pasos para Iniciar
1. Configurar credenciales en `.env` (no incluido en repo)
2. Construir contenedores: `docker-compose build`
3. Iniciar sistema: `docker-compose up -d`
4. Monitorear: `http://localhost:8501`
