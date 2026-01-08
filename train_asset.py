import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
from trading_env import TradingEnv

def train_asset_evolution(symbol_name):
    print(f"🚀 Iniciando Entrenamiento de {symbol_name.upper()} - Enfoque Profesional...")
    
    filename = f"datos_{symbol_name}_15m_binance.csv"
    if not os.path.exists(filename):
        print(f"❌ {filename} no encontrado. Ejecuta `python download_multi_data.py`.")
        return
        
    df = pd.read_csv(filename)
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_val = df.iloc[split_idx:]
    
    env_train = DummyVecEnv([lambda: TradingEnv(df_train)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val)])

    # TRANSFER LEARNING: BTC Phase 7 EVO -> TARGET ASSET
    btc_model_path = "models/BTC/ppo_btc_phase7_EVO.zip"
    model_version = "phase7_EVO"
    model_name = f"ppo_{symbol_name}_{model_version}"
    
    if os.path.exists(btc_model_path):
        print(f"🧠 Transfer Learning: Evolucionando desde el cerebro Evolucionado de BTC (Ph7)...")
        model = PPO.load(btc_model_path, env=env_train)
        model.learning_rate = 0.00002 # Fine-tuning LR
        model.ent_coef = 0.005 
    else:
        print("🆕 BTC Phase 7 not found, starting fresh.")
        model = PPO("MlpPolicy", env_train, verbose=1, device="cuda")

    log_dir = "./tensorboard_logs/"
    eval_callback = EvalCallback(env_val, best_model_save_path=f'./models/{symbol_name.upper()}/best_{model_name}', eval_freq=10000)

    # 200,000 steps for specialized fine-tuning
    model.learn(total_timesteps=200000, callback=eval_callback, tb_log_name=f"PPO_{model_name}")
    model.save(f"models/{symbol_name.upper()}/{model_name}")
    print(f"✅ Modelo {model_name} guardado en models/{symbol_name.upper()}/")

if __name__ == "__main__":
    import sys
    # Example: python train_asset.py sol
    if len(sys.argv) > 1:
        train_asset_evolution(sys.argv[1].lower())
    else:
        print("Uso: python train_asset.py [eth|sol|link]")
