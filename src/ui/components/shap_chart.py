"""SHAP chart Plotly component renderer."""

import gradio as gr
import plotly.express as px
import plotly.graph_objects as go


def build_shap_importance_chart() -> gr.Plot:
    """Build Plotly SHAP feature attribution bar chart."""
    features = ["portfolio_drift", "market_volatility", "tax_impact", "liquidity_score", "days_since_rebalance"]
    shap_vals = [0.45, 0.28, 0.18, 0.12, 0.08]

    fig = px.bar(x=shap_vals, y=features, orientation="h", title="TreeSHAP Global Feature Importance", labels={"x": "SHAP Importance Score", "y": "Feature"})
    fig.update_layout(template="plotly_dark", height=350)
    return gr.Plot(value=fig)
