"""Trade Execution Tab implementation displaying trade order lists and TWAP/VWAP strategy status."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.trade_table import build_trade_data_table


def render_trade_execution_tab(dashboard_service: DashboardService) -> None:
    """Render the Trade Execution tab contents in Gradio."""
    df_trades = dashboard_service.load_trade_execution_data()

    gr.Markdown("### 🛒 Executable Trade Orders & Slicing Schedule")
    build_trade_data_table(df_trades)

    gr.Markdown("### 📊 Market Impact & Liquidity Model")
    gr.Markdown(
        "- **Execution Algorithms**: TWAP (Time-Weighted), VWAP (Volume-Weighted)\n"
        "- **Transaction Costs**: Brokerage + STT + Exchange Fees + Stamp Duty + ADV Market Impact\n"
    )
