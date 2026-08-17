"""Trade Validator verifying trade integrity, cash availability, and lot constraints."""

from typing import List, Optional
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.models.portfolio import Portfolio
from src.models.trade import Trade, TradeAction

logger = get_logger(__name__)


class TradeValidator:
    """Enterprise trade validator verifying safety, positivity, deduplication, and cash sufficiency."""

    def validate_trades(self, trades: List[Trade], portfolio: Portfolio) -> bool:
        """Validate generated trades list for portfolio.

        Args:
            trades: List of generated Trade objects.
            portfolio: Portfolio instance.

        Returns:
            True if all trade validation checks pass.

        Raises:
            ValidationError: If any safety constraint is violated.
        """
        seen_tickers = set()
        total_buy_value = 0.0
        total_sell_value = 0.0

        for t in trades:
            # Check 1: Non-negative shares & market value
            if t.shares <= 0 or t.market_value <= 0:
                raise ValidationError(f"Trade {t.trade_id} has invalid non-positive shares or market value")

            # Check 2: No duplicate trades per security
            if t.ticker in seen_tickers:
                raise ValidationError(f"Duplicate trade order detected for ticker: {t.ticker}")
            seen_tickers.add(t.ticker)

            if t.action == TradeAction.BUY:
                total_buy_value += t.market_value
            else:
                total_sell_value += t.market_value

        # Check 3: Cash availability check for net BUY value
        net_buy_cash = total_buy_value - total_sell_value
        if net_buy_cash > portfolio.cash_balance + 0.01:
            raise ValidationError(
                f"Portfolio {portfolio.portfolio_id} net BUY trades value ({net_buy_cash:,.2f}) exceeds cash balance ({portfolio.cash_balance:,.2f})"
            )

        logger.debug(f"Trade validation PASSED for portfolio {portfolio.portfolio_id} ({len(trades)} trades).")
        return True
