"""Governance Tab implementation displaying approval queue, manual override form, kill switch, and audit logs."""

import gradio as gr
from src.services.dashboard_service import DashboardService
from src.ui.components.audit_table import build_audit_data_table


def render_governance_tab(dashboard_service: DashboardService) -> None:
    """Render the Governance & Approvals tab contents in Gradio."""
    df_app, df_ovr, df_aud = dashboard_service.load_governance_data()

    gr.Markdown("### 🛡️ Human-in-the-Loop Governance & Approvals")
    with gr.Row():
        with gr.Column():
            gr.Markdown("#### 🚨 Enterprise Safety Controls")
            ks_toggle = gr.Radio(choices=["DEACTIVATED", "ACTIVATED"], value="DEACTIVATED", label="Enterprise Kill Switch Toggle")
            ks_btn = gr.Button("Apply Safety Status", variant="stop")

        with gr.Column():
            gr.Markdown("#### ✍️ Manual Advisor Override Form")
            target_port = gr.Textbox(placeholder="PORT_00001", label="Portfolio ID")
            action_choice = gr.Dropdown(choices=["APPROVE", "REJECT", "MODIFY", "DEFER", "CANCEL"], value="APPROVE", label="Action")
            reason_category = gr.Dropdown(choices=["CLIENT_REQUEST", "MARKET_VOLATILITY", "TAX_TACTICAL", "CASH_REQUIREMENT"], value="CLIENT_REQUEST", label="Reason Category")
            comments_box = gr.Textbox(placeholder="Advisor comments...", label="Mandatory Comments")
            ovr_btn = gr.Button("Submit Advisor Override", variant="primary")

    gr.Markdown("### 📜 Immutable Event Audit Trail")
    build_audit_data_table(df_aud)
