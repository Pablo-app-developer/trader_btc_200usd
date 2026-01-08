import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
from trading_env import TradingEnv

def train_production_asset(symbol_name):
    print(f"🚀 Iniciando Entrenamiento de PRODUCCIÓN para {symbol_name.upper()}...")
    
    # 1. Cargar Datos
    filename = f"datos_{symbol_name.lower()}_15m_binance.csv"
    if not os.path.exists(filename):
        print(f"❌ {filename} no encontrado.")
        return
        
    df = pd.read_csv(filename)
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_val = df.iloc[split_idx:]
    
    # Entorno con personalización por Activo
    env_params = {
        "commission": 0.0005,
    }
    
    # Entorno con personalización por Activo (Fase 9: Estándar de Oro)
    env_params = {
        "commission": 0.0005,
    }
    
    if symbol_name.lower() == "sol":
        print(f"🎯 AJUSTE DE ÉLITE para {symbol_name.upper()}: Buscando el >5%...")
        env_params.update({
            "cooldown_steps": 8,      # Volvemos a la calma institucional para evitar sobretrading
            "stop_loss": 0.03,        
            "trailing_stop_drop": 0.015, # Cerramos beneficios más rápido
            "risk_aversion": 1.2,     # Más agresivos en la captura de ganancias
            "ema_penalty": 0.03,      # Filtro de tendencia firme
            "vol_penalty": 0.05       # No operamos en mercados muertos
        })
    elif symbol_name.lower() == "eth":
        print(f"🎯 AJUSTE DE ÉLITE para {symbol_name.upper()}: Rescatando potencia...")
        env_params.update({
            "cooldown_steps": 6,      
            "stop_loss": 0.025,       
            "trailing_stop_drop": 0.015, 
            "risk_aversion": 1.3,     
            "ema_penalty": 0.03,      
            "vol_penalty": 0.04       
        })
    else:
        # BTC SIN TOCAR
        print(f"🛡️ Manteniendo BTC intacto...")
    
    prod_steps = 150000 # Producción completa profesional

    # Inicializar Entornos
    env_train = DummyVecEnv([lambda: TradingEnv(df_train, **env_params)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val, **env_params)])

    # 2. CONFIGURACIÓN DE HIPERPARÁMETROS
    # Buscamos si existe una optimización específica para este activo
    hyperparams_file = f"best_hyperparams_{symbol_name.lower()}.json"
    if os.path.exists(hyperparams_file):
        print(f"💎 ¡ENCONTRADA CONFIGURACIÓN ESPECIALISTA! Cargando {hyperparams_file}...")
        import json
        with open(hyperparams_file, 'r') as f:
            hyperparams = json.load(f)
    else:
        print(f"🏛️ Usando Configuración Diamante Estándar (BTC)...")
        hyperparams = {
            "learning_rate": 1.128e-05,
            "ent_coef": 0.00313,
            "gamma": 0.961,
            "n_steps": 4096,
            "batch_size": 256
        }
    
    # 3. CARGAR CEREBRO BASE
    # Intentamos cargar la versión más avanzada/adecuada que tenemos disponible
    if symbol_name.lower() == "sol":
        paths_to_check = [
            f"models/ARCHIVE/SOL/ppo_sol_pro_final.zip", # Phase 6 (El ganador del 9.37%)
            f"models/ARCHIVE/SOL/ppo_sol_phase7_EVO.zip",
            f"models/ARCHIVE/BTC/ppo_btc_phase7_EVO.zip"
        ]
    else:
        paths_to_check = [
            f"models/ARCHIVE/{symbol_name.upper()}/ppo_{symbol_name.lower()}_phase7_EVO.zip",
            f"models/ARCHIVE/{symbol_name.upper()}/ppo_{symbol_name.lower()}_pro_final.zip",
            f"models/ARCHIVE/BTC/ppo_btc_phase7_EVO.zip"
        ]
    
    model = None
    for path in paths_to_check:
        if os.path.exists(path):
            print(f"📥 Cargando cerebro base adecuado para {symbol_name.upper()} desde: {path}")
            model = PPO.load(path, env=env_train, **hyperparams)
            break
            
    if model is None:
        print("⚠️ Ningún modelo base encontrado. Iniciando desde cero.")
        model = PPO("MlpPolicy", env_train, verbose=1, device="cuda", **hyperparams)

    # Setup Log Dir
    log_dir = "./tensorboard_logs/"
    os.makedirs(log_dir, exist_ok=True)

    # 4. Callbacks de Alta Precisión
    prod_dir = f"./models/PRODUCTION/{symbol_name.upper()}"
    os.makedirs(prod_dir, exist_ok=True)
    
    eval_callback = EvalCallback(
        env_val, 
        best_model_save_path=f'{prod_dir}/best_production',
        log_path=log_dir, 
        eval_freq=10000,
        deterministic=True
    )
    
    # 5. Entrenamiento de Producción (Validación rápida)
    print(f"🧠 Entrenando {prod_steps} pasos con Configuración Diamante para {symbol_name.upper()}...")
    model.learn(
        total_timesteps=prod_steps, 
        callback=eval_callback,
        tb_log_name=f"PPO_Production_{symbol_name.upper()}"
    )
    
    # 6. Guardar Modelo Final
    model_save_path = f"{prod_dir}/ppo_{symbol_name.lower()}_final"
    model.save(model_save_path)
    print(f"✅ Modelo de Producción guardado en: {model_save_path}.zip")

if __name__ == "__main__":
    import sys
    # Se puede llamar con: python train_production.py btc
    if len(sys.argv) > 1:
        train_production_asset(sys.argv[1].lower())
    else:
        # Por defecto entrenamos BTC
        train_production_asset("btc")
