"""
Test the integrated run_live_trader.py with database and YAML config
This verifies that all integrations work correctly
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import at module level
from trading_database import TradingDatabase as DB
from config_loader import load_bot_config as load_config

def test_integration():
    print("\n" + "="*60)
    print("🧪 TESTING INTEGRATION: Database + YAML Config")
    print("="*60 + "\n")
    
    # Test 1: Load YAML Configuration
    print("1️⃣ Testing YAML Configuration...")
    try:
        config = load_config()
        print(f"   ✅ Configuration loaded")
        
        # Check key values
        capital = config.get('trading', 'capital_initial')
        print(f"   💰 Initial Capital: ${capital}")
        
        sol_sl = config.get_stop_loss('SOL')
        sol_tp = config.get_take_profit('SOL')
        print(f"   🎯 SOL Risk: SL={sol_sl*100:.1f}%, TP={sol_tp*100:.1f}%")
        
        eth_sl = config.get_stop_loss('ETH')
        eth_tp = config.get_take_profit('ETH')
        print(f"   🎯 ETH Risk: SL={eth_sl*100:.1f}%, TP={eth_tp*100:.1f}%")
        
        btc_sl = config.get_stop_loss('BTC')
        btc_tp = config.get_take_profit('BTC')
        print(f"   🎯 BTC Risk: SL={btc_sl*100:.1f}%, TP={btc_tp*100:.1f}%")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Database Connection
    print("\n2️⃣ Testing Database Connection...")
    try:
        db = DB("trading_bot.db")
        print(f"   ✅ Database connected")
        
        # Check if we can query
        stats = db.get_statistics('SOL')
        if stats:
            print(f"   📊 SOL Stats: {stats['total_trades']} trades, {stats['win_rate']:.1f}% WR")
        else:
            print(f"   📊 SOL: No trades yet")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Check if all required files exist
    print("\n3️⃣ Checking Required Files...")
    required_files = [
        'run_live_trader.py',
        'trading_database.py',
        'config_loader.py',
        'bot_config.yaml',
        'telegram_notifier.py',
        'telegram_config.json'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            all_exist = False
    
    if not all_exist:
        print("\n   ⚠️ Some files are missing!")
        return False
    
    # Test 4: Verify imports work
    print("\n4️⃣ Testing Imports...")
    try:
        from run_live_trader import LiveTrader
        print(f"   ✅ LiveTrader imported successfully")
        
        from telegram_notifier import TelegramNotifier
        print(f"   ✅ TelegramNotifier imported successfully")
        
        from trading_database import TradingDatabase
        print(f"   ✅ TradingDatabase imported successfully")
        
        from config_loader import load_bot_config
        print(f"   ✅ load_bot_config imported successfully")
        
    except Exception as e:
        print(f"   ❌ Import Error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*60)
    print("\n🚀 Ready to deploy to VPS!")
    print("\nNext steps:")
    print("1. Copy files to VPS")
    print("2. Install dependencies: pip install pyyaml")
    print("3. Restart bots")
    print()
    
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
