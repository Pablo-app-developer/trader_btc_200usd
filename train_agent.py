import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from trading_env import TradingEnv

def train_agent():
    print("🚀 Starting Professional Agent Training...")
    
    # 1. Load Data
    try:
        df = pd.read_csv("datos_btc_15m_binance.csv") # PHASE 3 DATA (1 Year)
    except FileNotFoundError:
        print("❌ Data not found. Run download_data_binance.py first.")
        return

    # Split Data into Train and Validation (80/20)
    split_idx = int(len(df) * 0.8)
    df_train = df.iloc[:split_idx]
    df_val = df.iloc[split_idx:]
    
    print(f"📊 Data Split: Train={len(df_train)} rows, Val={len(df_val)} rows")

    # 2. Create the Environments
    env_train = DummyVecEnv([lambda: TradingEnv(df_train)])
    env_val = DummyVecEnv([lambda: TradingEnv(df_val)])
    
    # 3. Define Model (PPO - Actor Critic)
    model_name = "ppo_btc_phase5_scaled"
    log_dir = "./tensorboard_logs/"
    os.makedirs(log_dir, exist_ok=True)
    
    from stable_baselines3.common.callbacks import EvalCallback
    
    # Eval Callback
    eval_callback = EvalCallback(
        env_val, 
        best_model_save_path=f'./models/best_{model_name}',
        log_path=log_dir, 
        eval_freq=10000,
        deterministic=True, 
        render=False
    )
    
    checkpoint_callback = CheckpointCallback(
        save_freq=50000, 
        save_path='./models/', 
        name_prefix=model_name
    )

    # --- PHASE A: EXPLORATION (High Entropy) ---
    print("\n🦁 PHASE A: EXPLORATION (300k steps, Ent=0.05)")
    print("   Goal: Find valid trading strategies (wild attempts).")
    
    model = PPO(
        "MlpPolicy", 
        env_train, 
        verbose=1, 
        tensorboard_log=log_dir,
        learning_rate=0.0001,
        n_steps=2048,
        batch_size=64,
        gamma=0.99,
        ent_coef=0.05, # High Exploration
        device="cuda"
    )
    
    model.learn(total_timesteps=300000, callback=[eval_callback, checkpoint_callback])
    model.save(f"models/{model_name}_exploration")
    print("✅ Phase A Complete. Model saved.")

    # --- PHASE B: CONSOLIDATION (Low Entropy) ---
    print("\n🦅 PHASE B: CONSOLIDATION (700k steps, Ent=0.01)")
    print("   Goal: Refine strategy and minimize unforced errors.")
    
    # Modifying Entropy Coefficient on the fly
    model.ent_coef = 0.01 
    
    # Continue Training
    model.learn(total_timesteps=700000, callback=[eval_callback, checkpoint_callback], reset_num_timesteps=False)
    
    print("✅ Phase B Complete.")
    
    # 6. Save Final Model
    model.save(f"models/{model_name}_final")
    print(f"💾 Model saved to models/{model_name}_final.zip")

if __name__ == "__main__":
    train_agent()
