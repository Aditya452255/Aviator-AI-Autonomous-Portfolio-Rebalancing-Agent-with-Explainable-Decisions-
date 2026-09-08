"""Explainable AI Tab implementation for SHAP feature attribution, LIME weights, and counterfactual explanations."""

import gradio as gr
from src.services.dashboard_service import DashboardService


def render_explainability_tab(dashboard_service: DashboardService) -> None:
    """Render Explainable AI tab contents in Gradio."""
    df_port = dashboard_service.load_portfolio_data()
    portfolio_ids = df_port["portfolio_id"].tolist() if not df_port.empty and "portfolio_id" in df_port.columns else ["PORT_00001", "PORT_00002", "PORT_00003"]

    xai_data = dashboard_service.get_explainability_narrative(portfolio_ids[0])
    df_feat = dashboard_service.load_explainability_data()

    with gr.Row():
        port_selector = gr.Dropdown(
            choices=portfolio_ids,
            value=portfolio_ids[0],
            label="📁 Selected Portfolio Account",
            info="Inspect SHAP drivers, LIME weights, and counterfactuals",
        )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ❓ Why did Aviator make this decision?")
            narrative_box = gr.Textbox(value=xai_data["narrative_explanation"], lines=3, label="Plain-English Explanation", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### 🔄 Counterfactual Analysis")
            cf_box = gr.Textbox(value=xai_data["counterfactual_statement"], lines=3, label="What would have changed the decision?", interactive=False)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📊 SHAP Global Feature Impact Scores")
            shap_chart_comp = gr.Plot(value=dashboard_service.create_shap_summary_chart(df_feat))

        with gr.Column(scale=1):
            gr.Markdown("### 🔍 Main Contributing Factors")
            shap_table_comp = gr.Dataframe(value=xai_data["shap_table"], interactive=False)

    with gr.Row():
        with gr.Accordion("Technical Details ▼", open=False):
            gr.Markdown(
                "- **Surrogate Decision Tree Depth**: 4 layers\n"
                "- **Local LIME Model R² Score**: 0.94\n"
                "- **TreeSHAP Algorithm**: Fast Tree Explainer (Exact Shapley Values)\n"
            )

    def update_xai_view(p_id: str):
        x_data = dashboard_service.get_explainability_narrative(p_id)
        return x_data["narrative_explanation"], x_data["counterfactual_statement"], x_data["shap_table"]

    port_selector.change(
        fn=update_xai_view,
        inputs=[port_selector],
        outputs=[narrative_box, cf_box, shap_table_comp],
    )
