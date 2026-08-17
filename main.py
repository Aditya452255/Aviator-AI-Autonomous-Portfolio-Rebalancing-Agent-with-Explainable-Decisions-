"""Main entry point script supporting Phase 1-2."""
import argparse
from src.core.config import load_config
from src.core.logger import get_logger
from src.services.simulation_service import SimulationService
from src.services.monitoring_service import MonitoringService

logger = get_logger(__name__)

def main() -> None:
    parser = argparse.ArgumentParser(description="Aviator AI - Autonomous Portfolio Rebalancing Agent")
    parser.add_argument("--phase", type=int, choices=[1, 2], default=2, help="Phase to execute (1=Simulation, 2=Monitoring)")
    args = parser.parse_args()
    config = load_config()

    sim_service = SimulationService(config=config)
    securities, clients, portfolios, df_market = sim_service.run_simulation()

    if args.phase >= 2:
        mon_service = MonitoringService(config=config)
        metrics_list, queue, alerts, analytics_mon = mon_service.run_monitoring_cycle(
            portfolios=portfolios, clients=clients, save_exports=True
        )
        logger.info(f"Monitoring completed. Triggered portfolios queue size: {queue.qsize()}")

if __name__ == "__main__":
    main()
