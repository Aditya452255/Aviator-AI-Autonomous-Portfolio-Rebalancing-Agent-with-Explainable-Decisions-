"""LIME chart Plotly component renderer."""

import gradio as gr
import plotly.express as px
import plotly.graph_objects as go


def build_lime_local_chart() -> gr.Plot:
    """Build Plotly LIME local explanation bar chart."""
    features = ["portfolio_drift > 5%", "market_volatility < 20%", "tax_impact low"]
    weights = [0.38, 0.22, 0.19]

    fig = px.bar(x=weights, y=features, orientation="h", title="LIME Local Decision Explanations", labels={"x": "LIME Weight", "y": "Condition"})
    fig.update_layout(template="plotly_dark", height=350)
    return gr.Plot(value=fig)
