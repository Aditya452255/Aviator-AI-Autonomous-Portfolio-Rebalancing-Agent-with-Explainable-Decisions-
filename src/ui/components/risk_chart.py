"""Risk chart Plotly component renderer."""

import gradio as gr
import plotly.express as px
import plotly.graph_objects as go


def build_risk_distribution_chart() -> gr.Plot:
    """Build Plotly risk distribution chart."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=[0.05, 0.08, 0.12, 0.15, 0.18, 0.22, 0.25], name="Volatility"))
    fig.update_layout(title="Portfolio Volatility Distribution", template="plotly_dark", height=350)
    return gr.Plot(value=fig)
