"""Role-Based Access Control (RBAC) models and permissions."""

from typing import List
from pydantic import BaseModel, Field
from src.core.constants import StrEnum


class Role(StrEnum):
    """User roles for platform access control."""

    ADMIN = "ADMIN"
    ADVISOR = "ADVISOR"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    READ_ONLY = "READ_ONLY"


class UserSession(BaseModel):
    """User session context."""

    user_id: str = Field(..., description="User ID")
    role: Role = Field(..., description="Assigned role")
    token: str = Field(..., description="Session token")
