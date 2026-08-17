"""Metric cards component renderer."""

import gradio as gr


def build_kpi_card(title: str, value: str, subtitle: str = "") -> gr.HTML:
    """Build single HTML KPI card block."""
    html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """
    return gr.HTML(value=html)
