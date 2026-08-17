"""Domain models for portfolio drift calculation and monitoring metrics."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AssetClassDrift(BaseModel):
    """Drift metrics for a specific asset category."""

    asset_category: str = Field(..., description="High-level asset category (Equity, Fixed Income, Alternatives, Cash)")
    target_weight: float = Field(..., ge=0.0, le=1.0)
    current_weight: float = Field(..., ge=0.0, le=1.0)
    absolute_drift: float = Field(..., description="|current - target|")
    relative_drift: float = Field(..., description="|current - target| / target")
    is_breached: bool = Field(default=False, description="True if absolute drift > category drift threshold")


class SectorDrift(BaseModel):
    """Drift metrics for a specific economic sector."""

    sector: str = Field(..., description="Economic sector name")
    current_weight: float = Field(..., ge=0.0, le=1.0)
    target_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    absolute_drift: float = Field(..., description="Sector weight deviation")


class SecurityDrift(BaseModel):
    """Drift metrics for a specific holding security."""

    ticker: str = Field(..., description="Security ticker symbol")
    asset_category: str = Field(..., description="Asset category")
    target_weight: float = Field(..., ge=0.0, le=1.0)
    current_weight: float = Field(..., ge=0.0, le=1.0)
    absolute_drift: float = Field(..., description="|current - target|")
    relative_drift: float = Field(..., description="|current - target| / target")


class PortfolioDriftMetrics(BaseModel):
    """Aggregated multi-dimensional drift metrics for a portfolio."""

    portfolio_id: str = Field(..., description="Portfolio identifier")
    client_id: str = Field(..., description="Client identifier")
    risk_category: str = Field(..., description="Assigned risk category key")
    total_absolute_drift: float = Field(..., ge=0.0, description="Sum of absolute asset category drifts")
    portfolio_drift_score: float = Field(..., ge=0.0, description="Root Mean Square (RMS) drift metric")
    cash_drift: float = Field(..., description="Current cash weight minus target cash weight")
    max_drift_asset_class: str = Field(..., description="Asset category with maximum absolute drift")
    max_drift_value: float = Field(..., ge=0.0, description="Value of maximum absolute drift")
    asset_drifts: Dict[str, AssetClassDrift] = Field(..., description="Map of category name to AssetClassDrift")
    sector_drifts: Dict[str, SectorDrift] = Field(default_factory=dict, description="Map of sector name to SectorDrift")
    security_drifts: List[SecurityDrift] = Field(default_factory=list, description="List of SecurityDrift records")
    is_rebalance_candidate: bool = Field(default=False, description="True if any trigger condition or drift breach occurs")
