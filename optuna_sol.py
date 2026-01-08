import optuna
import pandas as pd
import numpy as np
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from trading_env import TradingEnv

# Load Solana Data
df = pd.read_csv("datos_sol_15m_binance.csv")
split_idx = int(len(df) * 0.8)
df_train = df.iloc[:split_idx]
df_val = df.iloc[split_idx:]

def objective(trial):
    # 1. Suggest Hyperparameters for SOL Volatility
    # Solana needs more "reflexes", so we allow slightly higher LR
    lr = trial.suggest_float("learning_rate", 1.5e-5, 3e-4, log=True)
    ent_coef = trial.suggest_float("ent_coef", 0.001, 0.015)
    gamma = trial.suggest_float("gamma", 0.90, 0.99) # Lower gamma for faster adaptation
    n_steps = trial.suggest_categorical("n_steps", [512, 1024, 2048])
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])
    
    # Env with realistic commission
    env_train = DummyVecEnv([lambda: TradingEnv(df_train, commission=0.0005)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val, commission=0.0005)])

    # 2. Base Model (The 9.37% winner + New Ph7 Logic)
    base_model = "models/ARCHIVE/SOL/ppo_sol_pro_final.zip"
    
    if os.path.exists(base_model):
        model = PPO.load(base_model, env=env_train, 
                         learning_rate=lr, 
                         ent_coef=ent_coef, 
                         gamma=gamma, 
                         n_steps=n_steps, 
                         batch_size=batch_size)
    else:
        model = PPO("MlpPolicy", env_train, verbose=0, device="cuda")

    # 3. Fast Trial Training (50,000 steps to capture SOL patterns)
    try:
        model.learn(total_timesteps=50000)
        
        # 4. Evaluation
        obs = env_val.reset()
        net_worths = []
        
        for _ in range(len(df_val) - 61):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env_val.step(action)
            net_worths.append(info[0]['net_worth'])
            if done: break
            
        final_nw = net_worths[-1]
        max_nw = max(net_worths)
        min_nw = min(net_worths)
        drawdown = (max_nw - min_nw) / max_nw if max_nw > 0 else 1.0
        
        # ALPHA SCORE: Reward high returns but heavily penalize excessive risk
        total_return_pct = (final_nw - 10000) / 100
        
        # If the bot loses money, give it a very low score
        if total_return_pct <= 0:
            return total_return_pct - (drawdown * 10)
            
        # Target: Return / Risk balance. We prioritize Return > 5%
        score = total_return_pct / (drawdown + 0.01)
        return score

    except Exception as e:
        print(f"Trial failed: {e}")
        return -10000

if __name__ == "__main__":
    print("🚀 Iniciando SOLANA ALPHA OPTIMIZER (Versión Turbo)...")
    study = optuna.create_study(direction="maximize")
    
    # 8 trials for professional speed/quality balance
    study.optimize(objective, n_trials=8)

    print("\n🏆 SOLANA OPTUNA COMPLETADO")
    print(f"Mejor Alpha Score: {study.best_value}")
    print("Parámetros Ganadores para SOL:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value}")

    # Save to specific SOL file
    import json
    with open("best_hyperparams_sol.json", "w") as f:
        json.dump(study.best_params, f, indent=4)
