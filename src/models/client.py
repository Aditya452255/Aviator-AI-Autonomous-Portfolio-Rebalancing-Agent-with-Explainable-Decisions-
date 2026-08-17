"""Client profile domain model."""

from typing import List
from pydantic import BaseModel, Field
from src.core.constants import Country, ESGPreference, RiskCategoryKey, TaxBracket


class ClientProfile(BaseModel):
    """Domain model representing an investor client profile managed by Aviator AI."""

    client_id: str = Field(..., description="Unique client identifier (e.g. CLT_00001)")
    name: str = Field(..., description="Full client name")
    risk_category: RiskCategoryKey = Field(..., description="Assigned risk category key")
    tax_bracket: TaxBracket = Field(..., description="Client tax bracket")
    investment_horizon: int = Field(..., ge=1, le=50, description="Investment horizon in years")
    annual_income: float = Field(..., ge=0.0, description="Annual income in base currency")
    portfolio_size: float = Field(..., ge=1000.0, description="Total portfolio value in base currency")
    esg_preference: ESGPreference = Field(..., description="ESG preference level")
    restricted_securities: List[str] = Field(default_factory=list, description="List of restricted ticker symbols")
    upcoming_cash_flow: float = Field(default=0.0, description="Upcoming cash deposit (positive) or withdrawal (negative)")
    country: Country = Field(default=Country.INDIA, description="Country of residence")
