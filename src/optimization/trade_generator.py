"""Trade Generator constructing executable BUY/SELL trade orders from target weights."""

from typing import Dict, List, Optional
from src.core.logger import get_logger
from src.models.portfolio import Portfolio
from src.models.security import Security
from src.models.trade import Trade, TradeAction
from src.optimization.cost_estimator import CostEstimator

logger = get_logger(__name__)


class TradeGenerator:
    """Enterprise trade generator creating clean Trade objects from optimized portfolio weights."""

    def __init__(self, cost_estimator: Optional[CostEstimator] = None) -> None:
        self.cost_estimator = cost_estimator or CostEstimator()

    def generate_trades(
        self,
        portfolio: Portfolio,
        optimized_sec_weights: Dict[str, float],
        securities_map: Optional[Dict[str, Security]] = None,
        min_trade_value: float = 500.0,
    ) -> List[Trade]:
        """Generate Trade objects comparing current portfolio holdings with optimized security weights.

        Args:
            portfolio: Portfolio domain model.
            optimized_sec_weights: Map of ticker to target weight fraction.
            securities_map: Map of ticker to Security objects.
            min_trade_value: Minimum order threshold to suppress tiny dust trades.

        Returns:
            List of validated Trade order objects.
        """
        trades: List[Trade] = []
        trade_idx = 1

        for h in portfolio.holdings:
            ticker = h.ticker
            curr_w = h.current_weight
            tgt_w = optimized_sec_weights.get(ticker, h.target_weight)

            w_change = tgt_w - curr_w
            price = h.current_price

            sec = securities_map.get(ticker) if securities_map else None
            adv = sec.average_daily_volume if sec else 1e7
            vol = sec.volatility if sec else 0.20

            # Absolute trade value
            trade_value = abs(w_change) * portfolio.total_market_value

            if trade_value < min_trade_value:
                continue  # Filter out dust trades

            action = TradeAction.BUY if w_change > 0 else TradeAction.SELL
            shares = round(trade_value / price, 4)

            # Estimate cost
            cost_info = self.cost_estimator.estimate_trade_cost(
                action=action,
                market_value=trade_value,
                avg_daily_volume=adv,
                volatility=vol,
            )

            trade_id = f"TRD_{portfolio.portfolio_id}_{trade_idx:03d}"
            reason = f"Rebalancing {action.value} order ({w_change:+.2%} weight delta)"

            trade = Trade(
                trade_id=trade_id,
                portfolio_id=portfolio.portfolio_id,
                ticker=ticker,
                action=action,
                shares=shares,
                current_weight=round(curr_w, 4),
                target_weight=round(tgt_w, 4),
                weight_change=round(w_change, 4),
                price=round(price, 2),
                market_value=round(trade_value, 2),
                estimated_cost=cost_info["total_cost"],
                tax_impact=0.0,
                reason=reason,
            )
            trades.append(trade)
            trade_idx += 1

        return trades
