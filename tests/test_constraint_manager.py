"""Unit tests for Constraint Manager validation rules."""

import pytest
from src.core.config import load_config
from src.data.client_profile_generator import ClientProfileGenerator
from src.data.portfolio_generator import PortfolioGenerator
from src.data.security_master_generator import SecurityMasterGenerator
from src.models.risk_category import RiskCategory
from src.optimization.constraint_manager import ConstraintManager


def test_constraint_manager_validation() -> None:
    """Test validation of position weight limits, cash minimums, and restricted securities."""
    config = load_config("config")
    risk_cats = {
        k: RiskCategory(
            id=v.id,
            name=v.name,
            target_equity=v.target_equity,
            target_fixed_income=v.target_fixed_income,
            target_alternatives=v.target_alternatives,
            target_cash=v.target_cash,
            drift_threshold=v.drift_threshold,
        )
        for k, v in config.risk_categories.items()
    }

    sec_gen = SecurityMasterGenerator(seed=42)
    securities = sec_gen.generate_securities(num_securities=50)
    sec_map = {s.ticker: s for s in securities}

    client_gen = ClientProfileGenerator(seed=42)
    clients = client_gen.generate_clients(num_clients=5, securities=securities)

    port_gen = PortfolioGenerator(risk_categories=risk_cats, seed=42)
    portfolios = port_gen.generate_portfolios(clients=clients, securities=securities)

    cm = ConstraintManager(max_position_weight=0.15, min_cash_weight=0.05)

    # Test position weight breach (>15%)
    overweight_sec = {portfolios[0].holdings[0].ticker: 0.25, "Cash": 0.01}
    violations = cm.validate_constraints(
        portfolio=portfolios[0],
        proposed_weights=overweight_sec,
        client=clients[0],
        securities_map=sec_map,
    )

    assert len(violations) >= 2
    v_names = {v.constraint_name for v in violations}
    assert "Maximum Position Limit" in v_names
    assert "Minimum Cash Reserve" in v_names
