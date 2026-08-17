"""Explainability Result domain model aggregating SHAP, LIME, counterfactuals, and quality scores."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.models.counterfactual import CounterfactualExplanation
from src.models.explanation import AdvisorExplanation, ClientExplanation, ComplianceExplanation
from src.models.feature_importance import FeatureAttribution


class QualityScores(BaseModel):
    """Explanation quality metrics (0.0 to 1.0)."""

    completeness_score: float = Field(..., ge=0.0, le=1.0)
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    readability_score: float = Field(..., ge=0.0, le=1.0)
    consistency_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)


class ExplainabilityResult(BaseModel):
    """Complete explainability result for a portfolio decision."""

    explanation_id: str = Field(..., description="Unique explanation ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    decision_id: str = Field(..., description="Associated Phase 4 decision ID")

    feature_attributions: List[FeatureAttribution] = Field(default_factory=list)
    shap_values: Dict[str, float] = Field(default_factory=dict)
    lime_contributions: Dict[str, float] = Field(default_factory=dict)
    counterfactuals: List[CounterfactualExplanation] = Field(default_factory=list)

    client_explanation: ClientExplanation
    advisor_explanation: AdvisorExplanation
    compliance_explanation: ComplianceExplanation

    quality_scores: QualityScores
    visualization_paths: List[str] = Field(default_factory=list)
