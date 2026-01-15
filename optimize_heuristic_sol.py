import optuna
import pandas as pd
import numpy as np
import json
import os

# --- CONFIG ---
DATA_FILE = "datos_sol_15m_binance.csv"
INITIAL_CAPITAL = 200.0
POSITION_SIZE_PCT = 0.60  # 60% tactic
COMMISSION = 0.0005      # 0.05%

def backtest(df, params):
    # Unpack params
    breakout_period = params['breakout_period']
    ema_period = params['ema_period']
    
    stop_loss_pct = params['stop_loss']       
    trailing_trigger = params['ts_trigger']   
    trailing_dist = params['ts_dist']         
    
    # --- PREPARE DATA ---
    # We use numpy for raw speed
    highs = df['High'].values
    closes = df['Close'].values
    
    # Compute Rolling Max using Pandas for convenience first
    # shift(1) allows us to see the max of Previous N candles
    roll_max = df['High'].rolling(window=breakout_period).max().shift(1).fillna(0).values
    
    # EMA for filter
    ema = df['Close'].ewm(span=ema_period, adjust=False).mean().values
    
    # --- LOOP ---
    balance = INITIAL_CAPITAL
    shares = 0
    max_price_since_entry = 0
    entry_price = 0
    
    trades = 0
    wins = 0
    equity_curve = []
    
    # Start after enough data
    start_idx = max(breakout_period, ema_period) + 10
    
    for i in range(start_idx, len(closes)):
        current_price = closes[i]
        equity = balance + (shares * current_price)
        equity_curve.append(equity)
        
        # 1. EXIT LOGIC
        if shares > 0:
            if current_price > max_price_since_entry:
                max_price_since_entry = current_price
            
            pnl_pct = (current_price - entry_price) / entry_price
            
            sell_signal = False
            reason = ""
            
            # SL
            if pnl_pct < -stop_loss_pct:
                sell_signal = True
            
            # TS
            if (max_price_since_entry - entry_price) / entry_price >= trailing_trigger:
                drop_from_high = (max_price_since_entry - current_price) / max_price_since_entry
                if drop_from_high >= trailing_dist:
                    sell_signal = True
            
            if sell_signal:
                revenue = shares * current_price * (1 - COMMISSION)
                balance += revenue
                if revenue > (shares * entry_price): wins += 1
                shares = 0
                max_price_since_entry = 0
                entry_price = 0
                trades += 1
                continue 
        
        # 2. ENTRY LOGIC
        if shares == 0:
            # Condition 1: Price broke above the N-period High
            breakout = current_price > roll_max[i]
            
            # Condition 2: Trend aligned
            trend_ok = current_price > ema[i]
            
            if breakout and trend_ok:
                invest_amount = balance * POSITION_SIZE_PCT
                if invest_amount < 10: invest_amount = balance
                
                cost = invest_amount * (1 + COMMISSION)
                if balance >= cost:
                    actual_invest = invest_amount
                    shares = (actual_invest / current_price) * (1 - COMMISSION)
                    balance -= actual_invest
                    
                    entry_price = current_price
                    max_price_since_entry = current_price

    final_equity = balance + (shares * closes[-1])
    
    # Drawdown Calc
    equity_arr = np.array(equity_curve)
    peak = np.maximum.accumulate(equity_arr)
    drawdown = (peak - equity_arr) / peak
    max_dd = drawdown.max() if len(drawdown) > 0 else 0
    
    return final_equity, max_dd, trades

def objective(trial):
    # HYPER-ACTIVE SCALPING PARAMETERS
    breakout_period = trial.suggest_int("breakout_period", 4, 48) # 1h to 12h breakouts
    ema_period = trial.suggest_int("ema_period", 20, 100) # Fast trend filter
    
    stop_loss = trial.suggest_float("stop_loss", 0.01, 0.04) # Tighter risk
    
    # Fast Profits (Scalping)
    ts_trigger = trial.suggest_float("ts_trigger", 0.005, 0.03) # Secure profit quickly (0.5% - 3%)
    ts_dist = trial.suggest_float("ts_dist", 0.005, 0.02) # Tight follow
    
    params = {
        "breakout_period": breakout_period,
        "ema_period": ema_period,
        "stop_loss": stop_loss,
        "ts_trigger": ts_trigger,
        "ts_dist": ts_dist
    }
    
    try:
        final_equity, max_dd, trades = backtest(df, params)
        
        roi = (final_equity - INITIAL_CAPITAL) / INITIAL_CAPITAL
        
        # --- SCORING FOR SPEED ---
        
        # 1. Survival Penalty
        if final_equity < INITIAL_CAPITAL: 
            return -100 + roi 
            
        # 2. Activity Filter (Need ACTION!)
        if trades < 300: # Approx 1 trade per day
            return -50
            
        # 3. Drawdown Limit (Still need to survive)
        if max_dd > 0.35: # Looser limit for aggressive growth
            return roi * 0.5 
            
        # Score heavily weighted on ROI
        score = roi * 10 - (max_dd * 2)
        return score
        
    except Exception as e:
        print(e)
        return -100

if __name__ == "__main__":
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} not found")
        exit()
        
    df = pd.read_csv(DATA_FILE)
    print(f"Data loaded: {len(df)} candles")

    study = optuna.create_study(direction="maximize")
    print("🚀 Running HYPER-ACTIVE Scalping Optimization (DEEP SEARCH - 1000 TRIALS)...")
    study.optimize(objective, n_trials=1000) 
    
    print("\n🏆 BEST BREAKOUT PARAMS (1000 TRIALS):")
    best = study.best_params
    print(best)
    
    final_eq, max_dd, trades = backtest(df, best)
    roi = (final_eq - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    print(f"\nSimulation Result:")
    print(f"Initial: ${INITIAL_CAPITAL}")
    print(f"Final:   ${final_eq:.2f}")
    print(f"ROI:     {roi:.2f}%")
    print(f"Drawdown: {max_dd*100:.2f}%")
    print(f"Trades:  {trades}")
    
    with open("best_breakout_sol_1000.json", "w") as f:
        json.dump(best, f, indent=4)
