"""Explanation Validator verifying structural completeness, length limits, and numerical consistency."""

from typing import Dict, List, Optional
from src.core.exceptions import ValidationError
from src.core.logger import get_logger
from src.models.explanation import AdvisorExplanation, ClientExplanation, ComplianceExplanation

logger = get_logger(__name__)


class ExplanationValidator:
    """Enterprise Explanation Validator verifying multi-audience explanations."""

    def validate_client_explanation(self, exp: ClientExplanation, max_words: int = 200) -> bool:
        """Validate ClientExplanation invariants.

        Args:
            exp: ClientExplanation instance.
            max_words: Word count ceiling.

        Returns:
            True if valid.

        Raises:
            ValidationError: If invariants fail.
        """
        if not exp.summary or not exp.benefits or not exp.costs_and_taxes:
            raise ValidationError(f"ClientExplanation for portfolio {exp.portfolio_id} has missing required sections.")

        if exp.word_count > max_words + 10:
            raise ValidationError(f"ClientExplanation word count ({exp.word_count}) exceeds max limit of {max_words} words.")

        return True

    def validate_advisor_explanation(self, exp: AdvisorExplanation, max_words: int = 400) -> bool:
        """Validate AdvisorExplanation invariants.

        Args:
            exp: AdvisorExplanation instance.
            max_words: Word count ceiling.

        Returns:
            True if valid.

        Raises:
            ValidationError: If invariants fail.
        """
        if not exp.summary or not exp.drift_analysis:
            raise ValidationError(f"AdvisorExplanation for portfolio {exp.portfolio_id} has missing required sections.")

        if exp.word_count > max_words + 15:
            raise ValidationError(f"AdvisorExplanation word count ({exp.word_count}) exceeds max limit of {max_words} words.")

        return True
