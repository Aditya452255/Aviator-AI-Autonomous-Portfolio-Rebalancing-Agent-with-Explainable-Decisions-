"""Tax Optimizer calculating realized capital gains, STCG vs LTCG tax liability, and tax loss harvesting."""

from typing import Dict, List, Optional, Tuple
from src.core.logger import get_logger
from src.models.tax_lot import TaxLot
from src.models.trade import Trade, TradeAction
from src.optimization.tax_lot_manager import TaxLotManager

logger = get_logger(__name__)


class TaxOptimizer:
    """Enterprise tax optimizer evaluating tax impact, STCG/LTCG splits, and loss harvesting opportunities."""

    def __init__(self, tax_rules: Optional[Dict] = None) -> None:
        cfg = tax_rules or {}
        rules = cfg.get("tax_rules", {})
        self.stcg_rate = rules.get("stcg_rate", 0.20)
        self.ltcg_rate = rules.get("ltcg_rate", 0.125)
        self.strategy = rules.get("lot_selection_strategy", "tax_efficient")
        self.tax_lot_manager = TaxLotManager()

    def evaluate_trade_tax_impact(
        self,
        trade: Trade,
        lots: List[TaxLot],
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate estimated tax liability or tax savings for a trade order.

        Args:
            trade: Trade order instance.
            lots: Available TaxLot list for the target security.

        Returns:
            Tuple of (tax_impact_amount, tax_breakdown_dict).
        """
        if trade.action == TradeAction.BUY or not lots:
            return 0.0, {
                "realized_stcg": 0.0,
                "realized_ltcg": 0.0,
                "stcg_tax": 0.0,
                "ltcg_tax": 0.0,
                "harvested_loss": 0.0,
                "net_tax_impact": 0.0,
            }

        selected_lots = self.tax_lot_manager.select_lots_to_sell(
            lots=lots,
            shares_to_sell=trade.shares,
            strategy=self.strategy,
        )

        realized_stcg = 0.0
        realized_ltcg = 0.0
        harvested_loss = 0.0

        for lot, shares_sold in selected_lots:
            gain_per_share = trade.price - lot.cost_basis_per_share
            total_gain = gain_per_share * shares_sold

            if total_gain < 0:
                harvested_loss += abs(total_gain)
            elif lot.is_long_term:
                realized_ltcg += total_gain
            else:
                realized_stcg += total_gain

        stcg_tax = realized_stcg * self.stcg_rate
        ltcg_tax = realized_ltcg * self.ltcg_rate

        # Tax savings from loss harvesting
        tax_saved = harvested_loss * self.stcg_rate
        net_tax_impact = (stcg_tax + ltcg_tax) - tax_saved

        breakdown = {
            "realized_stcg": round(realized_stcg, 2),
            "realized_ltcg": round(realized_ltcg, 2),
            "stcg_tax": round(stcg_tax, 2),
            "ltcg_tax": round(ltcg_tax, 2),
            "harvested_loss": round(harvested_loss, 2),
            "tax_saved_from_harvesting": round(tax_saved, 2),
            "net_tax_impact": round(net_tax_impact, 2),
        }

        return round(net_tax_impact, 2), breakdown
