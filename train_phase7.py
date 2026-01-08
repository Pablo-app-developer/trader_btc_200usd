import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
from trading_env import TradingEnv

def train_phase7_evolution():
    print("🚀 Iniciando Fase 7: Evolución Técnica y Filtro de Tendencia (EMA 200 + Trailing Stop)...")
    
    # 1. Cargar Datos
    try:
        df = pd.read_csv("datos_btc_15m_binance.csv")
    except FileNotFoundError:
        print("❌ Data not found.")
        return

    # Split Data (80/20)
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_val = df.iloc[split_idx:]
    
    # Entorno con fricción institucional
    env_train = DummyVecEnv([lambda: TradingEnv(df_train, commission=0.0005)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val, commission=0.0005)])

    # 2. CARGAR CEREBRO MAESTRO (Phase 6.1 FIXED)
    model_path = "models/BTC/ppo_btc_phase6_ULTIMATE_FIXED.zip"
    if not os.path.exists(model_path):
        print(f"❌ Modelo base no encontrado en {model_path}")
        return
        
    print(f"📥 Evolucionando cerebro FIXED: {model_path}")
    
    # Cargamos el modelo
    model = PPO.load(model_path, env=env_train)
    
    # 3. HIPERPARÁMETROS DE ESPECIALIZACIÓN (Fine-Tuning)
    model.learning_rate = 0.00002 # Aún más lento para no romper la disciplina previa
    model.ent_coef = 0.004 # Reducimos un poco más la exploración
    model.batch_size = 128 

    # Setup Log Dir
    log_dir = "./tensorboard_logs/"
    os.makedirs(log_dir, exist_ok=True)

    # 4. Callbacks
    eval_callback = EvalCallback(
        env_val, 
        best_model_save_path='./models/BTC/best_ppo_btc_phase7',
        log_path=log_dir, 
        eval_freq=10000,
        deterministic=True
    )
    
    # 5. Entrenar 500,000 pasos
    print("🧠 Entrenando 500k pasos de Evolución Técnica...")
    model.learn(
        total_timesteps=500000, 
        reset_num_timesteps=False,
        callback=eval_callback,
        tb_log_name="PPO_Phase7_EVO"
    )
    
    # 6. Guardar el modelo definitivo
    model.save("models/BTC/ppo_btc_phase7_EVO")
    print("✅ Modelo Phase 7 EVO guardado en models/BTC/ppo_btc_phase7_EVO.zip")

if __name__ == "__main__":
    train_phase7_evolution()
