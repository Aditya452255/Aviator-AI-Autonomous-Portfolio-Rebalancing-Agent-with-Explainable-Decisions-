"""Generator for Security Master data containing 500 securities across 6 asset classes."""

from typing import List
import numpy as np

from src.core.constants import AssetClass, Country, Currency, Sector
from src.core.logger import get_logger
from src.core.utils import Timer
from src.models.security import Security

logger = get_logger(__name__)


class SecurityMasterGenerator:
    """Enterprise generator producing structured Security Master records."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    def generate_securities(self, num_securities: int = 500) -> List[Security]:
        """Generate a realistic list of financial securities.

        Args:
            num_securities: Total count of securities to generate (default: 500).

        Returns:
            List of validated Security domain model objects.
        """
        with Timer(f"Generating Security Master ({num_securities} securities)"):
            securities: List[Security] = []

            # Asset class distribution ratios
            counts = {
                AssetClass.INDIAN_EQUITY: int(num_securities * 0.35),       # 175
                AssetClass.INTERNATIONAL_EQUITY: int(num_securities * 0.20),# 100
                AssetClass.FIXED_INCOME: int(num_securities * 0.25),        # 125
                AssetClass.REIT: int(num_securities * 0.08),                # 40
                AssetClass.GOLD: int(num_securities * 0.06),                # 30
                AssetClass.CASH_EQUIVALENT: int(num_securities * 0.06),     # 30
            }

            # Adjust remainder if any
            total_allocated = sum(counts.values())
            if total_allocated < num_securities:
                counts[AssetClass.INDIAN_EQUITY] += num_securities - total_allocated

            prefixes = {
                AssetClass.INDIAN_EQUITY: ("INE", "Indian Equity", Currency.INR, Country.INDIA),
                AssetClass.INTERNATIONAL_EQUITY: ("INT", "Global", Currency.USD, Country.USA),
                AssetClass.FIXED_INCOME: ("FIX", "Bond Fund", Currency.INR, Country.INDIA),
                AssetClass.REIT: ("REIT", "Real Estate Trust", Currency.INR, Country.INDIA),
                AssetClass.GOLD: ("GLD", "Gold ETF", Currency.INR, Country.INDIA),
                AssetClass.CASH_EQUIVALENT: ("CSH", "Liquid Cash Fund", Currency.INR, Country.INDIA),
            }

            sectors_equity = [
                Sector.TECHNOLOGY, Sector.FINANCIAL_SERVICES, Sector.HEALTHCARE,
                Sector.CONSUMER_GOODS, Sector.ENERGY, Sector.INDUSTRIALS,
                Sector.UTILITIES, Sector.TELECOMMUNICATIONS,
            ]

            idx = 1
            for asset_class, count in counts.items():
                prefix, base_name, currency, country = prefixes[asset_class]

                for i in range(1, count + 1):
                    ticker = f"{prefix}_{i:03d}"
                    name = f"{base_name} {i}"

                    if asset_class in (AssetClass.INDIAN_EQUITY, AssetClass.INTERNATIONAL_EQUITY):
                        sector = self.rng.choice(sectors_equity)
                        expected_ret = round(self.rng.uniform(0.09, 0.18), 4)
                        volatility = round(self.rng.uniform(0.14, 0.32), 4)
                        liquidity = round(self.rng.uniform(50.0, 98.0), 2)
                        mcap = round(self.rng.uniform(1e9, 5e11), 2)
                        volume = round(self.rng.uniform(1e6, 5e8), 2)
                        init_price = round(self.rng.uniform(50.0, 2500.0), 2)
                    elif asset_class == AssetClass.FIXED_INCOME:
                        sector = Sector.SOVEREIGN if self.rng.rand() > 0.4 else Sector.FINANCIAL_SERVICES
                        expected_ret = round(self.rng.uniform(0.045, 0.085), 4)
                        volatility = round(self.rng.uniform(0.025, 0.075), 4)
                        liquidity = round(self.rng.uniform(60.0, 99.0), 2)
                        mcap = round(self.rng.uniform(5e8, 1e11), 2)
                        volume = round(self.rng.uniform(5e5, 1e8), 2)
                        init_price = round(self.rng.uniform(90.0, 110.0), 2)
                    elif asset_class == AssetClass.REIT:
                        sector = Sector.REAL_ESTATE
                        expected_ret = round(self.rng.uniform(0.07, 0.12), 4)
                        volatility = round(self.rng.uniform(0.10, 0.22), 4)
                        liquidity = round(self.rng.uniform(40.0, 85.0), 2)
                        mcap = round(self.rng.uniform(2e8, 2e10), 2)
                        volume = round(self.rng.uniform(2e5, 5e7), 2)
                        init_price = round(self.rng.uniform(100.0, 600.0), 2)
                    elif asset_class == AssetClass.GOLD:
                        sector = Sector.COMMODITIES if hasattr(Sector, "COMMODITIES") else Sector.CONSUMER_GOODS
                        expected_ret = round(self.rng.uniform(0.06, 0.10), 4)
                        volatility = round(self.rng.uniform(0.11, 0.18), 4)
                        liquidity = round(self.rng.uniform(70.0, 99.0), 2)
                        mcap = round(self.rng.uniform(1e9, 5e10), 2)
                        volume = round(self.rng.uniform(1e6, 2e8), 2)
                        init_price = round(self.rng.uniform(40.0, 150.0), 2)
                    else:  # CASH_EQUIVALENT
                        sector = Sector.CASH
                        expected_ret = round(self.rng.uniform(0.035, 0.055), 4)
                        volatility = round(self.rng.uniform(0.002, 0.010), 4)
                        liquidity = round(self.rng.uniform(90.0, 100.0), 2)
                        mcap = round(self.rng.uniform(1e9, 1e11), 2)
                        volume = round(self.rng.uniform(1e7, 1e9), 2)
                        init_price = round(100.0, 2)

                    sec = Security(
                        ticker=ticker,
                        name=name,
                        asset_class=asset_class,
                        sector=sector,
                        country=country,
                        currency=currency,
                        expected_return=expected_ret,
                        volatility=volatility,
                        average_daily_volume=volume,
                        liquidity_score=liquidity,
                        market_cap=mcap,
                        initial_price=init_price,
                    )
                    securities.append(sec)
                    idx += 1

            logger.info(f"Successfully generated {len(securities)} securities master records.")
            return securities
