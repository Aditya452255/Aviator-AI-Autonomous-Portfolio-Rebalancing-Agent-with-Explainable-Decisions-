"""UI Layout module providing header banner, project narrative, and container layout."""

import gradio as gr


def build_header() -> gr.HTML:
    """Build the Aviator AI Final Year Project Header Banner HTML component."""
    html_content = """
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #1e293b 100%); padding: 24px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 style="color: #f8fafc; font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.025em; display: flex; align-items: center; gap: 10px;">
                    <span style="background: #3b82f6; color: #ffffff; padding: 4px 12px; border-radius: 8px; font-size: 1.1rem;">AVIATOR AI</span>
                    Autonomous Portfolio Rebalancing Agent
                </h1>
                <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 6px; margin-bottom: 0;">
                    <strong style="color: #60a5fa;">Final Year College Project</strong> | Explainable AI Decisions & Human-in-the-Loop Governance Command Center
                </p>
            </div>
            <div style="background: rgba(30, 41, 59, 0.8); padding: 10px 18px; border-radius: 8px; border: 1px solid #475569; text-align: right;">
                <span style="color: #38bdf8; font-weight: 600; font-size: 0.9rem;">AUTOMATED STORY WORKFLOW</span>
                <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 2px;">
                    Portfolio ➔ Drift ➔ Risk ➔ Optimize ➔ Agents ➔ XAI ➔ Governance ➔ Backtest
                </div>
            </div>
        </div>
    </div>
    """
    return gr.HTML(value=html_content)
