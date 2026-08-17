"""Trade table component renderer."""

import gradio as gr
import pandas as pd


def build_trade_data_table(df: pd.DataFrame) -> gr.Dataframe:
    """Build trade execution DataFrame viewer component."""
    return gr.Dataframe(
        value=df,
        headers=list(df.columns) if not df.empty else None,
        interactive=False,
        wrap=True,
    )
