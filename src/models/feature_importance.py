"""Feature importance and attribution domain models."""

from typing import List
from pydantic import BaseModel, Field


class FeatureAttribution(BaseModel):
    """Local and global feature attribution metrics."""

    feature_name: str = Field(..., description="Feature identifier")
    global_importance: float = Field(..., description="Global feature importance score")
    local_importance: float = Field(..., description="Local SHAP value magnitude")
    normalized_contribution: float = Field(..., description="Percentage contribution to decision")
    signed_contribution: float = Field(..., description="Directional signed SHAP value")


class FeatureAttributionSummary(BaseModel):
    """Collection of ranked feature attributions."""

    portfolio_id: str = Field(..., description="Target portfolio ID")
    attributions: List[FeatureAttribution] = Field(default_factory=list, description="Ranked attributions")
    top_driver: str = Field(..., description="Primary feature driving decision")
