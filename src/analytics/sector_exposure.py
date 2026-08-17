"""Sector Exposure Analytics aggregating economic sector weights across the portfolio universe."""

from typing import Dict, List
import pandas as pd

from src.core.logger import get_logger
from src.models.portfolio import Portfolio

logger = get_logger(__name__)


class SectorExposureAnalyzer:
    """Enterprise sector exposure analytics engine."""

    def compute_sector_exposure(self, portfolios: List[Portfolio]) -> pd.DataFrame:
        """Compute aggregate sector exposure percentages across all portfolios.

        Args:
            portfolios: List of Portfolio objects.

        Returns:
            DataFrame containing sector name, total market value, and percentage of universe.
        """
        sector_values: Dict[str, float] = {}
        total_universe_value = 0.0

        for p in portfolios:
            total_universe_value += p.total_market_value
            for h in p.holdings:
                sec_name = getattr(h, "sector", h.asset_category)
                sector_values[sec_name] = sector_values.get(sec_name, 0.0) + h.market_value

        rows = []
        for s_name, val in sector_values.items():
            pct = (val / total_universe_value * 100.0) if total_universe_value > 0 else 0.0
            rows.append({
                "sector": s_name,
                "total_market_value": round(val, 2),
                "exposure_pct": round(pct, 2),
            })

        df = pd.DataFrame(rows)
        return df.sort_values(by="total_market_value", ascending=False).reset_index(drop=True)
