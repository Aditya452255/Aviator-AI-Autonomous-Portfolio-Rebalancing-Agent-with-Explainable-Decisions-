"""Unit tests for StorageService dataset persistence."""

from pathlib import Path
import pytest
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.market_data_simulator import MarketDataSimulator
from src.data.security_master_generator import SecurityMasterGenerator
from src.services.storage_service import StorageService


def test_storage_service_save(tmp_path: Path) -> None:
    """Test saving securities, clients, portfolios, and market data."""
    storage = StorageService(output_dir=str(tmp_path), save_csv=True)

    sec_gen = SecurityMasterGenerator(seed=42)
    securities = sec_gen.generate_securities(num_securities=20)

    client_gen = ClientProfileGenerator(seed=42)
    clients = client_gen.generate_clients(num_clients=20, securities=securities)

    mkt_sim = MarketDataSimulator(seed=42)
    _, df_market = mkt_sim.simulate_market(securities=securities, trading_days=10)

    p_sec = storage.save_securities(securities)
    assert p_sec.exists()
    assert (tmp_path / "securities_master.csv").exists()

    p_clt = storage.save_clients(clients)
    assert p_clt.exists()
    assert (tmp_path / "client_profiles.csv").exists()

    p_mkt = storage.save_market_data(df_market)
    assert p_mkt.exists()
    assert (tmp_path / "market_data_ohlcv.csv").exists()
