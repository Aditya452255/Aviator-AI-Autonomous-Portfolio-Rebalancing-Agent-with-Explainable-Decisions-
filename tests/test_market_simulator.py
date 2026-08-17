"""Unit tests for Market Data Simulator."""

import pytest
from src.data.market_data_simulator import MarketDataSimulator
from src.data.security_master_generator import SecurityMasterGenerator


def test_market_data_simulator_252_days() -> None:
    """Test market simulation for 50 securities over 252 trading days."""
    sec_gen = SecurityMasterGenerator(seed=42)
    securities = sec_gen.generate_securities(num_securities=50)

    mkt_sim = MarketDataSimulator(seed=42)
    market_dict, df_market = mkt_sim.simulate_market(securities=securities, trading_days=252)

    assert len(market_dict) == 50
    assert not df_market.empty
    assert len(df_market) == 50 * 252

    # Check OHLC Invariants
    high_violations = df_market[df_market["high"] < df_market[["open", "close", "low"]].max(axis=1)]
    assert high_violations.empty, "High price invariant violated"

    low_violations = df_market[df_market["low"] > df_market[["open", "close", "high"]].min(axis=1)]
    assert low_violations.empty, "Low price invariant violated"

    # Prices > 0
    assert (df_market["open"] > 0).all()
    assert (df_market["high"] > 0).all()
    assert (df_market["low"] > 0).all()
    assert (df_market["close"] > 0).all()
