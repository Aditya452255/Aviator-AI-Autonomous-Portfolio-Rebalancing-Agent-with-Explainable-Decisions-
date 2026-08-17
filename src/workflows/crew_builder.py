"""Crew Builder defining CrewAI agent topologies, task sequences, and execution order."""

from typing import Dict, List, Optional
from src.agents.compliance_officer import ComplianceOfficerAgent
from src.agents.explanation_writer import ExplanationWriterAgent
from src.agents.orchestrator import OrchestratorAgent
from src.agents.portfolio_analyst import PortfolioAnalystAgent
from src.agents.risk_manager import RiskManagerAgent
from src.agents.tax_specialist import TaxSpecialistAgent
from src.core.logger import get_logger

logger = get_logger(__name__)


class CrewBuilder:
    """Enterprise CrewAI builder assembling specialized agent topologies."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}

        # Instantiate agents
        self.orchestrator = OrchestratorAgent(agent_config=self.config)
        self.analyst = PortfolioAnalystAgent(agent_config=self.config)
        self.risk_manager = RiskManagerAgent(agent_config=self.config)
        self.tax_specialist = TaxSpecialistAgent(agent_config=self.config)
        self.compliance_officer = ComplianceOfficerAgent(agent_config=self.config)
        self.explanation_writer = ExplanationWriterAgent(agent_config=self.config)

    def get_agent_sequence() -> List[str]:
        """Return ordered list of agent names in workflow topology."""
        return [
            "Portfolio Analyst",
            "Risk Manager",
            "Tax Specialist",
            "Compliance Officer",
            "Explanation Writer",
            "Orchestrator",
        ]
