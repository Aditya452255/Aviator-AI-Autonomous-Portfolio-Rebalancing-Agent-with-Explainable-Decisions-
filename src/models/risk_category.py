"""Risk category domain model."""

from pydantic import BaseModel, Field, model_validator
from src.core.constants import RiskCategoryName


class RiskCategory(BaseModel):
    """Domain model representing a robo-advisory risk profile category."""

    id: str = Field(..., description="Unique risk category identifier")
    name: str = Field(..., description="Human readable risk category name")
    target_equity: float = Field(..., ge=0.0, le=1.0, description="Target equity proportion")
    target_fixed_income: float = Field(..., ge=0.0, le=1.0, description="Target fixed income proportion")
    target_alternatives: float = Field(..., ge=0.0, le=1.0, description="Target alternatives proportion")
    target_cash: float = Field(..., ge=0.0, le=1.0, description="Target cash proportion")
    drift_threshold: float = Field(..., ge=0.01, le=0.20, description="Rebalancing drift trigger threshold")

    @model_validator(mode="after")
    def validate_weights_sum(self) -> "RiskCategory":
        """Ensure sum of target asset allocations equals 1.0 (100%)."""
        total = self.target_equity + self.target_fixed_income + self.target_alternatives + self.target_cash
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"Target allocations for {self.name} must sum to 1.0 (got {total:.4f})")
        return self
