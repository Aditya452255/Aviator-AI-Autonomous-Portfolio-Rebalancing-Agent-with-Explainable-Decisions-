"""UI Layout module providing header banner and layout containers."""

import gradio as gr


def build_header() -> gr.HTML:
    """Build the Aviator AI Header Banner HTML component."""
    html_content = """
    <div class="header-banner">
        <h1>Aviator AI — Autonomous Portfolio Rebalancing Agent</h1>
        <p>Enterprise Operations Dashboard | Explainable AI Decisions & Human-in-the-Loop Governance Command Center</p>
    </div>
    """
    return gr.HTML(value=html_content)
