import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
from trading_env import TradingEnv

def train_eth_evolution():
    print("🚀 Iniciando Entrenamiento de Ethereum (ETH/USDT) - Enfoque Profesional...")
    
    # 1. Cargar Datos
    filename = "datos_eth_15m_binance.csv"
    if not os.path.exists(filename):
        print(f"❌ {filename} no encontrado. Ejecuta primero `python download_eth_data.py`.")
        return
        
    df = pd.read_csv(filename)

    # Split Data (80/20)
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_val = df.iloc[split_idx:]
    
    env_train = DummyVecEnv([lambda: TradingEnv(df_train)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val)])

    # 2. CARGANTE O TRANSFERENCIA DE CONOCIMIENTO (BTC -> ETH)
    # Los profesionales usan Transfer Learning para que la IA aplique lo aprendido en BTC a ETH.
    btc_model_path = "models/ppo_btc_phase6_ULTIMATE.zip"
    model_name = "ppo_eth_pro"
    
    if os.path.exists(btc_model_path):
        print(f"🧠 Aplicando Transfer Learning: Cargando cerebro de BTC ({btc_model_path}) para ETH...")
        model = PPO.load(btc_model_path, env=env_train)
        # Ajustes de Fine-Tuning para la nueva cripto
        model.learning_rate = 0.00002 # Aún más lento para adaptarse al nuevo "dialecto"
        model.ent_coef = 0.01 # Un poco más de exploración inicial para conocer ETH
    else:
        print("🆕 No se detectó modelo previo. Iniciando entrenamiento limpio para ETH.")
        model = PPO(
            "MlpPolicy", 
            env_train, 
            verbose=1, 
            learning_rate=0.0001,
            n_steps=2048,
            batch_size=64,
            ent_coef=0.05,
            device="cuda"
        )

    # 3. Callbacks y Logs
    log_dir = "./tensorboard_logs/"
    eval_callback = EvalCallback(
        env_val, 
        best_model_save_path=f'./models/best_{model_name}',
        log_path=log_dir, 
        eval_freq=10000,
        deterministic=True
    )

    # 4. Entrenamiento
    # Entrenamos 1,000,000 de pasos para que domine la volatilidad de Ethereum
    print(f"🧠 Entrenando {model_name} por 1,000,000 de pasos...")
    model.learn(
        total_timesteps=1000000, 
        callback=eval_callback,
        tb_log_name=f"PPO_{model_name}"
    )
    
    # 5. Guardar
    model.save(f"models/{model_name}_final")
    print(f"✅ Modelo {model_name}_final guardado. ¡Listo para conquistar el mercado de ETH!")

if __name__ == "__main__":
    train_eth_evolution()
