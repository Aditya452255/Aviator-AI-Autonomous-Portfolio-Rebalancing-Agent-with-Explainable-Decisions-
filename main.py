"""Main entry point script supporting Phase 1-7."""
import argparse
from src.core.config import load_config
from src.core.logger import get_logger
from src.services.simulation_service import SimulationService
from src.services.monitoring_service import MonitoringService
from src.services.optimization_service import OptimizationService
from src.services.agent_service import AgentService
from src.services.explainability_service import ExplainabilityService
from src.services.governance_service import GovernanceService
from src.services.backtesting_service import BacktestingService

logger = get_logger(__name__)

def main() -> None:
    parser = argparse.ArgumentParser(description="Aviator AI - Autonomous Portfolio Rebalancing Agent")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4, 5, 6, 7], default=7, help="Phase to execute")
    args = parser.parse_args()
    config = load_config()

    sim_service = SimulationService(config=config)
    securities, clients, portfolios, df_market = sim_service.run_simulation()

    if args.phase >= 2:
        mon_service = MonitoringService(config=config)
        metrics_list, queue, alerts, analytics_mon = mon_service.run_monitoring_cycle(
            portfolios=portfolios, clients=clients, save_exports=True
        )

        if args.phase >= 3:
            opt_service = OptimizationService(config=config)
            opt_results, analytics_opt = opt_service.run_optimization_cycle(
                portfolios=portfolios, rebalancing_queue=queue, clients=clients, securities=securities, save_exports=True
            )

            if args.phase >= 4:
                agent_service = AgentService(config=config)
                decision_packages, analytics_agent = agent_service.run_decision_intelligence_cycle(
                    portfolios=portfolios, optimization_results=opt_results, clients=clients, save_exports=True
                )

                if args.phase >= 5:
                    xai_service = ExplainabilityService(config=config)
                    xai_results, analytics_xai = xai_service.run_explainability_cycle(
                        portfolios=portfolios, decision_packages=decision_packages, save_exports=True, generate_plots=True
                    )

                    if args.phase >= 6:
                        gov_service = GovernanceService(config=config)
                        approval_requests, analytics_gov = gov_service.run_governance_cycle(
                            portfolios=portfolios, decision_packages=decision_packages, explainability_results=xai_results, save_exports=True
                        )

                        if args.phase == 7:
                            bt_service = BacktestingService(config=config)
                            backtest_results, analytics_bt = bt_service.run_backtesting_cycle(
                                portfolios=portfolios, optimization_results=opt_results, decision_packages=decision_packages, trading_days=config.simulation.trading_days, save_exports=True
                            )
                            logger.info("Backtesting engine completed simulation.")

if __name__ == "__main__":
    main()
