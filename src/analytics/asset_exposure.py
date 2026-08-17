"""Asset Exposure Analytics aggregating asset category allocations and cash reserves."""

from typing import Dict, List
import pandas as pd

from src.core.constants import AssetCategory
from src.core.logger import get_logger
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class AssetExposureAnalyzer:
    """Enterprise asset allocation exposure analytics engine."""

    def compute_asset_exposure(self, portfolios: List[Portfolio]) -> pd.DataFrame:
        """Compute aggregate asset category weights and total market values.

        Args:
            portfolios: List of Portfolio objects.

        Returns:
            DataFrame containing Asset Category, Total Value, and Weight Percentage.
        """
        cat_values: Dict[str, float] = {cat.value: 0.0 for cat in AssetCategory}
        total_universe_val = 0.0

        for p in portfolios:
            total_universe_val += p.total_market_value
            for cat in AssetCategory:
                w = p.current_weights.get(cat.value, 0.0)
                cat_values[cat.value] += p.total_market_value * w

        rows = []
        for cat_name, val in cat_values.items():
            pct = (val / total_universe_val * 100.0) if total_universe_val > 0 else 0.0
            rows.append({
                "asset_category": cat_name,
                "total_market_value": round(val, 2),
                "exposure_pct": round(pct, 2),
            })

        return pd.DataFrame(rows)
