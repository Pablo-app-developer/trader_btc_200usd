"""
Create sample trading data for dashboard testing
This populates the database with realistic trading scenarios
"""
from trading_database import TradingDatabase
from datetime import datetime, timedelta
import random

def create_sample_data():
    print("🎲 Creating sample trading data...")
    print("-" * 60)
    
    db = TradingDatabase("trading_bot.db")
    
    # Starting balance
    balance = 200.0
    
    # Simulate trades over the last 7 days
    start_date = datetime.now() - timedelta(days=7)
    
    symbols = ['SOL', 'ETH', 'BTC']
    
    trade_count = 0
    
    for symbol in symbols:
        print(f"\n📊 Creating trades for {symbol}...")
        
        symbol_balance = balance
        wins = 0
        losses = 0
        
        # Create 10-15 trades per symbol
        num_trades = random.randint(10, 15)
        
        for i in range(num_trades):
            # Random time within the 7 days
            trade_time = start_date + timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Entry price (realistic ranges)
            if symbol == 'SOL':
                entry_price = random.uniform(115, 125)
            elif symbol == 'ETH':
                entry_price = random.uniform(3200, 3300)
            else:  # BTC
                entry_price = random.uniform(98000, 102000)
            
            # BUY trade
            db.log_trade(
                symbol=symbol,
                action='BUY',
                entry_price=entry_price,
                balance_after=symbol_balance
            )
            
            # Simulate holding time
            hold_minutes = random.randint(30, 180)
            
            # Exit with profit or loss (60% win rate)
            is_win = random.random() < 0.6
            
            if is_win:
                # Win: 1.5% to 2.5% profit
                pnl_pct = random.uniform(1.5, 2.5)
                wins += 1
            else:
                # Loss: -0.5% to -1.5%
                pnl_pct = random.uniform(-1.5, -0.5)
                losses += 1
            
            exit_price = entry_price * (1 + pnl_pct / 100)
            pnl_usd = symbol_balance * (pnl_pct / 100)
            symbol_balance += pnl_usd
            
            reason = "Take Profit" if is_win else "Stop Loss"
            
            # SELL trade
            db.log_trade(
                symbol=symbol,
                action='SELL',
                entry_price=entry_price,
                exit_price=exit_price,
                pnl_pct=pnl_pct,
                pnl_usd=pnl_usd,
                balance_after=symbol_balance,
                reason=reason,
                trade_duration_minutes=hold_minutes
            )
            
            trade_count += 1
        
        # Update bot state
        db.update_bot_state(
            symbol=symbol,
            balance=symbol_balance,
            position=0,
            entry_price=0,
            wins=wins,
            losses=losses
        )
        
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        total_pnl = symbol_balance - balance
        
        print(f"   ✅ {num_trades} trades created")
        print(f"   💰 Final Balance: ${symbol_balance:.2f}")
        print(f"   📈 Total PnL: ${total_pnl:+.2f}")
        print(f"   🎯 Win Rate: {win_rate:.1f}%")
    
    db.close()
    
    print("\n" + "=" * 60)
    print(f"✅ Sample data created successfully!")
    print(f"📊 Total trades: {trade_count}")
    print("=" * 60)
    print("\n🚀 Now you can run the dashboard:")
    print("   streamlit run dashboard.py")
    print()

if __name__ == "__main__":
    create_sample_data()
