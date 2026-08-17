"""Main entry point script supporting Phase 1-8."""
import argparse
from src.core.config import load_config
from src.core.logger import get_logger
from src.ui.app import launch_dashboard

logger = get_logger(__name__)

def main() -> None:
    parser = argparse.ArgumentParser(description="Aviator AI - Autonomous Portfolio Rebalancing Agent")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8], default=8, help="Phase to execute")
    parser.add_argument("--port", type=int, default=7860, help="Port for Gradio dashboard")
    args = parser.parse_args()

    if args.phase == 8:
        logger.info(f"Launching Gradio Enterprise Dashboard on http://localhost:{args.port}...")
        launch_dashboard(server_port=args.port)

if __name__ == "__main__":
    main()
