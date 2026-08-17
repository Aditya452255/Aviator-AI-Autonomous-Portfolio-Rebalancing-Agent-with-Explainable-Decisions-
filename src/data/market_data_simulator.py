"""Market Data Simulator implementing Multivariate Geometric Brownian Motion with correlated returns."""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.core.constants import ASSET_CLASS_TO_CATEGORY, AssetCategory
from src.core.logger import get_logger
from src.core.utils import Timer, ensure_positive_definite
from src.models.market import MarketDataPoint, SecurityMarketData
from src.models.security import Security

logger = get_logger(__name__)


class MarketDataSimulator:
    """Enterprise market simulator producing correlated multi-asset OHLCV historical time series."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    def _build_correlation_matrix(self, securities: List[Security]) -> np.ndarray:
        """Construct realistic multi-asset class correlation matrix.

        Args:
            securities: List of securities.

        Returns:
            (N, N) symmetric positive semi-definite correlation matrix.
        """
        n = len(securities)
        corr = np.eye(n)

        # Map asset categories to integer indices
        cat_indices: Dict[AssetCategory, List[int]] = {cat: [] for cat in AssetCategory}
        for idx, sec in enumerate(securities):
            cat = ASSET_CLASS_TO_CATEGORY[sec.asset_class]
            cat_indices[cat].append(idx)

        # Define category-level baseline correlation matrix
        cat_corr = {
            (AssetCategory.EQUITY, AssetCategory.EQUITY): 0.55,
            (AssetCategory.FIXED_INCOME, AssetCategory.FIXED_INCOME): 0.65,
            (AssetCategory.ALTERNATIVES, AssetCategory.ALTERNATIVES): 0.40,
            (AssetCategory.CASH, AssetCategory.CASH): 0.85,
            (AssetCategory.EQUITY, AssetCategory.FIXED_INCOME): -0.15,
            (AssetCategory.EQUITY, AssetCategory.ALTERNATIVES): 0.20,
            (AssetCategory.EQUITY, AssetCategory.CASH): 0.0,
            (AssetCategory.FIXED_INCOME, AssetCategory.ALTERNATIVES): 0.10,
            (AssetCategory.FIXED_INCOME, AssetCategory.CASH): 0.05,
            (AssetCategory.ALTERNATIVES, AssetCategory.CASH): 0.0,
        }

        for i in range(n):
            cat_i = ASSET_CLASS_TO_CATEGORY[securities[i].asset_class]
            for j in range(i + 1, n):
                cat_j = ASSET_CLASS_TO_CATEGORY[securities[j].asset_class]

                pair = (cat_i, cat_j) if (cat_i, cat_j) in cat_corr else (cat_j, cat_i)
                base_c = cat_corr.get(pair, 0.10)

                # Add noise around baseline correlation
                c_val = base_c + self.rng.uniform(-0.08, 0.08)
                c_val = np.clip(c_val, -0.90, 0.95)

                corr[i, j] = c_val
                corr[j, i] = c_val

        return ensure_positive_definite(corr)

    def simulate_market(
        self,
        securities: List[Security],
        trading_days: int = 252,
        start_date_str: str = "2025-01-01",
    ) -> Tuple[Dict[str, SecurityMarketData], pd.DataFrame]:
        """Simulate 252 trading days of market data using Multivariate Geometric Brownian Motion.

        Args:
            securities: List of Security master objects.
            trading_days: Number of trading days to simulate (default: 252).
            start_date_str: Simulation start date string (YYYY-MM-DD).

        Returns:
            Tuple of (dict mapping ticker to SecurityMarketData, combined pandas DataFrame of all OHLCV).
        """
        with Timer(f"Simulating Market Data ({trading_days} days across {len(securities)} securities)"):
            n_sec = len(securities)
            dt = 1.0 / 252.0  # Daily time step in years

            # Extract vectors
            mu = np.array([s.expected_return for s in securities])
            sigma = np.array([s.volatility for s in securities])
            s0 = np.array([s.initial_price for s in securities])

            # Build correlation and covariance matrix
            corr = self._build_correlation_matrix(securities)
            cov = np.outer(sigma, sigma) * corr
            cov = ensure_positive_definite(cov)

            # Cholesky factor L: Sigma = L * L^T
            L = np.linalg.cholesky(cov)

            # Generate independent standard normal random variables (n_sec, trading_days)
            Z = self.rng.normal(size=(n_sec, trading_days))

            # Correlated random shocks: dW = L * Z
            dW = np.dot(L, Z)

            # Multivariate Geometric Brownian Motion daily log returns:
            # d_ln_S = (mu - 0.5 * sigma^2) * dt + dW * sqrt(dt)
            drift = (mu - 0.5 * (sigma ** 2))[:, np.newaxis] * dt
            diffusion = dW * np.sqrt(dt)
            daily_log_returns = drift + diffusion

            # Inject market jump events (3 market-wide shock days)
            shock_days = self.rng.choice(trading_days, size=3, replace=False)
            for s_day in shock_days:
                # Market shock (-3% to +2.5%)
                shock_val = self.rng.uniform(-0.035, 0.025)
                daily_log_returns[:, s_day] += shock_val

            # Compute price path matrix (n_sec, trading_days)
            cum_log_returns = np.cumsum(daily_log_returns, axis=1)
            prices_close = s0[:, np.newaxis] * np.exp(cum_log_returns)

            # Build dates list excluding weekends
            dates: List[str] = []
            curr = datetime.strptime(start_date_str, "%Y-%m-%d")
            while len(dates) < trading_days:
                if curr.weekday() < 5:  # Mon-Fri
                    dates.append(curr.strftime("%Y-%m-%d"))
                curr += timedelta(days=1)

            # Build detailed market data
            market_dict: Dict[str, SecurityMarketData] = {}
            df_rows: List[dict] = []

            for i, sec in enumerate(securities):
                history: List[MarketDataPoint] = []
                p_close_series = prices_close[i, :]

                for t in range(trading_days):
                    close_p = float(p_close_series[t])
                    open_p = float(s0[i]) if t == 0 else float(p_close_series[t - 1])

                    # Intraday High/Low generation
                    max_op_cl = max(open_p, close_p)
                    min_op_cl = min(open_p, close_p)

                    intra_std = max(0.001, sec.volatility * np.sqrt(dt) * 0.5)
                    high_spread = abs(self.rng.normal(0, intra_std)) * max_op_cl
                    low_spread = abs(self.rng.normal(0, intra_std)) * min_op_cl

                    high_p = round(max_op_cl + high_spread + 0.01, 2)
                    low_p = round(max(0.01, min_op_cl - low_spread - 0.01), 2)
                    open_p = round(open_p, 2)
                    close_p = round(close_p, 2)

                    # Invariant enforcement
                    high_p = max(high_p, open_p, close_p)
                    low_p = min(low_p, open_p, close_p)

                    daily_ret = 0.0 if t == 0 else float((close_p - open_p) / open_p)

                    vol_mult = self.rng.lognormal(0.0, 0.25)
                    vol = round(float(sec.average_daily_volume * vol_mult), 2)

                    dp = MarketDataPoint(
                        ticker=sec.ticker,
                        date=dates[t],
                        trading_day=t,
                        open_price=open_p,
                        high_price=high_p,
                        low_price=low_p,
                        close_price=close_p,
                        volume=vol,
                        daily_return=round(daily_ret, 6),
                    )
                    history.append(dp)

                    df_rows.append({
                        "ticker": sec.ticker,
                        "date": dates[t],
                        "trading_day": t,
                        "open": open_p,
                        "high": high_p,
                        "low": low_p,
                        "close": close_p,
                        "volume": vol,
                        "daily_return": round(daily_ret, 6),
                    })

                market_dict[sec.ticker] = SecurityMarketData(
                    ticker=sec.ticker,
                    history=history,
                    trading_days_count=trading_days,
                )

            df_combined = pd.DataFrame(df_rows)
            logger.info(f"Successfully simulated {trading_days} days of market data ({len(df_rows)} rows).")
            return market_dict, df_combined
