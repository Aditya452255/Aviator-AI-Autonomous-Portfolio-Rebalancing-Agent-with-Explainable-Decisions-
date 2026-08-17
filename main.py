"""Main entry point script supporting Phase 1 Simulation."""
import argparse
from src.core.config import load_config
from src.core.logger import get_logger
from src.services.simulation_service import SimulationService

logger = get_logger(__name__)

def main() -> None:
    parser = argparse.ArgumentParser(description="Aviator AI - Autonomous Portfolio Rebalancing Agent")
    parser.add_argument("--phase", type=int, choices=[1], default=1, help="Phase to execute (1=Simulation)")
    parser.add_argument("--clients", type=int, help="Override number of clients")
    parser.add_argument("--portfolios", type=int, help="Override number of portfolios")
    parser.add_argument("--securities", type=int, help="Override number of securities")
    parser.add_argument("--days", type=int, help="Override number of trading days")
    args = parser.parse_args()

    config = load_config()
    if args.clients: config.simulation.num_clients = args.clients
    if args.portfolios: config.simulation.num_portfolios = args.portfolios
    if args.securities: config.simulation.num_securities = args.securities
    if args.days: config.simulation.trading_days = args.days

    logger.info("===============================================================")
    logger.info("  Aviator AI - Phase 1: Simulation Layer")
    logger.info("===============================================================")
    sim_service = SimulationService(config=config)
    securities, clients, portfolios, df_market = sim_service.run_simulation()
    logger.info(f"Simulation completed for {len(clients)} clients and {len(portfolios)} portfolios.")

if __name__ == "__main__":
    main()
