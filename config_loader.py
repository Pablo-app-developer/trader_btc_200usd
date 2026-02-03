"""
Configuration Loader
Loads and validates configuration from YAML file
"""
import yaml
import os
from pathlib import Path

class BotConfig:
    def __init__(self, config_file="bot_config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_file):
            print(f"⚠️ Config file not found: {self.config_file}")
            print("   Using default configuration")
            return self.get_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✅ Configuration loaded from {self.config_file}")
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            print("   Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            'trading': {
                'capital_initial': 200,
                'max_position_size': 0.95
            },
            'risk_management': {
                'stop_loss_pct': 0.015,
                'take_profit_pct': 0.02,
                'max_daily_drawdown': 0.05,
                'cooldown_minutes': 120
            },
            'notifications': {
                'telegram': {
                    'enabled': True,
                    'config_file': 'telegram_config.json'
                }
            },
            'database': {
                'enabled': True,
                'path': 'trading_bot.db'
            },
            'logging': {
                'level': 'INFO',
                'file': 'live_trader.log'
            }
        }
    
    def get(self, *keys, default=None):
        """Get nested configuration value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def get_asset_config(self, symbol):
        """Get configuration for a specific asset"""
        assets = self.get('assets', default={})
        return assets.get(symbol, {})
    
    def is_asset_enabled(self, symbol):
        """Check if an asset is enabled"""
        asset_config = self.get_asset_config(symbol)
        return asset_config.get('enabled', True)
    
    def get_stop_loss(self, symbol):
        """Get stop loss for asset (custom or global)"""
        asset_config = self.get_asset_config(symbol)
        custom_sl = asset_config.get('custom_stop_loss')
        if custom_sl is not None:
            return custom_sl
        return self.get('risk_management', 'stop_loss_pct', default=0.015)
    
    def get_take_profit(self, symbol):
        """Get take profit for asset (custom or global)"""
        asset_config = self.get_asset_config(symbol)
        custom_tp = asset_config.get('custom_take_profit')
        if custom_tp is not None:
            return custom_tp
        return self.get('risk_management', 'take_profit_pct', default=0.02)
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self.load_config()
        print("🔄 Configuration reloaded")
    
    def save(self, config_file=None):
        """Save current configuration to file"""
        if config_file is None:
            config_file = self.config_file
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            print(f"✅ Configuration saved to {config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def print_config(self):
        """Print current configuration"""
        print("\n" + "="*50)
        print("📋 CURRENT CONFIGURATION")
        print("="*50)
        print(yaml.dump(self.config, default_flow_style=False, sort_keys=False))
        print("="*50 + "\n")

# Convenience function
def load_bot_config(config_file="bot_config.yaml"):
    """Load bot configuration"""
    return BotConfig(config_file)
