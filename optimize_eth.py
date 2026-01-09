import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
import pandas as pd
import numpy as np
import os
import json
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
from trading_env import TradingEnv
from config import get_asset_config

# Configuración del Experimento
N_TRIALS = 30
N_STARTUP_TRIALS = 5
N_EVALUATIONS = 2
N_TIMESTEPS = 30000 
EVAL_FREQ = 10000
TIMEOUT = 60 * 60  # 1 hora máximo

ASSET = "ETH"

def optimize_agent(trial):
    # 1. Definir Espacio de Búsqueda (Hyperparameters Search Space)
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-3, log=True)
    ent_coef = trial.suggest_float("ent_coef", 0.0001, 0.01, log=True)
    clip_range = trial.suggest_float("clip_range", 0.1, 0.4)
    gae_lambda = trial.suggest_float("gae_lambda", 0.9, 0.99)
    gamma = trial.suggest_float("gamma", 0.9, 0.9999)
    n_steps = trial.suggest_categorical("n_steps", [2048, 4096, 8192])
    batch_size = trial.suggest_categorical("batch_size", [64, 128, 256, 512])

    if batch_size > n_steps:
        batch_size = n_steps

    hyperparams = {
        "learning_rate": learning_rate,
        "ent_coef": ent_coef,
        "clip_range": clip_range,
        "gae_lambda": gae_lambda,
        "gamma": gamma,
        "n_steps": n_steps,
        "batch_size": batch_size,
    }

    # 2. Cargar Datos y Config
    data_file = f"datos_{ASSET.lower()}_15m_binance.csv"
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"No data found for {ASSET}")
        
    df = pd.read_csv(data_file)
    train_size = int(len(df) * 0.7)
    df_train = df.iloc[:train_size]
    df_val = df.iloc[train_size:]

    # Cargar Configuración de Entorno "Elite"
    config = get_asset_config(ASSET)
    env_params = config.env_params if config else {"commission": 0.0005}

    env_train = DummyVecEnv([lambda: TradingEnv(df_train, **env_params)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val, **env_params)])

    # 3. Crear Modelo
    model = PPO(
        "MlpPolicy",
        env_train,
        verbose=0,
        **hyperparams
    )

    # 4. Entrenar con Pruning (Early Stopping si va mal)
    # Custom evaluation for Optuna
    mean_reward = -np.inf
    
    try:
        model.learn(total_timesteps=N_TIMESTEPS)
        
        # Evaluar
        mean_reward, std_reward = optuna_eval(model, env_val, n_eval_episodes=5)
        
    except Exception as e:
        print(f"Trial failed: {e}")
        return -np.inf

    return mean_reward

def optuna_eval(model, env, n_eval_episodes=5):
    """Evalua el modelo y retorna el Sharpe Ratio promedio estimado (Reward acumulado)"""
    episode_rewards = []
    for _ in range(n_eval_episodes):
        obs = env.reset()
        done = False
        total_reward = 0
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            total_reward += reward
        episode_rewards.append(total_reward)
    return np.mean(episode_rewards), np.std(episode_rewards)

if __name__ == "__main__":
    print(f"🧬 Iniciando Optimización Evolutiva (Optuna) para {ASSET}...")
    
    sampler = TPESampler(n_startup_trials=N_STARTUP_TRIALS, seed=42)
    pruner = MedianPruner(n_startup_trials=N_STARTUP_TRIALS, n_warmup_steps=N_EVALUATIONS)

    study = optuna.create_study(sampler=sampler, pruner=pruner, direction="maximize")
    
    try:
        study.optimize(optimize_agent, n_trials=N_TRIALS, timeout=TIMEOUT)
    except KeyboardInterrupt:
        print("Interrumpido por el usuario. Guardando mejores resultados hasta ahora...")

    print("✅ Optimización completada.")
    print("🏆 Mejores Hiperparámetros:")
    best_params = study.best_trial.params
    print(json.dumps(best_params, indent=4))

    # Guardar en archivo
    filename = f"best_hyperparams_{ASSET.lower()}.json"
    with open(filename, "w") as f:
        json.dump(best_params, f, indent=4)
    print(f"💾 Guardado en {filename}")
