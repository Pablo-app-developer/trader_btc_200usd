from trading_env import TradingEnv
import pandas as pd
import numpy as np

def debug_env():
    print("🐞 Debugging Environment (Phase 3)...")
    try:
        df = pd.read_csv("datos_btc_15m_binance.csv")
    except:
        df = pd.read_csv("datos_btc_15m.csv")
        
    env = TradingEnv(df) 
    
    obs, _ = env.reset()
    print(f"Initial Observation Shape: {obs.shape}")
    print(f"Initial Balance: {env.balance}")
    
    print("\n--- Testing Phase 4 Logic (20% Size, Risk Aversion) ---")
    obs, reward, done, _, info = env.step(1) # Buy
    print(f"Action: Buy")
    print(f"Balance: {env.balance} (Should be ~80% of init)")
    print(f"Shares: {env.shares_held}")
    print(f"Reward: {reward}")
    
    print("\n--- Testing Sell Action ---")
    obs, reward, done, _, info = env.step(2) # Sell
    print(f"Action: Sell")
    print(f"Reward: {reward}")
    
    # Test Inactivity
    print("\n--- Testing Inactivity Penalty ---")
    env.shares_held = 0
    env.steps_since_trade = 100 # Force penalty threshold
    obs, reward, done, _, info = env.step(0) # Hold
    print(f"Action: Hold (Steps=101)")
    print(f"Reward: {reward} (Should be negative due to inactivity)")

if __name__ == "__main__":
    debug_env()
