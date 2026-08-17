"""Domain models for rebalancing triggers and rule evaluation results."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class TriggerType(StrEnum):
    """Broad category of rebalancing trigger."""

    THRESHOLD = "Threshold"
    CALENDAR = "Calendar"
    MARKET_EVENT = "Market Event"
    CLIENT_EVENT = "Client Event"


class TriggerReason(StrEnum):
    """Specific cause for triggering a rebalancing review."""

    EQUITY_DRIFT_BREACH = "Equity Drift Breach"
    FIXED_INCOME_DRIFT_BREACH = "Fixed Income Drift Breach"
    CASH_DRIFT_BREACH = "Cash Drift Breach"
    SCHEDULED_REBALANCE = "Scheduled Calendar Rebalance"
    MARKET_VOLATILITY_SPIKE = "Market Volatility Spike"
    MARKET_GAP = "Market Price Gap"
    SECTOR_CRASH = "Sector Crash Event"
    LARGE_CASH_DEPOSIT = "Large Cash Deposit"
    LARGE_CASH_WITHDRAWAL = "Large Cash Withdrawal"
    RISK_PROFILE_CHANGE = "Risk Profile Change"
    RETIRING_SOON = "Approaching Retirement Horizon"
    TAX_EVENT = "Tax Event"
    ESG_PREFERENCE_CHANGE = "ESG Preference Change"


class TriggerEvaluation(BaseModel):
    """Result of evaluating a specific trigger rule against a portfolio."""

    trigger_type: TriggerType = Field(..., description="Category of trigger")
    trigger_reason: TriggerReason = Field(..., description="Specific trigger reason")
    is_triggered: bool = Field(..., description="True if rule condition is satisfied")
    severity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Normalized severity rating (0 to 1)")
    message: str = Field(..., description="Explanatory text describing why the trigger fired")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
