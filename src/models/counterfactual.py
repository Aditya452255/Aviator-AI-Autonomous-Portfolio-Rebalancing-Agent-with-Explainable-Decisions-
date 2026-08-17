"""Counterfactual explanation domain models."""

from typing import Dict, List
from pydantic import BaseModel, Field


class CounterfactualExplanation(BaseModel):
    """Minimum-change counterfactual explanation."""

    feature_name: str = Field(..., description="Feature evaluated")
    current_value: float = Field(..., description="Current observed feature value")
    counterfactual_value: float = Field(..., description="Counterfactual threshold value")
    current_decision: str = Field(..., description="Observed decision (e.g. REBALANCE)")
    counterfactual_decision: str = Field(..., description="Counterfactual decision (e.g. NO_REBALANCE)")
    impact_description: str = Field(..., description="Human readable description")


class CounterfactualSummary(BaseModel):
    """Collection of counterfactual scenarios for a portfolio."""

    portfolio_id: str = Field(..., description="Target portfolio ID")
    counterfactuals: List[CounterfactualExplanation] = Field(default_factory=list, description="Counterfactual list")
