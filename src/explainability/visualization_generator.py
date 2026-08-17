"""Visualization Generator rendering SHAP, LIME, Feature Attribution, and Counterfactual charts."""

from pathlib import Path
from typing import Dict, List, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.core.logger import get_logger

logger = get_logger(__name__)


class VisualizationGenerator:
    """Enterprise Visualization Generator producing crisp PNG explainability charts."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else Path("data/output/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_feature_importance_bar_chart(
        self,
        portfolio_id: str,
        shap_values: Dict[str, float],
    ) -> str:
        """Generate SHAP local feature importance bar chart PNG image.

        Args:
            portfolio_id: Target portfolio ID.
            shap_values: Map of feature_name -> shap_value.

        Returns:
            Absolute filepath string of saved plot image.
        """
        features = list(shap_values.keys())
        values = list(shap_values.values())

        # Sort by absolute SHAP value
        sorted_indices = np.argsort([abs(v) for v in values])
        sorted_features = [features[i] for i in sorted_indices]
        sorted_values = [values[i] for i in sorted_indices]

        colors = ["#2ecc71" if v > 0 else "#e74c3c" for v in sorted_values]

        plt.figure(figsize=(8, 5))
        plt.barh(sorted_features, sorted_values, color=colors)
        plt.axvline(0, color="gray", linestyle="--", linewidth=0.8)
        plt.xlabel("SHAP Value (Impact on Rebalance Decision)")
        plt.title(f"SHAP Feature Attribution — Portfolio {portfolio_id}")
        plt.tight_layout()

        file_path = self.output_dir / f"shap_bar_{portfolio_id}.png"
        plt.savefig(file_path, dpi=200)
        plt.close()

        logger.debug(f"Saved SHAP bar plot image to {file_path}")
        return str(file_path)

    def generate_counterfactual_comparison_chart(
        self,
        portfolio_id: str,
        current_drift: float,
        threshold_drift: float,
    ) -> str:
        """Generate counterfactual threshold comparison plot image.

        Args:
            portfolio_id: Target portfolio ID.
            current_drift: Current observed drift score.
            threshold_drift: Rebalance trigger threshold.

        Returns:
            Absolute filepath string of saved plot image.
        """
        categories = ["Current Drift", "Rebalance Threshold"]
        values = [current_drift * 100.0, threshold_drift * 100.0]
        colors = ["#e74c3c" if current_drift >= threshold_drift else "#3498db", "#95a5a6"]

        plt.figure(figsize=(6, 4))
        bars = plt.bar(categories, values, color=colors, width=0.5)
        plt.ylabel("Portfolio RMS Drift (%)")
        plt.title(f"Counterfactual Drift Threshold Comparison — {portfolio_id}")

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.2, f"{yval:.2f}%", ha="center", va="bottom", fontweight="bold")

        plt.tight_layout()
        file_path = self.output_dir / f"counterfactual_{portfolio_id}.png"
        plt.savefig(file_path, dpi=200)
        plt.close()

        logger.debug(f"Saved Counterfactual plot image to {file_path}")
        return str(file_path)
