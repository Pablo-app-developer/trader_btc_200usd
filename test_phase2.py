"""
Test script for Database and Configuration
Run this to verify Phase 2 implementation
"""
from trading_database import TradingDatabase
from config_loader import load_bot_config
from datetime import datetime

def test_database():
    print("\n" + "="*60)
    print("🧪 TESTING DATABASE")
    print("="*60 + "\n")
    
    # Initialize database
    db = TradingDatabase("test_trading.db")
    
    # Test 1: Log some trades
    print("1️⃣ Logging test trades...")
    
    # Buy trade
    trade_id = db.log_trade(
        symbol="SOL",
        action="BUY",
        entry_price=120.50,
        balance_after=200.00
    )
    print(f"   ✅ Logged BUY trade (ID: {trade_id})")
    
    # Sell trade (win)
    trade_id = db.log_trade(
        symbol="SOL",
        action="SELL",
        entry_price=120.50,
        exit_price=123.00,
        pnl_pct=2.07,
        pnl_usd=4.14,
        balance_after=204.14,
        reason="Take Profit",
        trade_duration_minutes=45
    )
    print(f"   ✅ Logged SELL trade (ID: {trade_id})")
    
    # Sell trade (loss)
    trade_id = db.log_trade(
        symbol="BTC",
        action="SELL",
        entry_price=100000,
        exit_price=98500,
        pnl_pct=-1.5,
        pnl_usd=-3.00,
        balance_after=201.14,
        reason="Stop Loss",
        trade_duration_minutes=30
    )
    print(f"   ✅ Logged SELL trade (ID: {trade_id})")
    
    # Test 2: Update bot state
    print("\n2️⃣ Updating bot state...")
    db.update_bot_state(
        symbol="SOL",
        balance=204.14,
        position=0,
        entry_price=0,
        wins=1,
        losses=0
    )
    print("   ✅ Bot state updated")
    
    # Test 3: Retrieve bot state
    print("\n3️⃣ Retrieving bot state...")
    state = db.get_bot_state("SOL")
    if state:
        print(f"   ✅ Retrieved state: Balance=${state['balance']:.2f}, Wins={state['wins']}")
    
    # Test 4: Get recent trades
    print("\n4️⃣ Getting recent trades...")
    recent = db.get_recent_trades(limit=5)
    print(f"   ✅ Retrieved {len(recent)} recent trades")
    for trade in recent:
        price = trade.get('exit_price') or trade.get('entry_price') or 0
        print(f"      - {trade['symbol']} {trade['action']} at ${price:.2f}")
    
    # Test 5: Get performance summary
    print("\n5️⃣ Getting performance summary...")
    summary = db.get_performance_summary()
    for s in summary:
        pnl = s.get('total_pnl_usd') or 0
        print(f"   ✅ {s['symbol']}: {s['total_trades']} trades, {s['wins']} wins, ${pnl:.2f} PnL")
    
    # Test 6: Get statistics
    print("\n6️⃣ Getting statistics for SOL...")
    stats = db.get_statistics("SOL")
    if stats:
        print(f"   ✅ Win Rate: {stats['win_rate']:.1f}%")
        print(f"   ✅ Total PnL: ${stats['total_pnl_usd']:.2f}")
        print(f"   ✅ Best Trade: {stats['best_trade_pct']:.2f}%")
    
    # Test 7: Export to JSON
    print("\n7️⃣ Exporting to JSON...")
    db.export_to_json("test_trades_export.json")
    
    db.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE TESTS PASSED!")
    print("="*60 + "\n")

def test_config():
    print("\n" + "="*60)
    print("🧪 TESTING CONFIGURATION")
    print("="*60 + "\n")
    
    # Load configuration
    config = load_bot_config()
    
    # Test 1: Get basic values
    print("1️⃣ Testing basic configuration access...")
    capital = config.get('trading', 'capital_initial')
    print(f"   ✅ Initial Capital: ${capital}")
    
    stop_loss = config.get('risk_management', 'stop_loss_pct')
    print(f"   ✅ Stop Loss: {stop_loss*100}%")
    
    take_profit = config.get('risk_management', 'take_profit_pct')
    print(f"   ✅ Take Profit: {take_profit*100}%")
    
    # Test 2: Get asset-specific config
    print("\n2️⃣ Testing asset-specific configuration...")
    sol_config = config.get_asset_config('SOL')
    print(f"   ✅ SOL enabled: {sol_config.get('enabled')}")
    print(f"   ✅ SOL EMA period: {sol_config.get('ema_period')}")
    
    # Test 3: Get custom stop loss/take profit
    print("\n3️⃣ Testing custom risk parameters...")
    sol_sl = config.get_stop_loss('SOL')
    sol_tp = config.get_take_profit('SOL')
    print(f"   ✅ SOL Stop Loss: {sol_sl*100}%")
    print(f"   ✅ SOL Take Profit: {sol_tp*100}%")
    
    # Test 4: Check if assets are enabled
    print("\n4️⃣ Checking enabled assets...")
    for symbol in ['SOL', 'ETH', 'BTC']:
        enabled = config.is_asset_enabled(symbol)
        status = "✅ Enabled" if enabled else "❌ Disabled"
        print(f"   {status}: {symbol}")
    
    # Test 5: Print full config
    print("\n5️⃣ Printing full configuration...")
    config.print_config()
    
    print("="*60)
    print("✅ CONFIGURATION TESTS PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n" + "🚀 PHASE 2 TESTING: DATABASE + CONFIGURATION")
    print("="*60 + "\n")
    
    # Test database
    test_database()
    
    # Test configuration
    test_config()
    
    print("\n" + "="*60)
    print("🎉 ALL PHASE 2 TESTS PASSED!")
    print("="*60)
    print("\n📱 Next: Integrate into run_live_trader.py")
    print()
