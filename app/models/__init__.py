"""Data models for ClaimFlow application."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DamageAnalysis(BaseModel):
    """Result from Vision agent."""
    damage_type: str
    severity: str
    estimated_cost: float
    confidence: float


class PolicyInfo(BaseModel):
    """Result from Policy agent."""
    policy_id: str
    deductible: float
    coverage_limit: float
    is_covered: bool
    coverage_details: str


class PayoutCalculation(BaseModel):
    """Result from Finance agent."""
    estimated_cost: float
    deductible: float
    payout_amount: float
    status: str


class ClaimRequest(BaseModel):
    """Claim submission request."""
    policy_id: str = Field(..., description="Policy ID")


class ClaimResponse(BaseModel):
    """Claim processing response."""
    claim_id: str
    damage_analysis: DamageAnalysis
    policy_info: PolicyInfo
    payout_calculation: PayoutCalculation
    pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "processed"
