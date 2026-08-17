"""Generator for 50,000 client portfolios conforming to target risk categories."""

from typing import Dict, List
import numpy as np

from src.core.constants import ASSET_CLASS_TO_CATEGORY, AssetCategory, RiskCategoryKey
from src.core.exceptions import PortfolioAllocationError
from src.core.logger import get_logger
from src.core.utils import Timer
from src.models.allocation import SecurityHolding
from src.models.client import ClientProfile
from src.models.portfolio import Portfolio
from src.models.risk_category import RiskCategory
from src.models.security import Security

logger = get_logger(__name__)


class PortfolioGenerator:
    """Enterprise generator constructing realistic portfolios matching client profiles and risk allocations."""

    def __init__(self, risk_categories: Dict[str, RiskCategory], seed: int = 42) -> None:
        self.risk_categories = risk_categories
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    def generate_portfolios(
        self,
        clients: List[ClientProfile],
        securities: List[Security],
    ) -> List[Portfolio]:
        """Generate 50,000 portfolios for given clients and security master.

        Args:
            clients: List of ClientProfile instances.
            securities: List of Security instances.

        Returns:
            List of validated Portfolio instances.
        """
        with Timer(f"Generating Portfolios ({len(clients)} portfolios)"):
            if not clients:
                raise PortfolioAllocationError("Cannot generate portfolios: client list is empty.")
            if not securities:
                raise PortfolioAllocationError("Cannot generate portfolios: security master is empty.")

            # Categorize securities by asset category
            secs_by_cat: Dict[AssetCategory, List[Security]] = {cat: [] for cat in AssetCategory}
            sec_lookup: Dict[str, Security] = {}
            for sec in securities:
                sec_lookup[sec.ticker] = sec
                cat = ASSET_CLASS_TO_CATEGORY[sec.asset_class]
                secs_by_cat[cat].append(sec)

            portfolios: List[Portfolio] = []

            for i, client in enumerate(clients):
                portfolio_id = f"PORT_{i + 1:05d}"

                # Look up target risk category profile
                risk_key = client.risk_category.value if isinstance(client.risk_category, RiskCategoryKey) else client.risk_category
                if risk_key not in self.risk_categories:
                    raise PortfolioAllocationError(f"Unknown risk category '{risk_key}' for client {client.client_id}")

                risk_prof = self.risk_categories[risk_key]

                target_cat_weights = {
                    AssetCategory.EQUITY: risk_prof.target_equity,
                    AssetCategory.FIXED_INCOME: risk_prof.target_fixed_income,
                    AssetCategory.ALTERNATIVES: risk_prof.target_alternatives,
                    AssetCategory.CASH: risk_prof.target_cash,
                }

                # Determine number of securities to hold (15 to 40)
                num_secs = self.rng.randint(15, 41)

                # Filter out client restricted securities
                restricted_set = set(client.restricted_securities)

                # Select securities per category based on target weights
                selected_secs: List[Security] = []

                for cat, cat_weight in target_cat_weights.items():
                    available = [s for s in secs_by_cat[cat] if s.ticker not in restricted_set]
                    if not available:
                        available = secs_by_cat[cat]  # Fallback if all restricted

                    if cat_weight > 0:
                        # Determine proportion of securities for this category
                        cat_num_secs = max(1, int(round(num_secs * cat_weight)))
                        cat_num_secs = min(cat_num_secs, len(available))

                        chosen = list(self.rng.choice(available, size=cat_num_secs, replace=False))
                        selected_secs.extend(chosen)

                # Ensure exact count within [15, 40]
                selected_secs = list({s.ticker: s for s in selected_secs}.values())  # Deduplicate

                while len(selected_secs) < 15:
                    available = [s for s in securities if s.ticker not in restricted_set and s not in selected_secs]
                    if not available:
                        break
                    selected_secs.append(self.rng.choice(available))

                if len(selected_secs) > 40:
                    selected_secs = selected_secs[:40]

                actual_num_secs = len(selected_secs)
                total_portfolio_value = client.portfolio_size

                # Assign target weights to securities within their category
                sec_target_weights: Dict[str, float] = {}
                cat_sec_groups: Dict[AssetCategory, List[Security]] = {cat: [] for cat in AssetCategory}
                for s in selected_secs:
                    cat_sec_groups[ASSET_CLASS_TO_CATEGORY[s.asset_class]].append(s)

                for cat, group in cat_sec_groups.items():
                    if not group:
                        continue
                    cat_weight = target_cat_weights[cat]
                    # Randomize weight allocation within category
                    raw_weights = self.rng.dirichlet(np.ones(len(group)))
                    for s, w in zip(group, raw_weights):
                        sec_target_weights[s.ticker] = w * cat_weight

                # Normalize target weights to sum to 1.0
                total_target_w = sum(sec_target_weights.values())
                sec_target_weights = {k: v / total_target_w for k, v in sec_target_weights.items()}

                # Simulate market drift to get current weights
                # Add mild noise ~ Normal(0, 0.02) to create current weights
                raw_current_w: Dict[str, float] = {}
                for ticker, tw in sec_target_weights.items():
                    drift = self.rng.normal(0.0, 0.02)
                    raw_current_w[ticker] = max(0.001, tw + drift)

                total_curr_w = sum(raw_current_w.values())
                sec_current_weights = {k: v / total_curr_w for k, v in raw_current_w.items()}

                # Construct holdings
                holdings: List[SecurityHolding] = []
                total_sec_market_val = 0.0
                total_cost_basis = 0.0

                for sec in selected_secs:
                    t_weight = sec_target_weights[sec.ticker]
                    c_weight = sec_current_weights[sec.ticker]

                    sec_mv = total_portfolio_value * c_weight
                    price = sec.initial_price
                    shares = sec_mv / price

                    # Cost basis with mild historical PnL variance (-10% to +15%)
                    pnl_factor = 1.0 + self.rng.uniform(-0.10, 0.15)
                    cost_basis = sec_mv / pnl_factor
                    unrealized_pnl = sec_mv - cost_basis

                    holding = SecurityHolding(
                        ticker=sec.ticker,
                        asset_class=sec.asset_class.value,
                        asset_category=ASSET_CLASS_TO_CATEGORY[sec.asset_class].value,
                        target_weight=round(float(t_weight), 6),
                        current_weight=round(float(c_weight), 6),
                        shares=round(float(shares), 4),
                        current_price=round(float(price), 2),
                        market_value=round(float(sec_mv), 2),
                        cost_basis=round(float(cost_basis), 2),
                        unrealized_pnl=round(float(unrealized_pnl), 2),
                    )
                    holdings.append(holding)
                    total_sec_market_val += sec_mv
                    total_cost_basis += cost_basis

                # Calculate category level current and target weights
                current_cat_weights: Dict[str, float] = {cat.value: 0.0 for cat in AssetCategory}
                target_cat_weights_formatted: Dict[str, float] = {cat.value: round(target_cat_weights[cat], 4) for cat in AssetCategory}

                for h in holdings:
                    current_cat_weights[h.asset_category] += h.current_weight

                for k in current_cat_weights:
                    current_cat_weights[k] = round(current_cat_weights[k], 4)

                # Cash balance is uninvested cash portion
                cash_balance = round(float(total_portfolio_value * target_cat_weights[AssetCategory.CASH]), 2)

                port = Portfolio(
                    portfolio_id=portfolio_id,
                    client_id=client.client_id,
                    risk_category=client.risk_category,
                    cash_balance=cash_balance,
                    total_market_value=round(float(total_portfolio_value), 2),
                    total_cost_basis=round(float(total_cost_basis), 2),
                    holdings=holdings,
                    current_weights=current_cat_weights,
                    target_weights=target_cat_weights_formatted,
                    num_securities=actual_num_secs,
                )
                portfolios.append(port)

            logger.info(f"Successfully generated {len(portfolios)} client portfolios.")
            return portfolios
