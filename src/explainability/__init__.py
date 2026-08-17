"""Explainability package containing SHAP, LIME, counterfactual, multi-audience, and visualization engines."""

from src.explainability.surrogate_model import SurrogateModel
from src.explainability.shap_engine import SHAPEngine
from src.explainability.lime_engine import LIMEEngine
from src.explainability.counterfactual_engine import CounterfactualEngine
from src.explainability.feature_attribution import FeatureAttributionEngine
from src.explainability.client_explainer import ClientExplainer
from src.explainability.advisor_explainer import AdvisorExplainer
from src.explainability.compliance_explainer import ComplianceExplainer
from src.explainability.decision_explainer import DecisionExplainer
from src.explainability.explanation_validator import ExplanationValidator
from src.explainability.explanation_quality import ExplanationQualityEngine
from src.explainability.visualization_generator import VisualizationGenerator

__all__ = [
    "SurrogateModel",
    "SHAPEngine",
    "LIMEEngine",
    "CounterfactualEngine",
    "FeatureAttributionEngine",
    "ClientExplainer",
    "AdvisorExplainer",
    "ComplianceExplainer",
    "DecisionExplainer",
    "ExplanationValidator",
    "ExplanationQualityEngine",
    "VisualizationGenerator",
]
