"""Explanation domain models for Client, Advisor, and Compliance audiences."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClientExplanation(BaseModel):
    """Plain-English explanation tailored for retail clients (max 200 words)."""

    portfolio_id: str = Field(..., description="Target portfolio ID")
    summary: str = Field(..., description="Plain-English explanation summary")
    word_count: int = Field(..., description="Word count of summary")
    benefits: str = Field(..., description="Expected benefits")
    costs_and_taxes: str = Field(..., description="Cost and tax overview")
    risks: str = Field(..., description="Risk impact")


class AdvisorExplanation(BaseModel):
    """Semi-technical explanation tailored for wealth advisors (max 400 words)."""

    portfolio_id: str = Field(..., description="Target portfolio ID")
    summary: str = Field(..., description="Technical advisor summary")
    word_count: int = Field(..., description="Word count of summary")
    drift_analysis: str = Field(..., description="Quantitative drift analysis")
    tracking_error_analysis: str = Field(..., description="Tracking error analysis")
    tax_and_cost_analysis: str = Field(..., description="Tax and cost analysis")
    liquidity_and_execution: str = Field(..., description="Liquidity and TWAP/VWAP strategy")


class ComplianceExplanation(BaseModel):
    """Highly detailed compliance and regulatory audit log."""

    decision_id: str = Field(..., description="Decision ID")
    portfolio_id: str = Field(..., description="Target portfolio ID")
    timestamp: str = Field(..., description="Generation timestamp")
    audit_summary: str = Field(..., description="Audit summary string")
    input_features: Dict[str, float] = Field(default_factory=dict, description="Input features map")
    optimization_summary: Dict[str, float | str] = Field(default_factory=dict, description="Phase 3 summary")
    constraint_results: List[str] = Field(default_factory=list, description="Constraint invariants check")
    agent_consensus: str = Field(..., description="Phase 4 multi-agent consensus log")
    shap_summary: str = Field(..., description="SHAP feature attribution summary")
    counterfactual_summary: str = Field(..., description="Counterfactual analysis summary")
    config_version: str = Field(default="v1.0", description="Config version")
    model_version: str = Field(default="v1.0.0", description="Surrogate model version")
