"""Data persistence and loading service supporting Parquet and CSV output formats."""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd

from src.core.exceptions import StorageError
from src.core.logger import get_logger
from src.core.utils import Timer
from src.models.client import ClientProfile
from src.models.portfolio import Portfolio
from src.models.security import Security

logger = get_logger(__name__)


class StorageService:
    """Enterprise storage service handling dataset serialization and file IO."""

    def __init__(self, output_dir: str = "data/output", save_csv: bool = True) -> None:
        self.output_dir = Path(output_dir)
        self.save_csv = save_csv
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_securities(self, securities: List[Security]) -> Path:
        """Save Security Master list to Parquet and CSV.

        Args:
            securities: List of Security instances.

        Returns:
            Path to saved Parquet file.
        """
        with Timer("Saving Securities Master"):
            try:
                data = [s.model_dump() for s in securities]
                df = pd.DataFrame(data)

                pq_path = self.output_dir / "securities_master.parquet"
                df.to_parquet(pq_path, index=False)

                if self.save_csv:
                    csv_path = self.output_dir / "securities_master.csv"
                    df.to_csv(csv_path, index=False)

                logger.info(f"Saved {len(securities)} securities master records to {pq_path}")
                return pq_path
            except Exception as e:
                raise StorageError(f"Failed to save securities master: {e}") from e

    def save_clients(self, clients: List[ClientProfile]) -> Path:
        """Save Client Profiles list to Parquet and CSV.

        Args:
            clients: List of ClientProfile instances.

        Returns:
            Path to saved Parquet file.
        """
        with Timer("Saving Client Profiles"):
            try:
                data = []
                for c in clients:
                    cdict = c.model_dump()
                    cdict["restricted_securities"] = ",".join(cdict["restricted_securities"])
                    data.append(cdict)

                df = pd.DataFrame(data)

                pq_path = self.output_dir / "client_profiles.parquet"
                df.to_parquet(pq_path, index=False)

                if self.save_csv:
                    csv_path = self.output_dir / "client_profiles.csv"
                    df.to_csv(csv_path, index=False)

                logger.info(f"Saved {len(clients)} client profiles to {pq_path}")
                return pq_path
            except Exception as e:
                raise StorageError(f"Failed to save client profiles: {e}") from e

    def save_portfolios(self, portfolios: List[Portfolio]) -> Tuple[Path, Path]:
        """Save Portfolios summary and granular Holdings to Parquet and CSV.

        Args:
            portfolios: List of Portfolio instances.

        Returns:
            Tuple of (portfolios_summary_path, holdings_path).
        """
        with Timer("Saving Portfolios & Holdings"):
            try:
                p_summary_rows = []
                holding_rows = []

                for p in portfolios:
                    p_summary_rows.append({
                        "portfolio_id": p.portfolio_id,
                        "client_id": p.client_id,
                        "risk_category": p.risk_category.value if hasattr(p.risk_category, "value") else str(p.risk_category),
                        "cash_balance": p.cash_balance,
                        "total_market_value": p.total_market_value,
                        "total_cost_basis": p.total_cost_basis,
                        "num_securities": p.num_securities,
                        "current_weights_json": json.dumps(p.current_weights),
                        "target_weights_json": json.dumps(p.target_weights),
                    })

                    for h in p.holdings:
                        holding_rows.append({
                            "portfolio_id": p.portfolio_id,
                            "client_id": p.client_id,
                            "ticker": h.ticker,
                            "asset_class": h.asset_class,
                            "asset_category": h.asset_category,
                            "target_weight": h.target_weight,
                            "current_weight": h.current_weight,
                            "shares": h.shares,
                            "current_price": h.current_price,
                            "market_value": h.market_value,
                            "cost_basis": h.cost_basis,
                            "unrealized_pnl": h.unrealized_pnl,
                        })

                df_p = pd.DataFrame(p_summary_rows)
                df_h = pd.DataFrame(holding_rows)

                p_pq = self.output_dir / "portfolios.parquet"
                h_pq = self.output_dir / "portfolio_holdings.parquet"

                df_p.to_parquet(p_pq, index=False)
                df_h.to_parquet(h_pq, index=False)

                if self.save_csv:
                    df_p.to_csv(self.output_dir / "portfolios.csv", index=False)
                    df_h.to_csv(self.output_dir / "portfolio_holdings.csv", index=False)

                logger.info(f"Saved {len(portfolios)} portfolios ({len(holding_rows)} holdings) to {p_pq} and {h_pq}")
                return p_pq, h_pq
            except Exception as e:
                raise StorageError(f"Failed to save portfolios: {e}") from e

    def save_market_data(self, df_market: pd.DataFrame) -> Path:
        """Save simulated OHLCV market dataset to Parquet and CSV.

        Args:
            df_market: Combined market data DataFrame.

        Returns:
            Path to saved Parquet file.
        """
        with Timer("Saving Market Data OHLCV"):
            try:
                pq_path = self.output_dir / "market_data_ohlcv.parquet"
                df_market.to_parquet(pq_path, index=False)

                if self.save_csv:
                    csv_path = self.output_dir / "market_data_ohlcv.csv"
                    df_market.to_csv(csv_path, index=False)

                logger.info(f"Saved market data ({len(df_market)} records) to {pq_path}")
                return pq_path
            except Exception as e:
                raise StorageError(f"Failed to save market data: {e}") from e

