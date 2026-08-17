"""Audit table component renderer."""

import gradio as gr
import pandas as pd


def build_audit_data_table(df: pd.DataFrame) -> gr.Dataframe:
    """Build immutable audit trail DataFrame viewer component."""
    return gr.Dataframe(
        value=df,
        headers=list(df.columns) if not df.empty else None,
        interactive=False,
        wrap=True,
    )
