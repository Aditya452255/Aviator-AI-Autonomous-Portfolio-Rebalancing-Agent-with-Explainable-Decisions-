"""UI Theme definition providing custom CSS styling and Gradio theme tokens for Aviator AI."""

CUSTOM_CSS = """
.container { max-width: 1400px; margin: auto; }
.header-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0284c7 100%);
    padding: 24px 32px;
    border-radius: 12px;
    color: #ffffff;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}
.header-banner h1 { margin: 0; font-size: 2.2rem; font-weight: 700; color: #f8fafc; }
.header-banner p { margin: 6px 0 0 0; color: #cbd5e1; font-size: 1.05rem; }

.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}
.metric-title { color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
.metric-value { color: #38bdf8; font-size: 1.8rem; font-weight: 700; margin-top: 4px; }
.metric-subtitle { color: #10b981; font-size: 0.8rem; margin-top: 2px; }

.status-badge-active { background: #065f46; color: #34d399; padding: 6px 14px; border-radius: 9999px; font-size: 0.9rem; font-weight: 700; display: inline-block; }
.status-badge-alert { background: #991b1b; color: #fca5a5; padding: 6px 14px; border-radius: 9999px; font-size: 0.9rem; font-weight: 700; display: inline-block; }

.demo-btn {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
}

.agent-card {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}
.agent-card-title { color: #38bdf8; font-weight: 700; font-size: 1.1rem; }
.agent-card-role { color: #94a3b8; font-size: 0.85rem; font-style: italic; }
.agent-card-vote { color: #34d399; font-weight: 700; font-size: 1rem; margin-top: 6px; }
"""
