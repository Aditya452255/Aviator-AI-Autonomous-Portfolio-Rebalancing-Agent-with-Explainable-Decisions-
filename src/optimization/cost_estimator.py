"""Cost Estimator calculating brokerage, STT, GST, stamp duty, exchange fees, and market impact."""

from typing import Dict, Optional
from src.core.logger import get_logger
from src.models.trade import TradeAction

logger = get_logger(__name__)


class CostEstimator:
    """Enterprise cost estimator computing transaction fees, taxes, and market impact for trade orders."""

    def __init__(self, execution_rules: Optional[Dict] = None) -> None:
        cfg = execution_rules or {}
        rules = cfg.get("execution_rules", {})
        self.brokerage_rate = rules.get("brokerage_rate", 0.0010)
        self.stt_rate_sell = rules.get("stt_rate_sell", 0.0010)
        self.exchange_rate = rules.get("exchange_charge_rate", 0.00003)
        self.gst_rate = rules.get("gst_rate", 0.18)
        self.stamp_duty_rate_buy = rules.get("stamp_duty_rate_buy", 0.00015)

    def estimate_trade_cost(
        self,
        action: TradeAction,
        market_value: float,
        avg_daily_volume: float = 1e7,
        volatility: float = 0.20,
    ) -> Dict[str, float]:
        """Compute detailed transaction cost breakdown for a single trade order.

        Args:
            action: TradeAction enum (BUY or SELL).
            market_value: Total monetary value of trade.
            avg_daily_volume: Average Daily Volume of security in base currency.
            volatility: Annualized volatility fraction of security.

        Returns:
            Dictionary containing fee breakdown and total cost.
        """
        if market_value <= 0:
            return {"total_cost": 0.0, "brokerage": 0.0, "stt": 0.0, "exchange_fee": 0.0, "gst": 0.0, "stamp_duty": 0.0, "market_impact": 0.0}

        # 1. Brokerage Fee
        brokerage = market_value * self.brokerage_rate

        # 2. STT (Securities Transaction Tax - paid on SELL trades)
        stt = (market_value * self.stt_rate_sell) if action == TradeAction.SELL else 0.0

        # 3. Exchange Turnaround Fee
        exchange_fee = market_value * self.exchange_rate

        # 4. GST (18% on Brokerage + Exchange Fee)
        gst = (brokerage + exchange_fee) * self.gst_rate

        # 5. Stamp Duty (paid on BUY trades)
        stamp_duty = (market_value * self.stamp_duty_rate_buy) if action == TradeAction.BUY else 0.0

        # 6. Market Impact / Slippage: square root law of participation rate
        part_rate = min(1.0, market_value / max(1.0, avg_daily_volume))
        impact_bps = 0.5 * volatility * 10000.0 * float(part_rate ** 0.5)
        market_impact = market_value * (impact_bps / 10000.0)

        total_cost = brokerage + stt + exchange_fee + gst + stamp_duty + market_impact

        return {
            "brokerage": round(brokerage, 2),
            "stt": round(stt, 2),
            "exchange_fee": round(exchange_fee, 2),
            "gst": round(gst, 2),
            "stamp_duty": round(stamp_duty, 2),
            "market_impact": round(market_impact, 2),
            "total_cost": round(total_cost, 2),
        }
