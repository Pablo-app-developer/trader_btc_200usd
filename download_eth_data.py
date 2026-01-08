import ccxt
import pandas as pd
import ta
import time
from datetime import datetime, timedelta

def download_eth_data(symbol='ETH/USDT', timeframe='15m', days=365):
    print(f"📥 Connecting to Binance to fetch {days} days of {symbol} ({timeframe})...")
    exchange = ccxt.binance()
    
    # Calculate start timestamp
    since = exchange.parse8601((datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S'))
    
    all_ohlcv = []
    limit = 1000 # Binance limit
    
    while since < exchange.milliseconds():
        print(f"   Fetching {symbol} since {exchange.iso8601(since)}...")
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            if len(ohlcv) == 0:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1 # Move to next timestamp
            time.sleep(0.5) 
        except Exception as e:
            print(f"Error fetching: {e}")
            break
            
    df = pd.DataFrame(all_ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Datetime'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Datetime', inplace=True)
    
    print(f"✅ Downloaded {len(df)} candles for {symbol}.")
    
    # --- FEATURE ENGINEERING ---
    print("🛠️ Calculating Indicators for Ethereum...")
    
    # 1. RSI
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    
    # 2. Bollinger Bands
    indicator_bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BBL_20_2.0'] = indicator_bb.bollinger_lband()
    df['BBM_20_2.0'] = indicator_bb.bollinger_mavg()
    df['BBU_20_2.0'] = indicator_bb.bollinger_hband()
    
    # 3. EMA
    df['EMA_20'] = ta.trend.EMAIndicator(close=df['Close'], window=20).ema_indicator()
    df['EMA_50'] = ta.trend.EMAIndicator(close=df['Close'], window=50).ema_indicator()
    df['EMA_200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()

    # Cleanup
    df.dropna(inplace=True)
    
    filename = "datos_eth_15m_binance.csv"
    df.to_csv(filename)
    print(f"💾 Saved to {filename}. Rows: {len(df)}")
    return df

if __name__ == "__main__":
    download_eth_data()
