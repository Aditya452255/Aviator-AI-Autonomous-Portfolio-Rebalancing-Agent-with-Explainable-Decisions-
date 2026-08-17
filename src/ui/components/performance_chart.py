"""Performance chart Plotly component renderer."""

import gradio as gr
import plotly.express as px
import plotly.graph_objects as go


def build_performance_comparison_chart() -> gr.Plot:
    """Build Plotly strategy performance line chart."""
    fig = go.Figure()
    days = list(range(1, 253))
    bh = [100.0 * (1 + 0.12 * d / 252.0) for d in days]
    ai = [100.0 * (1 + 0.157 * d / 252.0) for d in days]

    fig.add_trace(go.Scatter(x=days, y=bh, mode="lines", name="Buy & Hold"))
    fig.add_trace(go.Scatter(x=days, y=ai, mode="lines", name="AI Optimized"))
    fig.update_layout(title="Cumulative Strategy Returns (252 Trading Days)", template="plotly_dark", height=380)
    return gr.Plot(value=fig)
