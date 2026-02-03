"""
Telegram Notifier for Trading Bot
Sends real-time alerts for trades, errors, and daily summaries
"""
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token, chat_id, enabled=True):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        if self.enabled:
            self._test_connection()
    
    def _test_connection(self):
        """Test Telegram connection on initialization"""
        try:
            self.send_message("🤖 Bot de Trading Iniciado\n\nConexión a Telegram establecida correctamente.")
            logger.info("✅ Telegram notifier initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram: {e}")
            self.enabled = False
    
    def send_message(self, message, parse_mode="HTML"):
        """Send a message to Telegram"""
        if not self.enabled:
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def notify_buy(self, symbol, price, balance):
        """Notify when a BUY signal is detected"""
        message = f"""
🟢 <b>COMPRA DETECTADA</b>

💎 <b>Activo:</b> {symbol}
💰 <b>Precio:</b> ${price:.2f}
💵 <b>Balance:</b> ${balance:.2f}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
"""
        self.send_message(message)
    
    def notify_sell(self, symbol, entry_price, exit_price, pnl_pct, pnl_usd, balance, reason=""):
        """Notify when a SELL signal is detected"""
        emoji = "🟢" if pnl_usd > 0 else "🔴"
        profit_emoji = "📈" if pnl_usd > 0 else "📉"
        
        message = f"""
{emoji} <b>VENTA EJECUTADA</b>

💎 <b>Activo:</b> {symbol}
📊 <b>Entrada:</b> ${entry_price:.2f}
📊 <b>Salida:</b> ${exit_price:.2f}
{profit_emoji} <b>PnL:</b> {pnl_pct:+.2f}% (${pnl_usd:+.2f})
💵 <b>Balance:</b> ${balance:.2f}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
"""
        if reason:
            message += f"\n🎯 <b>Razón:</b> {reason}"
        
        self.send_message(message)
    
    def notify_daily_summary(self, symbol, balance, trades_today, wins, losses, pnl_today):
        """Send daily performance summary"""
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        emoji = "🎉" if pnl_today > 0 else "😔" if pnl_today < 0 else "😐"
        
        message = f"""
📅 <b>RESUMEN DIARIO - {symbol}</b>

{emoji} <b>Balance:</b> ${balance:.2f}
📊 <b>Operaciones:</b> {trades_today}
✅ <b>Ganadoras:</b> {wins}
❌ <b>Perdedoras:</b> {losses}
📈 <b>Win Rate:</b> {win_rate:.1f}%
💰 <b>PnL Hoy:</b> ${pnl_today:+.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        self.send_message(message)
    
    def notify_error(self, symbol, error_message):
        """Notify when an error occurs"""
        message = f"""
⚠️ <b>ERROR DETECTADO</b>

💎 <b>Bot:</b> {symbol}
❌ <b>Error:</b> {error_message}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}

<i>Revisa los logs para más detalles</i>
"""
        self.send_message(message)
    
    def notify_stop_loss(self, symbol, price, pnl_pct):
        """Notify when stop loss is triggered"""
        message = f"""
🛡️ <b>STOP LOSS ACTIVADO</b>

💎 <b>Activo:</b> {symbol}
💰 <b>Precio:</b> ${price:.2f}
📉 <b>Pérdida:</b> {pnl_pct:.2f}%
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}

<i>Protección de capital activada</i>
"""
        self.send_message(message)
    
    def notify_take_profit(self, symbol, price, pnl_pct):
        """Notify when take profit is triggered"""
        message = f"""
🎯 <b>TAKE PROFIT ACTIVADO</b>

💎 <b>Activo:</b> {symbol}
💰 <b>Precio:</b> ${price:.2f}
📈 <b>Ganancia:</b> +{pnl_pct:.2f}%
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}

<i>¡Ganancias aseguradas!</i>
"""
        self.send_message(message)
