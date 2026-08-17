"""Allocation chart Plotly component renderer."""

import gradio as gr
import plotly.graph_objects as go


def build_allocation_chart(current: dict = None, target: dict = None) -> gr.Plot:
    """Build Plotly asset allocation breakdown chart."""
    c_data = current or {"Equity": 65.0, "Fixed Income": 25.0, "Alternatives": 5.0, "Cash": 5.0}
    t_data = target or {"Equity": 60.0, "Fixed Income": 30.0, "Alternatives": 5.0, "Cash": 5.0}

    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(c_data.keys()), y=list(c_data.values()), name="Current Allocation"))
    fig.add_trace(go.Bar(x=list(t_data.keys()), y=list(t_data.values()), name="Target Allocation"))
    fig.update_layout(barmode="group", title="Current vs Target Asset Allocation %", template="plotly_dark", height=350)
    return gr.Plot(value=fig)
