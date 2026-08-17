"""Unit tests for configuration loader and Pydantic models."""

from pathlib import Path
import pytest
from src.core.config import AppConfig, load_config
from src.core.exceptions import ConfigurationError
from src.models.risk_category import RiskCategory


def test_load_config_success() -> None:
    """Test loading valid configuration directory."""
    config = load_config("config")
    assert isinstance(config, AppConfig)
    assert config.app.name == "Aviator AI Autonomous Portfolio Rebalancing Agent"
    assert config.simulation.num_clients == 50000
    assert config.simulation.num_portfolios == 50000
    assert config.simulation.num_securities == 500
    assert config.simulation.trading_days == 252


def test_risk_categories_config() -> None:
    """Test risk categories loading and validation."""
    config = load_config("config")
    assert "balanced" in config.risk_categories
    assert "ultra_conservative" in config.risk_categories

    bal = config.risk_categories["balanced"]
    assert bal.name == "Balanced"
    assert bal.target_equity == 0.50
    assert bal.target_fixed_income == 0.35
    assert bal.target_alternatives == 0.10
    assert bal.target_cash == 0.05
    assert round(bal.target_equity + bal.target_fixed_income + bal.target_alternatives + bal.target_cash, 2) == 1.0


def test_risk_category_model_validation() -> None:
    """Test RiskCategory Pydantic validator for invalid weight sum."""
    with pytest.raises(ValueError, match="must sum to 1.0"):
        RiskCategory(
            id="RC_BAD",
            name="Invalid Category",
            target_equity=0.50,
            target_fixed_income=0.50,
            target_alternatives=0.20,  # Sum = 1.20
            target_cash=0.0,
            drift_threshold=0.05,
        )


def test_invalid_config_directory() -> None:
    """Test error raised when invalid config path is supplied."""
    with pytest.raises(ConfigurationError):
        load_config("non_existent_config_folder")
