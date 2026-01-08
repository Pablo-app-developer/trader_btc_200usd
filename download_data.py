import yfinance as yf
import pandas as pd
import ta

def descargar_datos_profesionales(symbol="BTC-USD", interval="15m", period="59d"):
    print(f"📥 Descargando datos de {symbol}...")
    # Descargamos datos de Yahoo Finance
    # auto_adjust=True to get OHLC relative to closes
    df = yf.download(tickers=symbol, interval=interval, period=period, auto_adjust=True, multi_level_index=False)
    
    # If the dataframe is empty, stop
    if df.empty:
        print("❌ Error: No se descargaron datos. Verifica tu conexión o el símbolo.")
        return

    # --- FEATURE ENGINEERING ---
    # 1. RSI
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    
    # 2. Bandas de Bollinger
    indicator_bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BBL_20_2.0'] = indicator_bb.bollinger_lband()
    df['BBM_20_2.0'] = indicator_bb.bollinger_mavg()
    df['BBU_20_2.0'] = indicator_bb.bollinger_hband()
    
    # 3. EMA (Medias Móviles)
    df['EMA_20'] = ta.trend.EMAIndicator(close=df['Close'], window=20).ema_indicator()
    df['EMA_50'] = ta.trend.EMAIndicator(close=df['Close'], window=50).ema_indicator()
    
    # Limpiamos datos nulos
    df.dropna(inplace=True)
    
    filename = "datos_btc_15m.csv"
    df.to_csv(filename)
    print(f"✅ Datos guardados en '{filename}'. Listos para el entrenamiento.")
    print(df.tail())
    return df

if __name__ == "__main__":
    descargar_datos_profesionales()
