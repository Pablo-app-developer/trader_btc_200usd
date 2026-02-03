"""
Trading Database Manager
Stores all trades, performance metrics, and bot state persistently
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class TradingDatabase:
    def __init__(self, db_path="trading_bot.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        print(f"📊 Database initialized: {db_path}")
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                entry_price REAL,
                exit_price REAL,
                pnl_pct REAL,
                pnl_usd REAL,
                balance_after REAL,
                reason TEXT,
                win BOOLEAN,
                trade_duration_minutes INTEGER
            )
        ''')
        
        # Daily summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                symbol TEXT NOT NULL,
                starting_balance REAL,
                ending_balance REAL,
                total_trades INTEGER,
                wins INTEGER,
                losses INTEGER,
                total_pnl REAL,
                max_drawdown REAL,
                UNIQUE(date, symbol)
            )
        ''')
        
        # Bot state table (for recovery after restart)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_state (
                symbol TEXT PRIMARY KEY,
                current_balance REAL,
                current_position INTEGER,
                entry_price REAL,
                last_update DATETIME,
                wins INTEGER,
                losses INTEGER
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                balance REAL,
                win_rate REAL,
                profit_factor REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                total_trades INTEGER
            )
        ''')
        
        self.conn.commit()
        print("✅ Database tables created/verified")
    
    def log_trade(self, symbol, action, entry_price=None, exit_price=None, 
                   pnl_pct=None, pnl_usd=None, balance_after=None, reason="", 
                   trade_duration_minutes=0):
        """Log a trade to the database"""
        cursor = self.conn.cursor()
        
        win = None
        if pnl_usd is not None:
            win = pnl_usd > 0
        
        cursor.execute('''
            INSERT INTO trades (symbol, action, entry_price, exit_price, pnl_pct, 
                              pnl_usd, balance_after, reason, win, trade_duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, action, entry_price, exit_price, pnl_pct, pnl_usd, 
              balance_after, reason, win, trade_duration_minutes))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def update_bot_state(self, symbol, balance, position, entry_price, wins, losses):
        """Update or insert bot state"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO bot_state 
            (symbol, current_balance, current_position, entry_price, last_update, wins, losses)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, balance, position, entry_price, datetime.now(), wins, losses))
        self.conn.commit()
    
    def get_bot_state(self, symbol):
        """Retrieve bot state (for recovery after restart)"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM bot_state WHERE symbol = ?', (symbol,))
        row = cursor.fetchone()
        
        if row:
            return {
                'symbol': row[0],
                'balance': row[1],
                'position': row[2],
                'entry_price': row[3],
                'last_update': row[4],
                'wins': row[5],
                'losses': row[6]
            }
        return None
    
    def get_performance_summary(self, symbol=None, days=30):
        """Get performance summary for a symbol or all symbols"""
        cursor = self.conn.cursor()
        
        if symbol:
            query = '''
                SELECT 
                    symbol,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN win = 0 THEN 1 ELSE 0 END) as losses,
                    AVG(pnl_pct) as avg_pnl_pct,
                    SUM(pnl_usd) as total_pnl_usd,
                    MIN(balance_after) as min_balance,
                    MAX(balance_after) as max_balance
                FROM trades
                WHERE symbol = ? AND timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY symbol
            '''
            cursor.execute(query, (symbol, days))
        else:
            query = '''
                SELECT 
                    symbol,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN win = 0 THEN 1 ELSE 0 END) as losses,
                    AVG(pnl_pct) as avg_pnl_pct,
                    SUM(pnl_usd) as total_pnl_usd,
                    MIN(balance_after) as min_balance,
                    MAX(balance_after) as max_balance
                FROM trades
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY symbol
            '''
            cursor.execute(query, (days,))
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def get_recent_trades(self, symbol=None, limit=10):
        """Get recent trades"""
        cursor = self.conn.cursor()
        
        if symbol:
            cursor.execute('''
                SELECT * FROM trades 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (symbol, limit))
        else:
            cursor.execute('''
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def save_daily_summary(self, date, symbol, starting_balance, ending_balance,
                          total_trades, wins, losses, total_pnl, max_drawdown):
        """Save daily summary"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summary 
            (date, symbol, starting_balance, ending_balance, total_trades, 
             wins, losses, total_pnl, max_drawdown)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, symbol, starting_balance, ending_balance, total_trades,
              wins, losses, total_pnl, max_drawdown))
        self.conn.commit()
    
    def export_to_json(self, output_file="trades_export.json"):
        """Export all trades to JSON"""
        trades = self.get_recent_trades(limit=1000)
        with open(output_file, 'w') as f:
            json.dump(trades, f, indent=2, default=str)
        print(f"✅ Exported {len(trades)} trades to {output_file}")
    
    def get_statistics(self, symbol):
        """Get comprehensive statistics for a symbol"""
        cursor = self.conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) as wins,
                AVG(CASE WHEN win = 1 THEN pnl_pct ELSE NULL END) as avg_win_pct,
                AVG(CASE WHEN win = 0 THEN pnl_pct ELSE NULL END) as avg_loss_pct,
                MAX(pnl_pct) as best_trade_pct,
                MIN(pnl_pct) as worst_trade_pct,
                SUM(pnl_usd) as total_pnl_usd
            FROM trades
            WHERE symbol = ? AND action = 'SELL'
        ''', (symbol,))
        
        row = cursor.fetchone()
        if row and row[0] > 0:
            total_trades, wins, avg_win, avg_loss, best, worst, total_pnl = row
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'wins': wins,
                'losses': total_trades - wins,
                'win_rate': win_rate,
                'avg_win_pct': avg_win or 0,
                'avg_loss_pct': avg_loss or 0,
                'best_trade_pct': best or 0,
                'worst_trade_pct': worst or 0,
                'total_pnl_usd': total_pnl or 0
            }
        
        return None
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("📊 Database connection closed")
