import ccxt
import pandas as pd
import ta
import time
from datetime import datetime, timedelta

def download_asset_data(symbol, days=365):
    filename = f"datos_{symbol.replace('/', '_').split('_')[0].lower()}_15m_binance.csv"
    print(f"\n📥 Fetching {days} days of {symbol} (15m) from Binance...")
    
    exchange = ccxt.binance()
    since = exchange.parse8601((datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S'))
    
    all_ohlcv = []
    limit = 1000
    
    while since < exchange.milliseconds():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, '15m', since, limit)
            if not ohlcv: break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1
            time.sleep(0.2)
        except Exception as e:
            print(f"Error: {e}")
            break
            
    df = pd.DataFrame(all_ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Datetime'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Datetime', inplace=True)
    
    # Feature Engineering
    print(f"🛠️ Calculating indicators for {symbol}...")
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close']).rsi()
    bb = ta.volatility.BollingerBands(close=df['Close'])
    df['BBL_20_2.0'] = bb.bollinger_lband()
    df['BBM_20_2.0'] = bb.bollinger_mavg()
    df['BBU_20_2.0'] = bb.bollinger_hband()
    df['EMA_20'] = ta.trend.EMAIndicator(close=df['Close'], window=20).ema_indicator()
    df['EMA_50'] = ta.trend.EMAIndicator(close=df['Close'], window=50).ema_indicator()
    df['EMA_200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()
    
    df.dropna(inplace=True)
    df.to_csv(filename)
    print(f"✅ Saved to {filename}. Rows: {len(df)}")

if __name__ == "__main__":
    assets = ['ETH/USDT', 'SOL/USDT', 'LINK/USDT']
    for asset in assets:
        download_asset_data(asset)
