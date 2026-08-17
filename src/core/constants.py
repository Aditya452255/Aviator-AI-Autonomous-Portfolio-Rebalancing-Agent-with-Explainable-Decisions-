"""Domain constants, enumerations, and type definitions for Aviator AI."""

from enum import Enum, auto
from typing import Dict, List


class StrEnum(str, Enum):
    """Base string Enum class for clean serialization."""

    def __str__(self) -> str:
        return str(self.value)


class AssetClass(StrEnum):
    """Asset classes supported by the Aviator AI platform."""

    INDIAN_EQUITY = "Indian Equity"
    INTERNATIONAL_EQUITY = "International Equity"
    FIXED_INCOME = "Fixed Income"
    GOLD = "Gold"
    REIT = "REIT"
    CASH_EQUIVALENT = "Cash Equivalent"


class AssetCategory(StrEnum):
    """High-level asset categories for risk allocation matching."""

    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    ALTERNATIVES = "Alternatives"
    CASH = "Cash"


# Mapping from granular AssetClass to top-level AssetCategory
ASSET_CLASS_TO_CATEGORY: Dict[AssetClass, AssetCategory] = {
    AssetClass.INDIAN_EQUITY: AssetCategory.EQUITY,
    AssetClass.INTERNATIONAL_EQUITY: AssetCategory.EQUITY,
    AssetClass.FIXED_INCOME: AssetCategory.FIXED_INCOME,
    AssetClass.GOLD: AssetCategory.ALTERNATIVES,
    AssetClass.REIT: AssetCategory.ALTERNATIVES,
    AssetClass.CASH_EQUIVALENT: AssetCategory.CASH,
}


class RiskCategoryKey(StrEnum):
    """Risk category unique identifiers."""

    ULTRA_CONSERVATIVE = "ultra_conservative"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ULTRA_AGGRESSIVE = "ultra_aggressive"


class RiskCategoryName(StrEnum):
    """Human-readable risk category names."""

    ULTRA_CONSERVATIVE = "Ultra Conservative"
    CONSERVATIVE = "Conservative"
    BALANCED = "Balanced"
    AGGRESSIVE = "Aggressive"
    ULTRA_AGGRESSIVE = "Ultra Aggressive"


class Currency(StrEnum):
    """Supported currencies."""

    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class TaxBracket(StrEnum):
    """Client tax bracket categories."""

    SLAB_0 = "0%"
    SLAB_10 = "10%"
    SLAB_20 = "20%"
    SLAB_30 = "30%"
    SLAB_35 = "35%+"


class ESGPreference(StrEnum):
    """ESG preference levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    STRICT = "Strict"


class Country(StrEnum):
    """Supported client and security countries."""

    INDIA = "India"
    USA = "USA"
    UK = "UK"
    GERMANY = "Germany"
    SINGAPORE = "Singapore"
    UAE = "UAE"


class Sector(StrEnum):
    """Broad economic sectors."""

    TECHNOLOGY = "Technology"
    FINANCIAL_SERVICES = "Financial Services"
    HEALTHCARE = "Healthcare"
    CONSUMER_GOODS = "Consumer Goods"
    ENERGY = "Energy"
    INDUSTRIALS = "Industrials"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"
    TELECOMMUNICATIONS = "Telecommunications"
    SOVEREIGN = "Sovereign"
    CASH = "Cash & Equivalents"
