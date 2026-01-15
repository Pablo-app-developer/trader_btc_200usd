import optuna
import pandas as pd
import numpy as np
import os
import json
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from trading_env import TradingEnv

# --- SETTINGS FOR THE 200 USD CHALLENGE ---
INITIAL_BALANCE = 200
POSITION_SIZE_PCT = 0.60 # Tactical Mode (Balanced Aggression)
COMMISSION = 0.0005     
N_TRIALS = 5            
TOTAL_TIMESTEPS = 150000 

# Load Solana Data
if os.path.exists("datos_sol_15m_binance.csv"):
    df = pd.read_csv("datos_sol_15m_binance.csv")
else:
    print("Error: SOL Data not found!")
    exit()

split_idx = int(len(df) * 0.8)
df_train = df.iloc[:split_idx]
df_val = df.iloc[split_idx:]

def objective(trial):
    # 1. Hyperparameters customized for "Disciplined Sniper Phase"
    lr = trial.suggest_float("learning_rate", 5e-5, 3e-4, log=True) 
    ent_coef = trial.suggest_float("ent_coef", 0.005, 0.03) # Low chaos, high precision
    gamma = trial.suggest_float("gamma", 0.90, 0.98)
    n_steps = trial.suggest_categorical("n_steps", [2048])
    batch_size = trial.suggest_categorical("batch_size", [64, 128])
    
    # Environment Hyperparameters
    stop_loss = trial.suggest_float("stop_loss", 0.02, 0.045) 
    trailing_stop_drop = trial.suggest_float("ts_drop", 0.015, 0.03)
    cooldown = trial.suggest_int("cooldown", 4, 12) # Breathe between shots
    risk_aversion = trial.suggest_float("risk_aversion", 0.1, 0.5) # Healthy respect for loss
    
    # Create Env with Challenge Params - DISCIPLINED MODE
    env_train = DummyVecEnv([lambda: TradingEnv(
        df_train, 
        initial_balance=INITIAL_BALANCE,
        commission=COMMISSION,
        position_size_pct=POSITION_SIZE_PCT,
        stop_loss=stop_loss,
        trailing_stop_drop=trailing_stop_drop,
        cooldown_steps=cooldown, 
        risk_aversion=risk_aversion,
        ema_penalty=0.01, # Gentle nudge to follow trend
        vol_penalty=0.01 
    )])
    
    env_val = DummyVecEnv([lambda: TradingEnv(
        df_val, 
        initial_balance=INITIAL_BALANCE,
        commission=COMMISSION,
        position_size_pct=POSITION_SIZE_PCT,
        stop_loss=stop_loss,
        trailing_stop_drop=trailing_stop_drop,
        cooldown_steps=cooldown,
        risk_aversion=risk_aversion,
        ema_penalty=0.01,
        vol_penalty=0.01
    )])

    # 2. Model Setup
    model = PPO("MlpPolicy", env_train, 
                learning_rate=lr, 
                ent_coef=ent_coef, 
                gamma=gamma, 
                n_steps=n_steps, 
                batch_size=batch_size,
                verbose=0, 
                device="cuda")

    # 3. Train
    try:
        model.learn(total_timesteps=TOTAL_TIMESTEPS)
        
        # 4. Challenge Evaluation
        obs = env_val.reset()
        net_worths = []
        total_trades = 0
        
        for _ in range(len(df_val) - 61):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env_val.step(action)
            net_worths.append(info[0]['net_worth'])
            total_trades = info[0]['total_trades'] # Track trades
            if done: break
            
        final_nw = net_worths[-1]
        max_nw = max(net_worths)
        min_nw = min(net_worths)
        
        # Challenge Metrics
        roi_pct = (final_nw - INITIAL_BALANCE) / INITIAL_BALANCE
        drawdown = (max_nw - min_nw) / max_nw if max_nw > 0 else 1.0
        
        # --- FILTERS ---
        # 1. Must Trade! (Lowered threshold)
        if total_trades < 2:
            return -20 # Soft penalty
            
        # 2. Must Survive!
        if final_nw < INITIAL_BALANCE:
            return -100 + roi_pct 
            
        # 3. Must not Blow Up!
        if drawdown > 0.25: # Looser limit for 95% position size High Volatility
             return roi_pct * 0.2 # Heavily penalized
            
        # SCORE:
        score = roi_pct * (1 - drawdown)
        
        print(f"Trial Result: NW=${final_nw:.2f} | ROI={roi_pct*100:.1f}% | DD={drawdown*100:.1f}% | Trades={total_trades} | Score={score:.4f}")
        return score

    except Exception as e:
        print(f"Trial failed: {e}")
        return -100

if __name__ == "__main__":
    print(f"🚀 INICIANDO RETO 200 USD: SOLANA SPEED RUN")
    print(f"Settings: Equity=${INITIAL_BALANCE} | Position={POSITION_SIZE_PCT*100}% | Comm={COMMISSION*100}%")
    
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=N_TRIALS)

    print("\n🏆 RETO - CONFIGURACIÓN GANADORA ENCONTRADA")
    print(f"Mejor Score: {study.best_value}")
    print("Parámetros:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value}")

    # Save specifically for the challenge
    with open("best_hyperparams_sol_challenge.json", "w") as f:
        json.dump(study.best_params, f, indent=4)
