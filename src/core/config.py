"""Centralized configuration loader supporting YAML files, environment variables, and Pydantic v2 models."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.exceptions import ConfigurationError
from src.core.logger import get_logger, setup_logger

logger = get_logger(__name__)


class RiskCategoryConfigItem(BaseModel):
    """Configuration definition for a single risk category."""

    id: str
    name: str
    target_equity: float = Field(..., ge=0.0, le=1.0)
    target_fixed_income: float = Field(..., ge=0.0, le=1.0)
    target_alternatives: float = Field(..., ge=0.0, le=1.0)
    target_cash: float = Field(..., ge=0.0, le=1.0)
    drift_threshold: float = Field(..., ge=0.01, le=0.20)

    @field_validator("target_cash")
    @classmethod
    def validate_total_allocation(cls, v: float, info: Any) -> float:
        """Validate that total asset allocations sum to 1.0."""
        data = info.data
        if "target_equity" in data and "target_fixed_income" in data and "target_alternatives" in data:
            total = data["target_equity"] + data["target_fixed_income"] + data["target_alternatives"] + v
            if not (0.999 <= total <= 1.001):
                raise ValueError(f"Target allocations must sum to 1.0 (got {total:.4f})")
        return v


class PortfolioThresholdsConfig(BaseModel):
    """Portfolio boundary constraints configuration."""

    min_securities: int = Field(default=15, ge=1)
    max_securities: int = Field(default=40, le=100)
    max_single_security_weight: float = Field(default=0.15, gt=0.0, le=1.0)
    min_single_security_weight: float = Field(default=0.005, ge=0.0)


class SecurityThresholdsConfig(BaseModel):
    """Security parameter bounds configuration."""

    min_liquidity_score: float = Field(default=1.0, ge=0.0)
    max_liquidity_score: float = Field(default=100.0, le=100.0)


class ValidationThresholdsConfig(BaseModel):
    """Data validation rules tolerance thresholds."""

    weight_sum_tolerance: float = Field(default=0.0001, gt=0.0)
    min_market_value: float = Field(default=0.01, gt=0.0)


class ThresholdsConfig(BaseModel):
    """Aggregated system thresholds configuration."""

    portfolio: PortfolioThresholdsConfig = Field(default_factory=PortfolioThresholdsConfig)
    security: SecurityThresholdsConfig = Field(default_factory=SecurityThresholdsConfig)
    validation: ValidationThresholdsConfig = Field(default_factory=ValidationThresholdsConfig)


class AppConfigDetail(BaseModel):
    """General application metadata."""

    name: str = "Aviator AI Autonomous Portfolio Rebalancing Agent"
    version: str = "1.0.0"
    company: str = "Aviator AI"
    random_seed: int = 42
    environment: str = "development"


class SimulationConfigDetail(BaseModel):
    """Simulation engine setup parameters."""

    num_clients: int = Field(default=50000, ge=1)
    num_portfolios: int = Field(default=50000, ge=1)
    num_securities: int = Field(default=500, ge=10)
    trading_days: int = Field(default=252, ge=1)
    start_date: str = "2025-01-01"


class StorageConfigDetail(BaseModel):
    """Data storage location and format parameters."""

    output_dir: str = "data/output"
    format: str = "parquet"
    save_csv: bool = True


class ConsoleLoggingConfig(BaseModel):
    """Console logger parameters."""

    enabled: bool = True
    level: str = "INFO"
    format: Optional[str] = None


class FileLoggingConfig(BaseModel):
    """File logger parameters."""

    enabled: bool = True
    path: str = "logs/application.log"
    level: str = "DEBUG"
    rotation: str = "10 MB"
    retention: str = "10 days"
    compression: str = "zip"
    format: Optional[str] = None


class LoggingConfigDetail(BaseModel):
    """Aggregated logging configuration."""

    level: str = "INFO"
    console: ConsoleLoggingConfig = Field(default_factory=ConsoleLoggingConfig)
    file: FileLoggingConfig = Field(default_factory=FileLoggingConfig)


class AppConfig(BaseSettings):
    """Master application configuration class combining YAML and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    app: AppConfigDetail = Field(default_factory=AppConfigDetail)
    simulation: SimulationConfigDetail = Field(default_factory=SimulationConfigDetail)
    storage: StorageConfigDetail = Field(default_factory=StorageConfigDetail)
    risk_categories: Dict[str, RiskCategoryConfigItem] = Field(default_factory=dict)
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    logging: LoggingConfigDetail = Field(default_factory=LoggingConfigDetail)


def _load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Helper to read and parse a YAML file safely.

    Args:
        file_path: Path to YAML file.

    Returns:
        Dictionary parsed from YAML.

    Raises:
        ConfigurationError: If file is missing or invalid YAML.
    """
    if not file_path.exists():
        raise ConfigurationError(f"Configuration file not found at: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content or {}
    except Exception as e:
        raise ConfigurationError(f"Error parsing YAML file {file_path}: {e}") from e


def load_config(config_dir: str | Path = "config") -> AppConfig:
    """Load enterprise configuration from YAML files and environment variable overrides.

    Args:
        config_dir: Directory path containing configuration YAML files.

    Returns:
        Validated strongly typed AppConfig instance.
    """
    config_path = Path(config_dir)

    default_data = _load_yaml_file(config_path / "default.yaml")
    risk_data = _load_yaml_file(config_path / "risk_categories.yaml")
    thresholds_data = _load_yaml_file(config_path / "thresholds.yaml")
    logging_data = _load_yaml_file(config_path / "logging.yaml")

    merged_data: Dict[str, Any] = {}

    if "app" in default_data:
        merged_data["app"] = default_data["app"]
    if "simulation" in default_data:
        merged_data["simulation"] = default_data["simulation"]
    if "storage" in default_data:
        merged_data["storage"] = default_data["storage"]

    if "risk_categories" in risk_data:
        merged_data["risk_categories"] = risk_data["risk_categories"]

    if thresholds_data:
        merged_data["thresholds"] = thresholds_data

    if "logging" in logging_data:
        merged_data["logging"] = logging_data["logging"]

    # Environment variable overrides
    env_random_seed = os.getenv("SIMULATION_RANDOM_SEED")
    if env_random_seed is not None and "app" in merged_data:
        merged_data["app"]["random_seed"] = int(env_random_seed)

    env_output_dir = os.getenv("DATA_OUTPUT_DIR")
    if env_output_dir is not None and "storage" in merged_data:
        merged_data["storage"]["output_dir"] = env_output_dir

    env_log_level = os.getenv("LOG_LEVEL")
    if env_log_level is not None and "logging" in merged_data:
        merged_data["logging"]["level"] = env_log_level
        merged_data["logging"]["console"]["level"] = env_log_level

    try:
        config = AppConfig(**merged_data)
        # Initialize logger with loaded configuration
        setup_logger(
            log_level=config.logging.level,
            log_file=config.logging.file.path if config.logging.file.enabled else "",
            rotation=config.logging.file.rotation,
            retention=config.logging.file.retention,
            console_enabled=config.logging.console.enabled,
        )
        logger.info(f"Loaded configuration for {config.app.name} v{config.app.version}")
        return config
    except Exception as e:
        raise ConfigurationError(f"Configuration validation failed: {e}") from e
