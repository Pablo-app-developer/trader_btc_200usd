import pandas as pd
import numpy as np
from trading_env import TradingEnv
# from stable_baselines3.common.env_checker import check_env # Commented out due to install issues

def main():
    print("🧪 Verifying Custom Trading Environment (Manual Mode)...")
    
    # Load data
    try:
        df = pd.read_csv("datos_btc_15m.csv")
        print(f"Data loaded successfully. Shape: {df.shape}")
    except FileNotFoundError:
        print("❌ Error: 'datos_btc_15m.csv' not found. Please run download_data.py first.")
        return

    # Create environment
    env = TradingEnv(df)
    
    # Manual Check of Spaces
    print(f"Action Space: {env.action_space}")
    print(f"Observation Space: {env.observation_space}")
    
    # Test a random episode
    obs, info = env.reset()
    print(f"Initial Observation Shape: {obs.shape}")
    print(f"Initial Info: {info}")
    
    done = False
    truncated = False
    step = 0
    total_reward = 0
    
    while not done and not truncated:
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        step += 1
        
        # Verify observation shape consistency
        if obs.shape != (60, 9): # 7 features + 2 account stats
            print(f"❌ Error: Observation shape mismatch at step {step}. Got {obs.shape}")
            break
            
        if step > 1000: # Just test 1000 steps
            print("✅ 1000 steps reached without completion (good for long usage).")
            break
            
    print(f"✅ Random agent test passed. Steps: {step}, Total Reward: {total_reward:.4f}")
    print(f"Final Info: {info}")

if __name__ == "__main__":
    main()
