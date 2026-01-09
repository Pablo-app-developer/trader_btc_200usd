import time
import os
import pandas as pd
import numpy as np
import ccxt
import logging
from datetime import datetime
from stable_baselines3 import PPO
from config import get_asset_config

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("live_trader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

class LiveTrader:
    def __init__(self, asset_symbol, api_key=None, api_secret=None, sandbox=True):
        self.symbol = asset_symbol.upper()
        self.config = get_asset_config(self.symbol)
        
        # Conexión a Exchange
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'} # Futuros perpetuos
        })
        
        if sandbox:
            self.exchange.set_sandbox_mode(True)
            logger.warning("🧪 MODO SANDBOX (TESTNET) ACTIVADO. No se usará dinero real.")
            
        # Cargar Modelo
        model_path = f"models/PRODUCTION/{self.symbol}/ppo_{self.symbol.lower()}_final.zip"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No se encuentra el modelo entrenado: {model_path}")
            
        logger.info(f"🧠 Cargando cerebro IA para {self.symbol}...")
        self.model = PPO.load(model_path)
        
        # Estado Interno
        self.window_size = 60
        self.current_position = 0 # 0: Nada, 1: Long
        self.entry_price = 0.0

    def fetch_market_data(self, limit=100):
        """Descarga las últimas velas para alimentar al modelo."""
        timeframe = '15m'
        try:
            ohlcv = self.exchange.fetch_ohlcv(f"{self.symbol}/USDT", timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Feature Engineering (TIENE QUE SER IDÉNTICO AL ENTRENAMIENTO)
            # Copiar lógica exacta de trading_env.py
            # 1. Indicadores Técnicos
            df['RSI'] = self.calculate_rsi(df['Close'], 14)
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
            
            # Bollinger Bands
            rolling_mean = df['Close'].rolling(window=20).mean()
            rolling_std = df['Close'].rolling(window=20).std()
            df['BBU_20_2.0'] = rolling_mean + (rolling_std * 2.0)
            df['BBL_20_2.0'] = rolling_mean - (rolling_std * 2.0)

            # Features Normalizados para la IA
            df['Log_Ret'] = np.log(df['Close'] / df['Close'].shift(1)).fillna(0)
            df['RSI_Norm'] = df['RSI'] / 100.0
            df['BB_Pct'] = (df['Close'] - df['BBL_20_2.0']) / (df['BBU_20_2.0'] - df['BBL_20_2.0'])
            df['BB_Pct'] = df['BB_Pct'].fillna(0.5)
            df['EMA_20_Dist'] = (df['Close'] / df['EMA_20']) - 1
            df['EMA_50_Dist'] = (df['Close'] / df['EMA_50']) - 1
            df['EMA_200_Dist'] = (df['Close'] / df['EMA_200']) - 1
            
            # Seleccionar últimas 60 velas
            obs_cols = ['Log_Ret', 'RSI_Norm', 'BB_Pct', 'EMA_20_Dist', 'EMA_50_Dist', 'EMA_200_Dist']
            
            if len(df) < self.window_size:
                logger.error("❌ Datos insuficientes para generar predicción.")
                return None
                
            recent_data = df[obs_cols].iloc[-self.window_size:].values.astype(np.float32)
            current_close = df['Close'].iloc[-1]
            
            return recent_data, current_close
            
        except Exception as e:
            logger.error(f"Error descargando datos: {e}")
            return None, None

    def construct_observation(self, market_data):
        """Construye el tensor de observación final combinando Mercado + Estado de Cuenta."""
        # Necesitamos simular el estado de cuenta para la IA
        # En live real, esto vendría de self.exchange.fetch_balance()
        # Por seguridad inicial, lo normalizamos
        
        balance_ratio = 0.0 # Asumimos balance neutral estable
        position_ratio = 1.0 if self.current_position > 0 else 0.0
        
        account_obs = np.full((self.window_size, 2), [balance_ratio, position_ratio], dtype=np.float32)
        
        # Combinar
        obs = np.hstack((market_data, account_obs))
        return obs

    def execute_trade(self, action, price):
        """Ejecuta la orden en el exchange."""
        # 0: Hold, 1: Buy, 2: Sell
        
        if action == 1 and self.current_position == 0:
            logger.info(f"🟢 SEÑAL DE COMPRA detectada a ${price:.2f}")
            # AQUÍ IRÍA LA ORDEN REAL DE BINANCE
            # order = self.exchange.create_market_buy_order(f"{self.symbol}/USDT", size)
            self.current_position = 1
            self.entry_price = price
            
        elif action == 2 and self.current_position > 0:
            logger.info(f"🔴 SEÑAL DE VENTA detectada a ${price:.2f}")
            pnl = (price - self.entry_price) / self.entry_price * 100
            logger.info(f"💰 Resultado Trade: {pnl:.2f}%")
            # AQUÍ IRÍA LA ORDEN REAL DE BINANCE
            self.current_position = 0
            
        else:
            logger.info(f"💤 Hold. Acción: {action} | Posición actual: {self.current_position}")

    def run(self):
        logger.info(f"🚀 Iniciando Trader en Vivo para {self.symbol}...")
        
        while True:
            logger.info("⏳ Esperando cierre de vela (15m)...")
            # En producción real, sincronizaríamos con el reloj del sistema
            # Por ahora, ciclo simple de 1min para pruebas
            
            market_data, current_price = self.fetch_market_data()
            if market_data is not None:
                obs = self.construct_observation(market_data)
                
                # Predecir
                action, _ = self.model.predict(obs, deterministic=True)
                
                # Ejecutar
                self.execute_trade(action.item(), current_price)
            
            time.sleep(60 * 15) # Esperar 15 minutos (simulado)

    # Utilidades
    def calculate_rsi(self, series, period):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

if __name__ == "__main__":
    import sys
    asset = sys.argv[1] if len(sys.argv) > 1 else "ETH"
    trader = LiveTrader(asset)
    trader.run()
