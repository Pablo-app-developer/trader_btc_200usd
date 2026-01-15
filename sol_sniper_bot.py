import ccxt
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime

# --- CONFIGURATION (OPTION A: SAFE SNIPER) ---
SYMBOL = 'SOL/USDT'
TIMEFRAME = '15m'
CAPITAL_ALLOCATION = 0.60 # 60% of Balance
LEVERAGE = 1              # Spot (No leverage by default)

# Load Best Params (Option A)
PARAMS = {
    "breakout_period": 35,
    "ema_period": 23,
    "stop_loss": 0.0172,
    "ts_trigger": 0.0096,
    "ts_dist": 0.0080
}

# --- BINANCE CONNECTION ---
def get_exchange(use_us=False):
    return ccxt.binanceus({'enableRateLimit': True}) if use_us else ccxt.binance({'enableRateLimit': True})

exchange = get_exchange(use_us=False) # Start with Global

def fetch_data(symbol, timeframe, limit=500, retries=3):
    global exchange
    for i in range(retries):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"⚠️ Connection Error (Attempt {i+1}/{retries}): {e}")
            time.sleep(2)
            
            # Auto-Switch to Binance US if blocked/451/403 errors occur
            if "451" in str(e) or "403" in str(e) or "Service Unavailable" in str(e):
                if not isinstance(exchange, ccxt.binanceus):
                    print("🇺🇸 Switching to Binance US API (Region Detected)...")
                    exchange = get_exchange(use_us=True)
                    time.sleep(1)
    
    print("❌ Failed to fetch data after retries. Checking internet or API status.")
    return None

def calculate_signals(df, params):
    # 1. Breakout Level (Max of last N candles, shifted by 1 to avoid lookahead)
    df['Roll_Max'] = df['high'].rolling(window=params['breakout_period']).max().shift(1)
    
    # 2. Trend Filter
    df['EMA'] = df['close'].ewm(span=params['ema_period'], adjust=False).mean()
    
    # Get latest completed candle (row -2, since -1 is current forming candle)
    # But for real-time breakout, we monitor the CURRENT price vs Previous Level
    current_price = df['close'].iloc[-1]
    prev_breakout_level = df['Roll_Max'].iloc[-1]
    ema_value = df['EMA'].iloc[-1]
    
    return current_price, prev_breakout_level, ema_value

def run_bot():
    print(f"🚀 SOL SNIPER BOT STARTED [Option A Config]")
    print(f"Strategy: Volatility Breakout")
    print(f"Params: {json.dumps(PARAMS, indent=2)}")
    
    # Mock State
    position = None # None or {'entry': float, 'shares': float, 'stop_loss': float, 'highest': float}
    balance = 200.0 # Simulation Balance
    
    while True:
        df = fetch_data(SYMBOL, TIMEFRAME)
        if df is not None:
            current_price, breakout_level, ema = calculate_signals(df, PARAMS)
            
            timestamp = df['timestamp'].iloc[-1]
            print(f"\n[{timestamp}] Price: {current_price:.4f} | Breakout Lvl: {breakout_level:.4f} | EMA: {ema:.4f}")
            
            # --- TRADING LOGIC ---
            
            if position is None:
                # ENTRY CONDITIONS
                # 1. Price > Breakout Level
                # 2. Price > EMA (Trend)
                
                if current_price > breakout_level and current_price > ema:
                    print("✅ BUY SIGNAL DETECTED!")
                    invest = balance * CAPITAL_ALLOCATION
                    shares = invest / current_price
                    entry_price = current_price
                    
                    # Initial Stop Loss
                    sl_price = entry_price * (1 - PARAMS['stop_loss'])
                    
                    position = {
                        'entry': entry_price,
                        'shares': shares,
                        'stop_loss': sl_price,
                        'highest': current_price
                    }
                    balance -= invest
                    print(f"🛒 BOUGHT {shares:.4f} SOL @ {current_price} | Invested: ${invest:.2f}")
                    print(f"🛡️ HARD STOP LOSS set at: {sl_price:.4f}")
            
            else:
                # EXIT CONDITIONS
                # Update Highest High for Trailing Stop
                if current_price > position['highest']:
                    position['highest'] = current_price
                
                # Check Hard Stop Loss
                if current_price < position['stop_loss']:
                    reason = "STOP LOSS"
                    sell = True
                else:
                    sell = False
                
                # Check Trailing Stop
                # Trigger Condition: Are we in profit enough?
                profit_pct = (position['highest'] - position['entry']) / position['entry']
                
                if profit_pct >= PARAMS['ts_trigger']:
                    # Calculate Dynamic Stop Price
                    trailing_stop_price = position['highest'] * (1 - PARAMS['ts_dist'])
                    
                    print(f"🎯 TRAILING STOP ACTIVE: {trailing_stop_price:.4f} (Profit Peak: {profit_pct*100:.2f}%)")
                    
                    if current_price < trailing_stop_price:
                        reason = f"TRAILING STOP (Locked Profit)"
                        sell = True
                
                if sell:
                    revenue = position['shares'] * current_price
                    # Commission
                    revenue = revenue * (1 - 0.0005) 
                    
                    balance += revenue
                    net_profit = revenue - (position['shares'] * position['entry'])
                    
                    print(f"🚨 SELL EXECUTED: {reason}")
                    print(f"💰 PnL: ${net_profit:.2f}")
                    print(f"💵 NEW BALANCE: ${balance:.2f}")
                    position = None

        time.sleep(15 * 60) # Wait 15 minutes for next candle (Simplified)

if __name__ == "__main__":
    run_bot()
