"""
Healthcheck API for Trading Bot
Provides system status, bot health, and metrics via HTTP endpoint
"""
from flask import Flask, jsonify
import psutil
import time
import os
from datetime import datetime
from trading_database import TradingDatabase

app = Flask(__name__)

# Global variables
start_time = time.time()
last_trade_time = {}

@app.route('/health')
def health():
    """Main health check endpoint"""
    uptime_seconds = time.time() - start_time
    uptime_hours = uptime_seconds / 3600
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_hours": round(uptime_hours, 2),
        "system": get_system_metrics(),
        "bots": get_bot_status(),
        "database": check_database()
    })

@app.route('/metrics')
def metrics():
    """Detailed metrics endpoint"""
    db = TradingDatabase()
    
    metrics_data = {
        "timestamp": datetime.now().isoformat(),
        "performance": {},
        "recent_trades": []
    }
    
    # Get performance for each asset
    for symbol in ['SOL', 'ETH', 'BTC']:
        stats = db.get_statistics(symbol)
        if stats:
            metrics_data["performance"][symbol] = stats
    
    # Get recent trades
    recent = db.get_recent_trades(limit=10)
    metrics_data["recent_trades"] = recent
    
    db.close()
    
    return jsonify(metrics_data)

@app.route('/status/<symbol>')
def bot_status(symbol):
    """Get status for specific bot"""
    symbol = symbol.upper()
    
    db = TradingDatabase()
    state = db.get_bot_state(symbol)
    stats = db.get_statistics(symbol)
    db.close()
    
    if state is None:
        return jsonify({
            "error": f"Bot {symbol} not found",
            "status": "unknown"
        }), 404
    
    return jsonify({
        "symbol": symbol,
        "status": "active" if state['position'] > 0 else "idle",
        "balance": state['balance'],
        "position": state['position'],
        "entry_price": state['entry_price'],
        "wins": state['wins'],
        "losses": state['losses'],
        "last_update": state['last_update'],
        "statistics": stats
    })

def get_system_metrics():
    """Get system resource usage"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "process_count": len(psutil.pids())
    }

def get_bot_status():
    """Get status of all bots"""
    db = TradingDatabase()
    
    bots = {}
    for symbol in ['SOL', 'ETH', 'BTC']:
        state = db.get_bot_state(symbol)
        if state:
            bots[symbol] = {
                "status": "active" if state['position'] > 0 else "idle",
                "balance": state['balance'],
                "wins": state['wins'],
                "losses": state['losses'],
                "last_update": state['last_update']
            }
        else:
            bots[symbol] = {
                "status": "not_started",
                "balance": 0,
                "wins": 0,
                "losses": 0
            }
    
    db.close()
    return bots

def check_database():
    """Check database health"""
    db_path = "trading_bot.db"
    
    if not os.path.exists(db_path):
        return {
            "status": "missing",
            "path": db_path
        }
    
    try:
        db = TradingDatabase(db_path)
        recent = db.get_recent_trades(limit=1)
        db.close()
        
        return {
            "status": "healthy",
            "path": db_path,
            "size_mb": round(os.path.getsize(db_path) / (1024 * 1024), 2),
            "last_trade": recent[0]['timestamp'] if recent else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.route('/')
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        "name": "Trading Bot Health API",
        "version": "1.0",
        "endpoints": {
            "/health": "Overall system health",
            "/metrics": "Detailed trading metrics",
            "/status/<symbol>": "Status for specific bot (SOL, ETH, BTC)"
        },
        "example": "http://localhost:5000/health"
    })

if __name__ == '__main__':
    print("🏥 Starting Healthcheck API on port 5000...")
    print("📊 Access dashboard at: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=False)
