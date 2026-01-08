import gymnasium as gym
import pandas as pd
import numpy as np
import os
import json
import argparse
from typing import Dict, Any, Optional

from stable_baselines3 import PPO, A2C
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback

# Import custom environment
from trading_env import TradingEnv
# Import new configuration system
from config import get_asset_config

def load_hyperparams(symbol_name: str) -> Dict[str, Any]:
    """Load hyperparameters from JSON file or return default defaults."""
    hyperparams_file = f"best_hyperparams_{symbol_name.lower()}.json"
    
    if os.path.exists(hyperparams_file):
        print(f"💎 ¡ENCONTRADA CONFIGURACIÓN ESPECIALISTA! Cargando {hyperparams_file}...")
        with open(hyperparams_file, "r") as f:
            return json.load(f)
    elif os.path.exists("best_hyperparams.json"):
        print("⚠️ No se encontró config específica. Usando 'best_hyperparams.json' genérico.")
        with open("best_hyperparams.json", "r") as f:
            return json.load(f)
    else:
        print("⚠️⚠️ ALERTA: No se encontraron hiperparámetros. Usando valores por defecto de PPO.")
        return {}

def train_production_asset(symbol_name: str, total_timesteps: Optional[int] = None):
    symbol_name = symbol_name.upper()
    print(f"\n🚀 Iniciando Entrenamiento de PRODUCCIÓN para {symbol_name}...")
    
    # 1. Load Asset Configuration
    config = get_asset_config(symbol_name)
    if not config:
        print(f"❌ Error: No configuration found for asset '{symbol_name}'. Adding generic default.")
        # Fallback logic could go here, but for strict production we exit
        return

    # Override steps if provided via CLI, else use config default
    prod_steps = total_timesteps if total_timesteps else config.steps
    
    print(f"🎯 AJUSTE DE ÉLITE para {symbol_name}: Cfr. config/assets.py")
    print(f"   Steps: {prod_steps}")
    print(f"   Env Params: {config.env_params}")

    # 2. Data Loading
    data_file = f"datos_{symbol_name.lower()}_15m_binance.csv"
    if not os.path.exists(data_file):
        print(f"❌ Error: No se encuentra el archivo de datos {data_file}")
        return

    print(f"📂 Cargando datos históricos de {symbol_name} ({data_file})...")
    df = pd.read_csv(data_file)
    
    # Simple validation split (80/20) for production check
    train_size = int(len(df) * 0.8)
    df_train = df.iloc[:train_size]
    df_val = df.iloc[train_size:]

    # 3. Environment Setup
    # Create the training environment with asset-specific parameters
    env_train = DummyVecEnv([lambda: TradingEnv(df_train, **config.env_params)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val, **config.env_params)])

    # 4. Hyperparameters & Model Setup
    hyperparams = load_hyperparams(symbol_name)
    
    # Define paths for saving
    models_dir = f"models/PRODUCTION/{symbol_name}"
    log_dir = f"tensorboard_logs/PPO_Production_{symbol_name}"
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # Check for existing base models to transfer-learn from
    # Order of preference: 
    # 1. Best model for this specific asset (Phase 7/Evo)
    # 2. Production model for this asset (re-training)
    # 3. Generic BTC model (The "Teacher")
    
    base_model_paths = [
        f"models/ARCHIVE/{symbol_name}/best_model.zip",
        f"models/PRODUCTION/{symbol_name}/ppo_{symbol_name.lower()}_final.zip",
        "models/ARCHIVE/BTC/best_model_btc_phase7.zip"
    ]
    
    model = None
    for path in base_model_paths:
        if os.path.exists(path):
            print(f"♻️  Cargando modelo base para Transfer Learning desde: {path}")
            try:
                # We load without env first to avoid some warnings, then set env
                model = PPO.load(path, env=env_train, **hyperparams, tensorboard_log=log_dir)
                print("✅ Modelo cargado exitosamente.")
                break
            except Exception as e:
                print(f"⚠️ Error cargando modelo {path}: {e}")
    
    if model is None:
        print("🐣 No se encontró modelo base. Iniciando entrenamiento desde CERO (Scratch).")
        model = PPO("MlpPolicy", env=env_train, verbose=1, device="cuda", tensorboard_log=log_dir, **hyperparams)

    # 5. Callbacks
    # Save a checkpoint every 50k steps
    checkpoint_callback = CheckpointCallback(
        save_freq=50000, 
        save_path=models_dir, 
        name_prefix=f"ppo_{symbol_name.lower()}_ckpt"
    )
    
    # Eval callback to monitor performance on unseen data
    eval_callback = EvalCallback(
        env_val, 
        best_model_save_path=os.path.join(models_dir, "best_model"),
        log_path=log_dir, 
        eval_freq=10000,
        deterministic=True, 
        render=False
    )

    # 6. Training
    print(f"🧠 Entrenando {prod_steps} pasos con la configuración cargada...")
    try:
        model.learn(total_timesteps=prod_steps, callback=[checkpoint_callback, eval_callback], reset_num_timesteps=False)
        
        # 7. Final Save
        final_path = os.path.join(models_dir, f"ppo_{symbol_name.lower()}_final")
        model.save(final_path)
        print(f"💾 Modelo final guardado en: {final_path}.zip")
        print("✅ Entrenamiento de producción finalizado.")
        
    except Exception as e:
        print(f"❌ Error crítico durante el entrenamiento: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Production Bot")
    parser.add_argument("asset", type=str, help="Asset symbol (BTC, SOL, ETH)")
    parser.add_argument("--steps", type=int, default=None, help="Overide training steps")
    
    args = parser.parse_args()
    
    train_production_asset(args.asset, args.steps)
