from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class AssetConfig:
    name: str
    env_params: Dict[str, Any]
    steps: int = 150000

# CONFIGURACION: MODO AGRESIVO INSTITUCIONAL (21 Ene 2026)
# Objetivo: Aumentar la frecuencia de trades para alcanzar ROI de 5-8% mensual
ASSETS = {
    "BTC": AssetConfig(
        name="BTC",
        env_params={
            "cooldown_steps": 3,      # 45 min de espera (Antes 60)
            "stop_loss": 0.035,       # Seguridad 3.5%
            "trailing_stop_drop": 0.02,
            "risk_aversion": 1.0,     # Mas agresivo (Antes 1.5)
            "ema_penalty": 0.002,     # Filtro mas suave
            "vol_penalty": 0.01       # Menos miedo a la volatilidad
        }
    ),
    "SOL": AssetConfig(
        name="SOL",
        env_params={
            "cooldown_steps": 4,      # 60 min (Antes 120)
            "stop_loss": 0.03,        # Seguridad 3.0%
            "trailing_stop_drop": 0.015,
            "risk_aversion": 0.8,     # Mucho mas agresivo (Antes 1.2)
            "ema_penalty": 0.01,      # Reduccion del 60% en penalizacion
            "vol_penalty": 0.02
        }
    ),
    "ETH": AssetConfig(
        name="ETH",
        env_params={
            "cooldown_steps": 3,      # 45 min (Antes 90)
            "stop_loss": 0.03,        # Seguridad 3.0%
            "trailing_stop_drop": 0.015,
            "risk_aversion": 0.7,     # El mas agresivo (IA tiene permiso total)
            "ema_penalty": 0.005,     # Reduccion masiva para reactivar ETH
            "vol_penalty": 0.015
        }
    )
}

def get_asset_config(symbol_name: str) -> Optional[AssetConfig]:
    return ASSETS.get(symbol_name.upper())
