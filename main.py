"""Main entry point script to execute Aviator AI Simulation, Monitoring, Optimization, Multi-Agent Intelligence, XAI, Governance, Backtesting, Gradio Dashboard, and Production Reliability Service."""

import argparse
import sys
from src.core.config import load_config
from src.core.logger import get_logger
from src.services.agent_service import AgentService
from src.services.backtesting_service import BacktestingService
from src.services.explainability_service import ExplainabilityService
from src.services.governance_service import GovernanceService
from src.services.monitoring_service import MonitoringService
from src.services.optimization_service import OptimizationService
from src.services.production_service import ProductionService
from src.services.simulation_service import SimulationService
from src.ui.app import launch_dashboard

logger = get_logger(__name__)


def main() -> None:
    """Main execution CLI entry point supporting Phases 1 through 9."""
    parser = argparse.ArgumentParser(
        description="Aviator AI - Autonomous Portfolio Rebalancing Agent"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        default=9,
        help="Phase to execute (1=Simulation, 2=Monitoring, 3=Optimization, 4=Multi-Agent Intelligence, 5=Explainable AI, 6=Governance, 7=Backtesting, 8=Gradio Dashboard, 9=Production Service & Observability)",
    )
    parser.add_argument("--clients", type=int, help="Override number of clients (default from config)")
    parser.add_argument("--portfolios", type=int, help="Override number of portfolios (default from config)")
    parser.add_argument("--securities", type=int, help="Override number of securities (default from config)")
    parser.add_argument("--days", type=int, help="Override number of trading days (default from config)")
    parser.add_argument("--port", type=int, default=7860, help="Port for Gradio dashboard (default 7860)")
    parser.add_argument("--health-port", type=int, default=8000, help="Port for FastAPI health server (default 8000)")
    args = parser.parse_args()

    config = load_config()

    if args.clients:
        config.simulation.num_clients = args.clients
    if args.portfolios:
        config.simulation.num_portfolios = args.portfolios
    if args.securities:
        config.simulation.num_securities = args.securities
    if args.days:
        config.simulation.trading_days = args.days

    phase_names = {
        1: "Simulation Layer",
        2: "Drift Monitoring & Trigger Intelligence Layer",
        3: "Optimization & Trade Generation Engine",
        4: "Multi-Agent Decision Intelligence Layer",
        5: "Explainable AI (XAI) Engine",
        6: "Human-in-the-Loop, Governance & Compliance Layer",
        7: "Backtesting, Simulation & Performance Evaluation Engine",
        8: "Gradio Enterprise Operations Dashboard",
        9: "Production Readiness, Reliability & Observability Service",
    }

    logger.info("===============================================================")
    logger.info("  Aviator AI - Autonomous Portfolio Rebalancing Agent")
    logger.info(f"  Executing Phase {args.phase}: {phase_names[args.phase]}")
    logger.info("===============================================================")

    if args.phase == 8:
        logger.info(f"Launching Gradio Enterprise Dashboard on http://localhost:{args.port}...")
        launch_dashboard(server_port=args.port)
        return

    if args.phase == 9:
        prod_service = ProductionService(config=config)
        reports = prod_service.run_production_health_cycle(save_exports=True)

        health = reports.get("health_status", {})
        sec = reports.get("security_report", {})

        logger.info("\n--- PHASE 9 PRODUCTION HEALTH & OBSERVABILITY SUMMARY ---")
        logger.info(f"Subsystem Status      : {health.get('status', 'HEALTHY')}")
        logger.info(f"CPU Usage             : {health.get('cpu_usage_pct', 0.0)}%")
        logger.info(f"Memory Usage          : {health.get('memory_usage_pct', 0.0)}%")
        logger.info(f"Authentication        : {sec.get('authentication_status', 'ENABLED')}")
        logger.info(f"RBAC Roles            : {', '.join(sec.get('roles_configured', []))}")
        logger.info(f"FastAPI Health API    : http://localhost:{args.health_port}/health")
        logger.info(f"Prometheus Metrics    : http://localhost:{args.health_port}/metrics")
        logger.info("===============================================================\n")
        return

    # Run Phase 1 Simulation
    sim_service = SimulationService(config=config)
    securities, clients, portfolios, df_market = sim_service.run_simulation()

    if args.phase >= 2:
        mon_service = MonitoringService(config=config)
        metrics_list, queue, alerts, analytics_mon = mon_service.run_monitoring_cycle(
            portfolios=portfolios,
            clients=clients,
            save_exports=True,
        )

        if args.phase >= 3:
            opt_service = OptimizationService(config=config)
            opt_results, analytics_opt = opt_service.run_optimization_cycle(
                portfolios=portfolios,
                rebalancing_queue=queue,
                clients=clients,
                securities=securities,
                save_exports=True,
            )

            if args.phase >= 4:
                agent_service = AgentService(config=config)
                decision_packages, analytics_agent = agent_service.run_decision_intelligence_cycle(
                    portfolios=portfolios,
                    optimization_results=opt_results,
                    clients=clients,
                    save_exports=True,
                )

                if args.phase >= 5:
                    xai_service = ExplainabilityService(config=config)
                    xai_results, analytics_xai = xai_service.run_explainability_cycle(
                        portfolios=portfolios,
                        decision_packages=decision_packages,
                        save_exports=True,
                        generate_plots=True,
                    )

                    if args.phase >= 6:
                        gov_service = GovernanceService(config=config)
                        approval_requests, analytics_gov = gov_service.run_governance_cycle(
                            portfolios=portfolios,
                            decision_packages=decision_packages,
                            explainability_results=xai_results,
                            save_exports=True,
                        )

                        if args.phase == 7:
                            bt_service = BacktestingService(config=config)
                            backtest_results, analytics_bt = bt_service.run_backtesting_cycle(
                                portfolios=portfolios,
                                optimization_results=opt_results,
                                decision_packages=decision_packages,
                                trading_days=config.simulation.trading_days,
                                save_exports=True,
                            )


if __name__ == "__main__":
    main()
