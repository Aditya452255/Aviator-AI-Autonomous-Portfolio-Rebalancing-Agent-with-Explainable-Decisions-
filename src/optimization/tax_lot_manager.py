"""Tax Lot Manager tracking historical purchase lots and matching sales for tax efficiency."""

import random
from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.models.portfolio import Portfolio
from src.models.tax_lot import TaxLot

logger = get_logger(__name__)


class TaxLotManager:
    """Enterprise tax lot manager tracking tax purchase lots per portfolio and security."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_synthetic_tax_lots(self, portfolio: Portfolio) -> Dict[str, List[TaxLot]]:
        """Generate synthetic purchase tax lots for all holdings in a portfolio.

        Args:
            portfolio: Portfolio instance.

        Returns:
            Dictionary mapping ticker to list of TaxLot objects.
        """
        lots_by_ticker: Dict[str, List[TaxLot]] = {}

        for h in portfolio.holdings:
            # Create 1 to 4 lots per holding
            num_lots = self.rng.randint(1, 4)
            shares_per_lot = h.shares / num_lots

            ticker_lots: List[TaxLot] = []
            for i in range(num_lots):
                lot_id = f"LOT_{portfolio.portfolio_id}_{h.ticker}_{i+1}"

                # Vary holding days: 50% chance of LTCG (>365 days)
                holding_days = self.rng.randint(30, 800)
                is_lt = holding_days > 365

                # Cost basis variance per lot (-15% to +20%)
                cb_factor = 1.0 + self.rng.uniform(-0.15, 0.20)
                cost_basis_per_share = h.current_price / cb_factor

                unrealized_pnl = (h.current_price - cost_basis_per_share) * shares_per_lot

                lot = TaxLot(
                    lot_id=lot_id,
                    portfolio_id=portfolio.portfolio_id,
                    ticker=h.ticker,
                    purchase_date=f"2023-01-{self.rng.randint(1, 28):02d}",
                    cost_basis_per_share=round(cost_basis_per_share, 2),
                    shares=round(shares_per_lot, 4),
                    holding_days=holding_days,
                    is_long_term=is_lt,
                    current_price=round(h.current_price, 2),
                    unrealized_gain_loss=round(unrealized_pnl, 2),
                )
                ticker_lots.append(lot)

            lots_by_ticker[h.ticker] = ticker_lots

        return lots_by_ticker

    def select_lots_to_sell(
        self,
        lots: List[TaxLot],
        shares_to_sell: float,
        strategy: str = "tax_efficient",
    ) -> List[Tuple_Lot_Shares if False else tuple[TaxLot, float]]:
        """Select specific tax lots to sell according to specified strategy.

        Args:
            lots: Available TaxLot list for the security.
            shares_to_sell: Target quantity of shares to liquidate.
            strategy: Matching strategy ('tax_efficient', 'hifo', 'fifo', 'lifo').

        Returns:
            List of tuples: (TaxLot, shares_sold_from_this_lot).
        """
        if not lots or shares_to_sell <= 0:
            return []

        # Sort lots according to strategy
        if strategy == "hifo":  # Highest Cost Basis First (maximizes loss / minimizes gain)
            sorted_lots = sorted(lots, key=lambda l: l.cost_basis_per_share, reverse=True)
        elif strategy == "fifo":  # First In First Out (oldest first)
            sorted_lots = sorted(lots, key=lambda l: l.holding_days, reverse=True)
        elif strategy == "lifo":  # Last In First Out (newest first)
            sorted_lots = sorted(lots, key=lambda l: l.holding_days, reverse=False)
        else:  # "tax_efficient": Losses first, then LTCG gains, then STCG gains
            sorted_lots = sorted(
                lots,
                key=lambda l: (
                    0 if l.unrealized_gain_loss < 0 else 1,  # Losses first
                    0 if l.is_long_term else 1,              # LTCG before STCG
                    -l.cost_basis_per_share                  # Highest cost basis
                )
            )

        selected: List[tuple[TaxLot, float]] = []
        remaining = shares_to_sell

        for lot in sorted_lots:
            if remaining <= 0:
                break
            sold_qty = min(lot.shares, remaining)
            selected.append((lot, sold_qty))
            remaining -= sold_qty

        return selected
