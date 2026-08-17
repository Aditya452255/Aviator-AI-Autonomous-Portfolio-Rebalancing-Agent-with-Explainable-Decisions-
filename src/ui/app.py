"""Entry point launcher for Gradio Enterprise Dashboard."""

from src.core.logger import get_logger
from src.ui.dashboard import create_dashboard_app

logger = get_logger(__name__)


def launch_dashboard(server_name: str = "0.0.0.0", server_port: int = 7860, share: bool = False) -> None:
    """Launch Gradio Enterprise Operations Dashboard application.

    Args:
        server_name: Host server IP address.
        server_port: Host port number.
        share: True to generate public Gradio link.
    """
    logger.info(f"Launching Aviator AI Gradio Dashboard on http://{server_name}:{server_port}...")
    app = create_dashboard_app()
    app.launch(server_name=server_name, server_port=server_port, share=share)


if __name__ == "__main__":
    launch_dashboard()
