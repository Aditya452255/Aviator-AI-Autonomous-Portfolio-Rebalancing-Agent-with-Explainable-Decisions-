"""Unit tests for Client Profile generation."""

import pytest
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.client import ClientProfile


def test_client_generator_sample() -> None:
    """Test generating a sample batch of clients."""
    sec_gen = SecurityMasterGenerator(seed=42)
    securities = sec_gen.generate_securities(num_securities=50)

    client_gen = ClientProfileGenerator(seed=42)
    clients = client_gen.generate_clients(num_clients=100, securities=securities)

    assert len(clients) == 100
    for c in clients:
        assert isinstance(c, ClientProfile)
        assert c.client_id.startswith("CLT_")
        assert c.portfolio_size >= 50000.0
        assert c.annual_income >= 300000.0
        assert 1 <= c.investment_horizon <= 30
        assert c.country in ["India", "USA", "UK", "Germany", "Singapore", "UAE"]


def test_client_id_uniqueness() -> None:
    """Test that all client IDs are unique."""
    client_gen = ClientProfileGenerator(seed=123)
    clients = client_gen.generate_clients(num_clients=200)
    ids = {c.client_id for c in clients}
    assert len(ids) == 200
