"""Market data domain models."""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class MarketDataPoint(BaseModel):
    """Single trading day OHLCV data point for a security."""

    ticker: str = Field(..., description="Security ticker symbol")
    date: str = Field(..., description="Trading date in YYYY-MM-DD format")
    trading_day: int = Field(..., ge=0, description="Sequential trading day index (0 to 251)")
    open_price: float = Field(..., gt=0.0, description="Opening price")
    high_price: float = Field(..., gt=0.0, description="Highest price during trading session")
    low_price: float = Field(..., gt=0.0, description="Lowest price during trading session")
    close_price: float = Field(..., gt=0.0, description="Closing price")
    volume: float = Field(..., ge=0.0, description="Daily trading volume")
    daily_return: float = Field(..., description="Daily percentage price return")

    @model_validator(mode="after")
    def validate_ohlc_invariants(self) -> "MarketDataPoint":
        """Validate price invariants: High >= Open/Close/Low and Low <= Open/Close/High."""
        if self.high_price < max(self.open_price, self.close_price, self.low_price):
            raise ValueError(f"High price {self.high_price} is less than max(open, close, low)")
        if self.low_price > min(self.open_price, self.close_price, self.high_price):
            raise ValueError(f"Low price {self.low_price} is greater than min(open, close, high)")
        return self


class SecurityMarketData(BaseModel):
    """Historical market data container for a single security."""

    ticker: str = Field(..., description="Security ticker symbol")
    history: List[MarketDataPoint] = Field(..., description="Daily OHLCV series")
    trading_days_count: int = Field(default=252, description="Total trading days simulated")
