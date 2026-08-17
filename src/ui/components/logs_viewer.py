"""Logs viewer component renderer."""

import gradio as gr


def build_system_logs_viewer(log_text: str = "System Initialized cleanly. Phase 1-7 pipelines active.") -> gr.Textbox:
    """Build recent system log viewer component."""
    return gr.Textbox(
        value=log_text,
        lines=12,
        label="Recent System Log Output",
        interactive=False,
    )
