"""Historical Replay Engine replaying price series over daily, monthly, quarterly, and rolling windows."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.core.logger import get_logger

logger = get_logger(__name__)


class HistoricalReplayEngine:
    """Enterprise Historical Replay Engine managing price series stepping."""

    def get_replay_schedules(self, trading_days: int = 252, frequency: str = "DAILY") -> List[int]:
        """Get stepping day indices for specified replay frequency.

        Args:
            trading_days: Total trading days in historical dataset.
            frequency: DAILY, MONTHLY, QUARTERLY, ANNUAL, or ROLLING_WINDOW.

        Returns:
            List of 1-indexed trading day numbers when rebalance checks occur.
        """
        freq_upper = frequency.upper()
        if freq_upper == "DAILY":
            return list(range(1, trading_days + 1))
        elif freq_upper == "MONTHLY":
            return list(range(21, trading_days + 1, 21))
        elif freq_upper == "QUARTERLY":
            return list(range(63, trading_days + 1, 63))
        elif freq_upper == "ANNUAL":
            return [trading_days]
        elif freq_upper == "ROLLING_WINDOW":
            return list(range(10, trading_days + 1, 10))
        else:
            return list(range(63, trading_days + 1, 63))

    def slice_market_history(self, df_market: pd.DataFrame, end_day: int) -> pd.DataFrame:
        """Slice market dataset up to specific historical trading day.

        Args:
            df_market: Market data DataFrame.
            end_day: Day index boundary.

        Returns:
            Sliced DataFrame.
        """
        if "day" in df_market.columns:
            return df_market[df_market["day"] <= end_day]
        return df_market
