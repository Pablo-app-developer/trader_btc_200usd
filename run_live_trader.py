import time
import os
import json
import pandas as pd
import numpy as np
import yfinance as yf
import logging
from datetime import datetime
from stable_baselines3 import PPO
from config import get_asset_config
from torch.utils.tensorboard import SummaryWriter
from telegram_notifier import TelegramNotifier
from trading_database import TradingDatabase
from config_loader import load_bot_config

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
    def __init__(self, asset_symbol):
        self.symbol = asset_symbol.upper()
        # Mapping symbol to Yahoo Ticker
        self.yahoo_ticker = f"{self.symbol}-USD"
        
        # Load YAML Configuration
        self.bot_config = load_bot_config()
        logger.info(f"⚙️ Configuration loaded from YAML")
        
        # Old config (for compatibility)
        self.config = get_asset_config(self.symbol)
        
        # Database for persistent storage
        self.db = TradingDatabase("trading_bot.db")
        logger.info(f"💾 Database connected")
        
        # TensorBoard Logger (Gráficas estilo FTMO)
        log_dir = f"tensorboard_logs/LIVE_{self.symbol}_200USD"
        self.writer = SummaryWriter(log_dir)
        logger.info(f"📊 TensorBoard activo en: {log_dir}")

        logger.info(f"🌍 Conectando a Yahoo Finance ({self.yahoo_ticker}) para evitar bloqueo Geo-IP...")
            
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
        self.trade_start_time = None
        
        # Load configuration from YAML
        initial_capital = self.bot_config.get('trading', 'capital_initial', default=200)
        
        # Prop Firm Tracking (From YAML Config)
        self.sim_balance = float(initial_capital)
        self.daily_start_balance = float(initial_capital)
        self.last_day_checked = datetime.now().day
        self.max_daily_loss = 0.0
        self.wins = 0
        self.losses = 0
        
        # Risk Config (From YAML - Asset-specific or global)
        self.stop_loss_pct = self.bot_config.get_stop_loss(self.symbol)
        self.take_profit_pct = self.bot_config.get_take_profit(self.symbol)
        cooldown_minutes = self.bot_config.get('risk_management', 'cooldown_minutes', default=120)
        self.cooldown_seconds = cooldown_minutes * 60
        self.last_sell_time = 0
        
        logger.info(f"🎯 Risk Config: SL={self.stop_loss_pct*100:.1f}%, TP={self.take_profit_pct*100:.1f}%")
        
        # Try to recover previous state from database
        self._recover_state()
        
        # Telegram Notifications
        self.notifier = self._init_telegram()
        
    def _init_telegram(self):
        """Initialize Telegram notifier from config file"""
        try:
            config_path = "telegram_config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    telegram_config = config.get('telegram', {})
                    if telegram_config.get('enabled', False):
                        return TelegramNotifier(
                            bot_token=telegram_config['bot_token'],
                            chat_id=telegram_config['chat_id'],
                            enabled=True
                        )
            logger.info("Telegram notifications disabled or config not found")
            return TelegramNotifier("", "", enabled=False)
        except Exception as e:
            logger.error(f"Failed to initialize Telegram: {e}")
            return TelegramNotifier("", "", enabled=False)
    
    def _recover_state(self):
        """Recover bot state from database after restart"""
        try:
            state = self.db.get_bot_state(self.symbol)
            if state:
                self.sim_balance = state['balance']
                self.current_position = state['position']
                self.entry_price = state['entry_price'] or 0.0
                self.wins = state['wins']
                self.losses = state['losses']
                logger.info(f"🔄 State recovered: Balance=${self.sim_balance:.2f}, Position={self.current_position}, W/L={self.wins}/{self.losses}")
            else:
                logger.info(f"📝 No previous state found. Starting fresh.")
        except Exception as e:
            logger.error(f"Failed to recover state: {e}")
    
    def _save_state(self):
        """Save current bot state to database"""
        try:
            self.db.update_bot_state(
                symbol=self.symbol,
                balance=self.sim_balance,
                position=self.current_position,
                entry_price=self.entry_price,
                wins=self.wins,
                losses=self.losses
            )
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def check_prop_firm_rules(self, current_equity):
        # Reset Daily Drawdown Logic
        today = datetime.now().day
        if today != self.last_day_checked:
            self.daily_start_balance = self.sim_balance
            self.last_day_checked = today
            self.max_daily_loss = 0.0
            logger.info(f"📅 NUEVO DÍA REGISTRADO. Reset de Drawdown Diario. Balance Inicio: ${self.daily_start_balance:.2f}")

        # Calculate Metrics
        daily_drawdown = (self.daily_start_balance - current_equity) / self.daily_start_balance * 100

        if daily_drawdown > self.max_daily_loss:
            self.max_daily_loss = daily_drawdown

        # Warnings (FTMO/MFF limits usually 5% daily, 10% total)
        if daily_drawdown > 4.0:
            logger.warning(f"⚠️ PELIGRO PROP FIRM: Drawdown Diario al {daily_drawdown:.2f}% (Límite 5%)")
        
        return daily_drawdown

    def fetch_market_data(self):
        """Descarga las últimas velas para alimentar al modelo usando Yahoo Finance."""
        try:
            # Download recent data (enough for window_size + indicators)
            # interval='15m' is supported by yfinance for last 60 days
            df = yf.download(self.yahoo_ticker, interval="15m", period="5d", progress=False)
            
            if len(df) == 0:
                logger.error("❌ Yahoo Finance devolvió DataFrame vacío.")
                return None, None

            # YFinance columns might come as MultiIndex (Price, Ticker). Flatten them.
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Reset index to get columns clean
            df = df.reset_index()
            
            # YFinance columns: Date, Open, High, Low, Close, Adj Close, Volume
            # Ensure proper naming
            df = df.rename(columns={"Date": "timestamp", "Datetime": "timestamp"})
            
            # Feature Engineering (TIENE QUE SER IDÉNTICO AL ENTRENAMIENTO)
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
                logger.error(f"❌ Datos insuficientes ({len(df)} velas). Esperando más historia...")
                return None, None
                
            recent_data = df[obs_cols].iloc[-self.window_size:].values.astype(np.float32)
            current_close = df['Close'].iloc[-1]
            
            # Clean scalar if it's a Series (yfinance quirk)
            if hasattr(current_close, 'item'): 
                current_close = current_close.item()
            
            return recent_data, current_close
            
        except Exception as e:
            logger.error(f"Error descargando datos: {e}")
            return None, None

    def construct_observation(self, market_data):
        """Construye el tensor de observación final combinando Mercado + Estado de Cuenta."""
        # Necesitamos simular el estado de cuenta para la IA
        
        balance_ratio = 0.0 # Asumimos balance neutral estable
        position_ratio = 1.0 if self.current_position > 0 else 0.0
        
        account_obs = np.full((self.window_size, 2), [balance_ratio, position_ratio], dtype=np.float32)
        
        # Combinar
        obs = np.hstack((market_data, account_obs))
        return obs

    def execute_trade(self, action, price):
        """Simula la ejecución de la orden (Modo Señales) con Gestión de Riesgo."""
        # 0: Hold, 1: Buy, 2: Sell
        
        # Timestamp actual
        now_dt = datetime.now()
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        now_ts = now_dt.timestamp()
        step = int(now_ts)

        # Update Equity Simulation (Floating PnL)
        current_equity = self.sim_balance
        if self.current_position == 1:
            floating_pnl = (price - self.entry_price) / self.entry_price * self.sim_balance # Full leverage simulation
            current_equity += floating_pnl
            
        # Check Prop Firm Rules
        self.check_prop_firm_rules(current_equity)

        # 1. MECHANICAL TAKE PROFIT CHECK (NEW - Secure Profits!)
        if self.current_position == 1:
            pnl_pct = (price - self.entry_price) / self.entry_price
            
            # Take Profit: Lock in gains at 2%
            if pnl_pct >= self.take_profit_pct:
                logger.info(f"🎯 TAKE PROFIT ACTIVADO a ${price:.2f} (Ganancia: +{pnl_pct*100:.2f}%)")
                self.notifier.notify_take_profit(self.symbol, price, pnl_pct*100)
                action = 2  # Force Sell
            
            # Stop Loss: Cut losses at 1.5%
            elif pnl_pct <= -self.stop_loss_pct:
                logger.warning(f"🛡️ STOP LOSS ACTIVADO a ${price:.2f} (Pérdida: {pnl_pct*100:.2f}%)")
                self.notifier.notify_stop_loss(self.symbol, price, pnl_pct*100)
                action = 2  # Force Sell
        
        # 2. COOLDOWN CHECK
        if action == 1 and self.current_position == 0:
            time_since_sell = now_ts - self.last_sell_time
            if time_since_sell < self.cooldown_seconds:
                hours_wait = (self.cooldown_seconds - time_since_sell) / 3600
                if hours_wait < 0.1: # Only log if close just to reduce noise? No, log always for debug
                    logger.info(f"❄️ Enfriamiento activo. Ignorando COMPRA. Espera {hours_wait:.2f}h más.")
                return # Abort trade

            logger.info(f"🟢 [COMPRA] SEÑAL DETECTADA a ${price:.2f} ({now_str})")
            logger.info(f"   👉 Sugerencia: Abrir LONG en {self.symbol}")
            self.notifier.notify_buy(self.symbol, price, self.sim_balance)
            self.current_position = 1
            self.entry_price = price
            self.trade_start_time = now_dt
            
            # Log BUY to database
            try:
                self.db.log_trade(
                    symbol=self.symbol,
                    action='BUY',
                    entry_price=price,
                    balance_after=self.sim_balance
                )
                self._save_state()
            except Exception as e:
                logger.error(f"Failed to log BUY trade: {e}")
            
        elif action == 2 and self.current_position > 0:
            logger.info(f"🔴 [VENTA] SEÑAL DETECTADA a ${price:.2f} ({now_str})")
            pnl_pct = (price - self.entry_price) / self.entry_price 
            
            # Update Sim Balance
            pnl_amount = self.sim_balance * pnl_pct
            self.sim_balance += pnl_amount
            
            if pnl_amount > 0: self.wins += 1
            else: self.losses += 1
            
            win_rate = (self.wins / (self.wins + self.losses)) * 100 if (self.wins+self.losses) > 0 else 0
            
            logger.info(f"   💰 Cierre. PnL: {pnl_pct*100:.2f}% | Balance Sim: ${self.sim_balance:.2f}")
            logger.info(f"   📊 ESTADO: WinRate: {win_rate:.1f}% | DD Diario Max: {self.max_daily_loss:.2f}%")
            
            # Telegram Notification
            self.notifier.notify_sell(
                self.symbol, 
                self.entry_price, 
                price, 
                pnl_pct*100, 
                pnl_amount, 
                self.sim_balance
            )
            
            # Calculate trade duration
            trade_duration = 0
            if self.trade_start_time:
                duration_delta = now_dt - self.trade_start_time
                trade_duration = int(duration_delta.total_seconds() / 60)  # minutes
            
            # Determine reason
            reason = ""
            if pnl_pct >= self.take_profit_pct:
                reason = "Take Profit"
            elif pnl_pct <= -self.stop_loss_pct:
                reason = "Stop Loss"
            else:
                reason = "Manual/Signal"
            
            # Log SELL to database
            try:
                self.db.log_trade(
                    symbol=self.symbol,
                    action='SELL',
                    entry_price=self.entry_price,
                    exit_price=price,
                    pnl_pct=pnl_pct * 100,
                    pnl_usd=pnl_amount,
                    balance_after=self.sim_balance,
                    reason=reason,
                    trade_duration_minutes=trade_duration
                )
                self._save_state()
            except Exception as e:
                logger.error(f"Failed to log SELL trade: {e}")

            # TENSORBOARD GRAPHING
            try:
                self.writer.add_scalar("FTMO_Sim/Balance", self.sim_balance, step)
                self.writer.add_scalar("FTMO_Sim/WinRate", win_rate, step)
                self.writer.add_scalar("FTMO_Risk/DailyDrawdown", self.max_daily_loss, step)
                self.writer.flush()
            except Exception as e:
                logger.error(f"Error escribiendo a TensorBoard: {e}")

            self.current_position = 0
            self.last_sell_time = now_ts # Start Cooldown Clock
            
        else:
            # Reducir ruido: Solo loggear Hold ocasionalmente o si cambia algo
            pass

    def run(self):
        logger.info(f"🚀 Iniciando Trader en Vivo (Señales) para {self.symbol}...")
        
        while True:
            # logger.info("⏳ Analizando mercado (Yahoo Finance)...")
            
            market_data, current_price = self.fetch_market_data()
            if market_data is not None:
                obs = self.construct_observation(market_data)
                
                # Predecir
                action, _ = self.model.predict(obs, deterministic=True)
                
                # Ejecutar
                self.execute_trade(action.item(), current_price)
            
            # Esperar 60 segundos antes de volver a chequear
            # Yahoo tiene retraso, no necesitamos consultar cada milisegundo
            time.sleep(60) 

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
    # No API keys needed for Yahoo
    trader = LiveTrader(asset)
    trader.run()
