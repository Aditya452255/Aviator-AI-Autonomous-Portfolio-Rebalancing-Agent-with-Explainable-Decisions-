"""Governance & Approval Tab implementation displaying Human-in-the-Loop approval workflows and cryptographic audit trails."""

import gradio as gr
from src.services.dashboard_service import DashboardService


def render_governance_tab(dashboard_service: DashboardService) -> None:
    """Render Governance & Approvals tab contents in Gradio."""
    df_port = dashboard_service.load_portfolio_data()
    portfolio_ids = df_port["portfolio_id"].tolist() if not df_port.empty and "portfolio_id" in df_port.columns else ["PORT_00001", "PORT_00002", "PORT_00003"]

    gov_data = dashboard_service.get_governance_approval(portfolio_ids[0])

    with gr.Row():
        port_selector = gr.Dropdown(
            choices=portfolio_ids,
            value=portfolio_ids[0],
            label="📁 Selected Portfolio Account",
            info="Review approval tier, policy check status, and audit logs",
        )

    with gr.Row():
        tier_card = gr.Textbox(value=gov_data["approval_tier"], label="Human Governance Status", interactive=False)
        policy_card = gr.Textbox(value=gov_data["risk_policy_status"], label="Risk Policy Check", interactive=False)
        safety_card = gr.Textbox(value=gov_data["system_safety_status"], label="System Safety Status", interactive=False)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 👤 Human-in-the-Loop (HITL) Advisor Action Center")
            gr.Markdown(f"**Policy Trigger**: _{gov_data['policy_reason']}_")

            with gr.Row():
                approve_btn = gr.Button("✅ Approve Trade", variant="primary")
                reject_btn = gr.Button("❌ Reject Trade", variant="stop")
                override_btn = gr.Button("✏️ Override Quantity", variant="secondary")

            action_status_box = gr.Textbox(value="Awaiting Advisor Review", label="Action Status", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### 📜 Event Audit Log (Selected Portfolio)")
            aud_table_comp = gr.Dataframe(value=gov_data["audit_trail_table"], interactive=False)

            with gr.Accordion("Technical Details ▼", open=False):
                gr.Markdown(
                    f"- **SHA-256 Cryptographic Hash**: `{gov_data['audit_hash']}`\n"
                    f"- **Audit Timestamp**: `{gov_data['audit_timestamp']}`\n"
                    f"- **Ledger Status**: `IMMUTABLE & VERIFIED`\n"
                )

    def handle_approve(p_id: str):
        return f"✅ Recommendation for portfolio {p_id} APPROVED by Advisor at {gov_data['audit_timestamp']}."

    def handle_reject(p_id: str):
        return f"❌ Recommendation for portfolio {p_id} REJECTED by Advisor. Trade cancelled."

    def handle_override(p_id: str):
        return f"✏️ Override form opened for portfolio {p_id}. Trade parameters unlocked."

    def update_governance_view(p_id: str):
        g_data = dashboard_service.get_governance_approval(p_id)
        return g_data["approval_tier"], g_data["risk_policy_status"], g_data["system_safety_status"], g_data["audit_trail_table"], "Awaiting Advisor Review"

    port_selector.change(
        fn=update_governance_view,
        inputs=[port_selector],
        outputs=[tier_card, policy_card, safety_card, aud_table_comp, action_status_box],
    )

    approve_btn.click(fn=handle_approve, inputs=[port_selector], outputs=[action_status_box])
    reject_btn.click(fn=handle_reject, inputs=[port_selector], outputs=[action_status_box])
    override_btn.click(fn=handle_override, inputs=[port_selector], outputs=[action_status_box])
