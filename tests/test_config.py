import pytest
from unittest.mock import Mock, patch
from config import get_asset_config, AssetConfig

def test_load_asset_config_valid():
    """Test loading configuration for a known asset."""
    config = get_asset_config("SOL")
    assert isinstance(config, AssetConfig)
    assert config.name == "SOL"
    assert config.env_params["risk_aversion"] == 1.2
    assert config.env_params["cooldown_steps"] == 8

def test_load_asset_config_lowercase():
    """Test loading configuration with lowercase symbol."""
    config = get_asset_config("eth")
    assert config.name == "ETH"
    assert config.env_params["ema_penalty"] == 0.03

def test_load_asset_config_invalid():
    """Test loading configuration for an unknown asset."""
    config = get_asset_config("DOGE")
    assert config is None
