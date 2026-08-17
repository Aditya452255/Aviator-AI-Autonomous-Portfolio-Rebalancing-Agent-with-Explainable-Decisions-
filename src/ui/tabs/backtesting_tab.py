"""Backtesting Tab implementation displaying strategy comparison, benchmark alpha, and stress tests."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.performance_chart import build_performance_comparison_chart
from src.ui.components.portfolio_table import build_portfolio_data_table


def render_backtesting_tab(dashboard_service: DashboardService) -> None:
    """Render the Backtesting & Benchmarks tab contents in Gradio."""
    df_strat, df_bench = dashboard_service.load_backtesting_data()

    gr.Markdown("### 📊 Strategy Performance & Benchmark Comparisons")
    with gr.Row():
        with gr.Column(scale=2):
            build_performance_comparison_chart()
        with gr.Column(scale=1):
            gr.Markdown("#### 🥇 Strategy Winner Summary")
            build_portfolio_data_table(df_strat)

    gr.Markdown("### 🎯 Excess Return Alpha & Beta Analysis")
    build_portfolio_data_table(df_bench)
