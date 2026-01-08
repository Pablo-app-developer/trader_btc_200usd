from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class AssetConfig:
    name: str
    env_params: Dict[str, Any]
    steps: int = 150000

# Configuration Store
ASSETS = {
    "BTC": AssetConfig(
        name="BTC",
        env_params={
            "cooldown_steps": 2,
            "stop_loss": 0.05,
            "trailing_stop_drop": 0.10,
            "risk_aversion": 1.6,
            "ema_penalty": 0.005,
            "vol_penalty": 0.02
        }
    ),
    "SOL": AssetConfig(
        name="SOL",
        env_params={
            "cooldown_steps": 8,
            "stop_loss": 0.03,
            "trailing_stop_drop": 0.015,
            "risk_aversion": 1.2,
            "ema_penalty": 0.03,
            "vol_penalty": 0.05
        }
    ),
    "ETH": AssetConfig(
        name="ETH",
        env_params={
            "cooldown_steps": 6,
            "stop_loss": 0.025,
            "trailing_stop_drop": 0.015,
            "risk_aversion": 1.3,
            "ema_penalty": 0.03,
            "vol_penalty": 0.04
        }
    )
}

def get_asset_config(symbol_name: str) -> Optional[AssetConfig]:
    """Retrieve configuration for a specific asset (case-insensitive)."""
    return ASSETS.get(symbol_name.upper())
