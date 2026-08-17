"""Scenario and stress testing result domain models."""

from typing import Dict, List
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class ScenarioType(StrEnum):
    """Types of market scenario simulations and stress tests."""

    BULL_MARKET = "BULL_MARKET"
    BEAR_MARKET = "BEAR_MARKET"
    SIDEWAYS = "SIDEWAYS"
    HIGH_INFLATION = "HIGH_INFLATION"
    INTEREST_RATE_SHOCK = "INTEREST_RATE_SHOCK"
    LIQUIDITY_CRISIS = "LIQUIDITY_CRISIS"
    SECTOR_CRASH = "SECTOR_CRASH"
    BLACK_SWAN = "BLACK_SWAN"
    CRASH_20_PCT = "CRASH_20_PCT"
    CRASH_35_PCT = "CRASH_35_PCT"


class ScenarioResult(BaseModel):
    """Simulation result under specific market scenario shock."""

    scenario_id: str = Field(..., description="Unique scenario run ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    scenario_type: ScenarioType = Field(..., description="Scenario type classification")
    portfolio_return: float = Field(..., description="Portfolio return during scenario")
    max_drawdown: float = Field(..., description="Maximum drawdown during scenario")
    var_95: float = Field(..., description="Value at Risk (95%) during scenario")
    cvar_95: float = Field(..., description="Conditional VaR (95%)")
    recovery_days: int = Field(..., description="Recovery time in trading days")
    survival_status: str = Field(default="PASSED", description="Survival status: PASSED, BREACH, CRITICAL")
