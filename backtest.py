import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from stable_baselines3 import PPO
from trading_env import TradingEnv

def run_backtest(asset_name="BTC", model_path=None, data_path=None, chart_name=None):
    # Default paths if not provided
    if model_path is None:
        model_path = f"models/PRODUCTION/{asset_name.upper()}/ppo_{asset_name.lower()}_final.zip"
            
    if data_path is None:
        data_path = f"datos_{asset_name.lower()}_15m_binance.csv"

    if chart_name is None:
        chart_name = f"backtest_{asset_name.lower()}_latest.png"

    print(f"📊 Running Backtest for {asset_name} using {model_path}...")
    
    # Load Data
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"❌ Data file not found: {data_path}")
        return

    # Create Env with Asset Specific Risk Config (Standard of Gold / Elite Hybrid)
    env_params = {}
    if asset_name.upper() == "SOL":
        env_params = {
            "cooldown_steps": 8,
            "stop_loss": 0.03,
            "trailing_stop_drop": 0.015,
            "risk_aversion": 1.2,
            "ema_penalty": 0.03,
            "vol_penalty": 0.05
        }
        print(f"🎯 {asset_name.upper()} Backtest: MODO ÉLITE ACTIVADO...")
    elif asset_name.upper() == "ETH":
        env_params = {
            "cooldown_steps": 6,
            "stop_loss": 0.025,
            "trailing_stop_drop": 0.015,
            "risk_aversion": 1.3,
            "ema_penalty": 0.03,
            "vol_penalty": 0.04
        }
        print(f"🎯 {asset_name.upper()} Backtest: MODO ÉLITE ACTIVADO...")

    env = TradingEnv(df, **env_params)
    
    # Load Model
    try:
        model = PPO.load(model_path)
    except Exception as e:
        print(f"❌ Could not load model: {e}")
        return
    
    obs, info = env.reset()
    done = False
    truncated = False
    
    net_worths = []
    real_trades = 0
    
    while not done and not truncated:
        action, _states = model.predict(obs, deterministic=True)
        if hasattr(action, 'item'): action = int(action.item())
        
        obs, reward, done, truncated, info = env.step(action)
        if info.get('trade_executed', False): real_trades += 1
        net_worths.append(info['net_worth'])
        
    # Analysis
    net_worths = np.array(net_worths)
    initial_balance = env.initial_balance
    final_balance = net_worths[-1]
    total_return = ((final_balance - initial_balance) / initial_balance) * 100
    
    # Sharpe Ratio (Approximate)
    returns = np.diff(net_worths) / net_worths[:-1]
    sharpe = np.mean(returns) / (np.std(returns) + 1e-9) * np.sqrt(252 * 96) # Adjusted for 15m candles (96 per day)
    
    running_max = np.maximum.accumulate(net_worths)
    drawdowns = (running_max - net_worths) / running_max
    max_drawdown = drawdowns.max() * 100
    
    # Save Results Data
    os.makedirs("reports", exist_ok=True)
    results_file = "reports/results_summary.json"
    
    current_results = {}
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            try:
                current_results = json.load(f)
            except:
                current_results = {}
                
    current_results[asset_name.upper()] = {
        "initial_balance": initial_balance,
        "final_balance": final_balance,
        "return_pct": total_return,
        "sharpe_ratio": float(sharpe),
        "max_drawdown_pct": max_drawdown,
        "total_trades": real_trades,
        "chart_path": f"reports/{chart_name}"
    }
    
    with open(results_file, 'w') as f:
        json.dump(current_results, f, indent=4)
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(net_worths, label='Equity Curve', color='#00ffcc', linewidth=2)
    plt.axhline(y=initial_balance, color='white', linestyle='--', alpha=0.5)
    plt.title(f'{asset_name} Backtest - Return: {total_return:.2f}% | Trades: {real_trades}', fontsize=14, color='white')
    plt.xlabel('Steps', color='white')
    plt.ylabel('Net Worth ($)', color='white')
    plt.grid(True, alpha=0.1)
    plt.legend()
    
    plt.gcf().set_facecolor('#1e1e1e')
    plt.gca().set_facecolor('#2d2d2d')
    plt.gca().tick_params(colors='white')
    
    chart_dest = f"reports/{chart_name}"
    plt.savefig(chart_dest, facecolor='#1e1e1e')
    print(f"🖼️ Chart saved as {chart_dest}")
    plt.close()

    print(f"✅ {asset_name} results recorded. Return: {total_return:.2f}%")

if __name__ == "__main__":
    import sys
    asset = sys.argv[1].upper() if len(sys.argv) > 1 else "BTC"
    model = sys.argv[2] if len(sys.argv) > 2 else None
    chart = sys.argv[3] if len(sys.argv) > 3 else None
    run_backtest(asset, model_path=model, chart_name=chart)
