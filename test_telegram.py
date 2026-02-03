"""
Test script for Telegram notifications
Run this to verify Telegram integration is working
"""
import json
from telegram_notifier import TelegramNotifier

def test_telegram():
    print("🧪 Testing Telegram Integration...")
    print("-" * 50)
    
    # Load config
    try:
        with open('telegram_config.json', 'r') as f:
            config = json.load(f)
            telegram_config = config['telegram']
        
        print(f"✅ Config loaded")
        print(f"   Bot Token: {telegram_config['bot_token'][:20]}...")
        print(f"   Chat ID: {telegram_config['chat_id']}")
        print()
        
        # Initialize notifier
        notifier = TelegramNotifier(
            bot_token=telegram_config['bot_token'],
            chat_id=telegram_config['chat_id'],
            enabled=True
        )
        
        print("✅ Notifier initialized")
        print()
        
        # Test different notification types
        print("📤 Sending test notifications...")
        print()
        
        # Test 1: Buy notification
        print("1️⃣ Testing BUY notification...")
        notifier.notify_buy("SOL", 120.50, 200.00)
        print("   ✅ Sent")
        
        # Test 2: Sell notification (profit)
        print("2️⃣ Testing SELL notification (profit)...")
        notifier.notify_sell("SOL", 120.50, 123.00, 2.07, 4.14, 204.14)
        print("   ✅ Sent")
        
        # Test 3: Stop Loss notification
        print("3️⃣ Testing STOP LOSS notification...")
        notifier.notify_stop_loss("BTC", 98500, -1.5)
        print("   ✅ Sent")
        
        # Test 4: Take Profit notification
        print("4️⃣ Testing TAKE PROFIT notification...")
        notifier.notify_take_profit("ETH", 3250, 2.0)
        print("   ✅ Sent")
        
        # Test 5: Daily summary
        print("5️⃣ Testing DAILY SUMMARY notification...")
        notifier.notify_daily_summary("SOL", 210.50, 5, 3, 2, 10.50)
        print("   ✅ Sent")
        
        # Test 6: Error notification
        print("6️⃣ Testing ERROR notification...")
        notifier.notify_error("ETH", "Connection timeout to exchange")
        print("   ✅ Sent")
        
        print()
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print()
        print("📱 Check your Telegram app for the test messages!")
        
    except FileNotFoundError:
        print("❌ Error: telegram_config.json not found")
        print("   Create the file with your Telegram credentials")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_telegram()
