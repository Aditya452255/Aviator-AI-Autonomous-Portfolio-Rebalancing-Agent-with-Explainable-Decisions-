"""Explainability Tab implementation displaying multi-audience explanations and SHAP/LIME charts."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.lime_chart import build_lime_local_chart
from src.ui.components.shap_chart import build_shap_importance_chart


def render_explainability_tab(dashboard_service: DashboardService) -> None:
    """Render the Explainable AI (XAI) tab contents in Gradio."""
    df_feat = dashboard_service.load_explainability_data()

    gr.Markdown("### 🧠 Multi-Audience Explanation Inspector")
    with gr.Row():
        with gr.Column():
            gr.Markdown("#### 💬 Client Explanation (Plain English)")
            gr.Textbox(value="Your portfolio drifted due to equity growth. We recommended rebalancing to protect your gains.", lines=4, interactive=False)
        with gr.Column():
            gr.Markdown("#### 📊 Advisor Technical Brief")
            gr.Textbox(value="Portfolio drift reached 6.5%. Equity allocation is +5.2% overweight. Rebalancing generates $1,200 harvested losses.", lines=4, interactive=False)
        with gr.Column():
            gr.Markdown("#### 📜 Compliance Audit Log")
            gr.Textbox(value="[AUDIT] Portfolio PORT_00001 evaluated. Restricted list checked: Passed. Sector limits checked: Passed.", lines=4, interactive=False)

    gr.Markdown("### 🔬 Feature Attribution & Local Explanations")
    with gr.Row():
        with gr.Column():
            build_shap_importance_chart()
        with gr.Column():
            build_lime_local_chart()
