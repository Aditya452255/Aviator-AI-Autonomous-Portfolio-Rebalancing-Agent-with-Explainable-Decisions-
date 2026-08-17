"""Master orchestrator service for the Aviator AI Enterprise Foundation & Simulation Layer."""

from typing import Dict, List, Tuple
import pandas as pd

from src.core.config import AppConfig, load_config
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.core.utils import Timer, set_random_seed
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.market_data_simulator import MarketDataSimulator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.client import ClientProfile
from src.models.portfolio import Portfolio
from src.models.risk_category import RiskCategory
from src.models.security import Security
from src.services.storage_service import StorageService

logger = get_logger(__name__)


class SimulationService:
    """Master service executing end-to-end synthetic financial simulation and dataset validation."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        set_random_seed(self.config.app.random_seed)

        # Map RiskCategory objects
        self.risk_categories: Dict[str, RiskCategory] = {}
        for key, item in self.config.risk_categories.items():
            rc = RiskCategory(
                id=item.id,
                name=item.name,
                target_equity=item.target_equity,
                target_fixed_income=item.target_fixed_income,
                target_alternatives=item.target_alternatives,
                target_cash=item.target_cash,
                drift_threshold=item.drift_threshold,
            )
            self.risk_categories[key] = rc

        self.storage_service = StorageService(
            output_dir=self.config.storage.output_dir,
            save_csv=self.config.storage.save_csv,
        )

    def run_simulation(
        self,
    ) -> Tuple[List[Security], List[ClientProfile], List[Portfolio], pd.DataFrame]:
        """Execute complete simulation workflow: generate securities, clients, portfolios, market data, validate, and save.

        Returns:
            Tuple of (securities, clients, portfolios, market_data_df).
        """
        with Timer("Full Aviator AI Simulation Execution"):
            logger.info("Initializing Aviator AI Portfolio Simulation Layer...")

            # 1. Generate Securities Master
            sec_gen = SecurityMasterGenerator(seed=self.config.app.random_seed)
            securities = sec_gen.generate_securities(num_securities=self.config.simulation.num_securities)

            # 2. Generate Client Profiles
            client_gen = ClientProfileGenerator(seed=self.config.app.random_seed)
            clients = client_gen.generate_clients(
                num_clients=self.config.simulation.num_clients,
                securities=securities,
            )

            # 3. Generate Portfolios
            port_gen = PortfolioGenerator(
                risk_categories=self.risk_categories,
                seed=self.config.app.random_seed,
            )
            portfolios = port_gen.generate_portfolios(clients=clients, securities=securities)

            # 4. Generate Market Data
            mkt_sim = MarketDataSimulator(seed=self.config.app.random_seed)
            _, df_market = mkt_sim.simulate_market(
                securities=securities,
                trading_days=self.config.simulation.trading_days,
                start_date_str=self.config.simulation.start_date,
            )

            # 5. Enterprise Data Validation
            self.validate_datasets(securities=securities, clients=clients, portfolios=portfolios, df_market=df_market)

            # 6. Save Generated Datasets
            self.storage_service.save_securities(securities)
            self.storage_service.save_clients(clients)
            self.storage_service.save_portfolios(portfolios)
            self.storage_service.save_market_data(df_market)

            logger.info("Simulation successfully completed and validated!")
            return securities, clients, portfolios, df_market

    def validate_datasets(
        self,
        securities: List[Security],
        clients: List[ClientProfile],
        portfolios: List[Portfolio],
        df_market: pd.DataFrame,
    ) -> bool:
        """Validate integrity and domain invariants across generated datasets.

        Raises:
            ValidationError: If any constraint check fails.
        """
        with Timer("Dataset Integrity Validation"):
            logger.info("Executing enterprise data validation checks...")

            # Check 1: Security Ticker Uniqueness & Valid Parameters
            valid_tickers = {s.ticker for s in securities}
            if len(valid_tickers) != len(securities):
                raise ValidationError("Duplicate ticker symbols found in Security Master.")

            for s in securities:
                if s.initial_price <= 0:
                    raise ValidationError(f"Security {s.ticker} has non-positive initial price {s.initial_price}")

            # Check 2: Client ID Uniqueness
            valid_client_ids = {c.client_id for c in clients}
            if len(valid_client_ids) != len(clients):
                raise ValidationError("Duplicate client IDs found in Client Profiles.")

            # Check 3: Portfolio Ownership & Security Existence
            valid_portfolio_ids = set()
            for p in portfolios:
                if p.portfolio_id in valid_portfolio_ids:
                    raise ValidationError(f"Duplicate portfolio ID found: {p.portfolio_id}")
                valid_portfolio_ids.add(p.portfolio_id)

                if p.client_id not in valid_client_ids:
                    raise ValidationError(f"Portfolio {p.portfolio_id} references invalid client ID: {p.client_id}")

                if p.total_market_value <= 0:
                    raise ValidationError(f"Portfolio {p.portfolio_id} has non-positive market value: {p.total_market_value}")

                # Verify 15-40 securities constraint
                if not (15 <= p.num_securities <= 40):
                    raise ValidationError(f"Portfolio {p.portfolio_id} has {p.num_securities} securities, outside valid range [15, 40]")

                # Check security holdings
                sec_target_sum = 0.0
                sec_curr_sum = 0.0
                for h in p.holdings:
                    if h.ticker not in valid_tickers:
                        raise ValidationError(f"Portfolio {p.portfolio_id} contains unknown ticker: {h.ticker}")
                    if h.market_value < 0 or h.current_price <= 0:
                        raise ValidationError(f"Portfolio {p.portfolio_id} holding {h.ticker} has invalid pricing/value")
                    sec_target_sum += h.target_weight
                    sec_curr_sum += h.current_weight

                # Verify target weight sums equal 1.0 within tolerance
                if not (0.99 <= sec_target_sum <= 1.01):
                    raise ValidationError(f"Portfolio {p.portfolio_id} target holding weights sum to {sec_target_sum:.4f}, expected ~1.0")

                if not (0.99 <= sec_curr_sum <= 1.01):
                    raise ValidationError(f"Portfolio {p.portfolio_id} current holding weights sum to {sec_curr_sum:.4f}, expected ~1.0")

            # Check 4: Market Data Invariants
            if df_market.empty:
                raise ValidationError("Simulated market data DataFrame is empty.")

            invalid_high = df_market[df_market["high"] < df_market[["open", "close", "low"]].max(axis=1)]
            if not invalid_high.empty:
                raise ValidationError(f"Found {len(invalid_high)} market records violating High price invariant.")

            invalid_low = df_market[df_market["low"] > df_market[["open", "close", "high"]].min(axis=1)]
            if not invalid_low.empty:
                raise ValidationError(f"Found {len(invalid_low)} market records violating Low price invariant.")

            logger.info("All dataset validation checks PASSED successfully.")
            return True
