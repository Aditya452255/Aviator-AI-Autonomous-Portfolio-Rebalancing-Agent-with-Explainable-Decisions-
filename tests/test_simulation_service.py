"""Unit tests for SimulationService workflow and validation."""

from pathlib import Path
import pytest
from src.core.config import load_config
from src.services.simulation_service import SimulationService


def test_simulation_service_run(tmp_path: Path) -> None:
    """Test full simulation run with small sample size."""
    config = load_config("config")
    config.simulation.num_clients = 20
    config.simulation.num_portfolios = 20
    config.simulation.num_securities = 50
    config.simulation.trading_days = 10
    config.storage.output_dir = str(tmp_path)

    service = SimulationService(config=config)
    securities, clients, portfolios, df_market = service.run_simulation()

    assert len(securities) == 50
    assert len(clients) == 20
    assert len(portfolios) == 20
    assert len(df_market) == 500

    # Validate output files exist
    assert (tmp_path / "securities_master.parquet").exists()
    assert (tmp_path / "client_profiles.parquet").exists()
    assert (tmp_path / "portfolios.parquet").exists()
    assert (tmp_path / "portfolio_holdings.parquet").exists()
    assert (tmp_path / "market_data_ohlcv.parquet").exists()
