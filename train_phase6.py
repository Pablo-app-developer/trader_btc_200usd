import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from trading_env import TradingEnv

def train_pro_evolution():
    print("🚀 Iniciando Fase 6: Optimización Institucional y Blindaje de Capital...")
    
    # 1. Cargar Datos con EMA 200
    try:
        df = pd.read_csv("datos_btc_15m_binance.csv")
    except FileNotFoundError:
        print("❌ Data not found. Run download_data_binance.py first.")
        return

    # Split Data (80/20)
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_val = df.iloc[split_idx:]
    
    env_train = DummyVecEnv([lambda: TradingEnv(df_train)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val)])

    # 2. CARGAR MODELO "GOLDEN" (Phase 5 best)
    model_path = "models/ppo_btc_phase4_GOLDEN.zip"
    if not os.path.exists(model_path):
        print(f"❌ Modelo base no encontrado en {model_path}")
        return
        
    print(f"📥 Reiniciando desde GOLDEN (Fase 5): {model_path}")
    
    # Entorno con FRICCIÓN AUMENTADA (Realistic Training)
    env_train = DummyVecEnv([lambda: TradingEnv(df_train, commission=0.0005)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val, commission=0.0005)])

    # Cargamos el modelo
    model = PPO.load(model_path, env=env_train)
    
    # 3. HIPERPARÁMETROS DE REFINAMIENTO (Phase 6.1)
    model.learning_rate = 0.00003 
    model.ent_coef = 0.005 
    model.batch_size = 128 
    
    # Setup Log Dir
    log_dir = "./tensorboard_logs/"
    os.makedirs(log_dir, exist_ok=True)

    # 4. Callbacks
    eval_callback = EvalCallback(
        env_val, 
        best_model_save_path='./models/best_ppo_btc_phase6.1',
        log_path=log_dir, 
        eval_freq=10000,
        deterministic=True, 
        render=False
    )
    
    # 5. Entrenar otros 500,000 pasos
    print("🧠 Entrenando 500k pasos (Fine-Tuning v6.1)...")
    model.learn(
        total_timesteps=500000, 
        reset_num_timesteps=False,
        callback=eval_callback,
        tb_log_name="PPO_Phase6_1_FIXED"
    )
    
    # 6. Guardar el modelo definitivo
    model.save("models/ppo_btc_phase6_ULTIMATE_FIXED")
    print("✅ Modelo ULTIMATE FIXED guardado.")

if __name__ == "__main__":
    train_pro_evolution()
