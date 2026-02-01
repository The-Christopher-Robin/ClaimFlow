"""Policy Agent - RAG over policy documents using watsonx Discovery (stub)."""
from app.models import PolicyInfo
import random


class PolicyAgent:
    """
    Policy agent that retrieves policy information.
    
    Stub implementation - would integrate with IBM watsonx Discovery
    for RAG over policy.pdf in production.
    """
    
    def __init__(self):
        # Mock policy database
        self.policies = {
            "POL001": {
                "deductible": 500.0,
                "coverage_limit": 50000.0,
                "covered_damages": ["collision", "hail", "flood", "fire"]
            },
            "POL002": {
                "deductible": 1000.0,
                "coverage_limit": 100000.0,
                "covered_damages": ["collision", "hail", "flood", "fire", "vandalism"]
            },
            "POL003": {
                "deductible": 250.0,
                "coverage_limit": 25000.0,
                "covered_damages": ["collision", "hail"]
            }
        }
    
    async def get_policy_info(self, policy_id: str, damage_type: str) -> PolicyInfo:
        """
        Retrieve policy information and check coverage.
        
        In production, this would use watsonx Discovery to perform
        RAG over policy documents.
        """
        # Check if policy exists
        if policy_id in self.policies:
            policy = self.policies[policy_id]
        else:
            # Default policy for demo purposes
            policy = {
                "deductible": 500.0,
                "coverage_limit": 50000.0,
                "covered_damages": ["collision", "hail", "flood", "fire"]
            }
        
        is_covered = damage_type in policy["covered_damages"]
        
        if is_covered:
            coverage_details = f"Damage type '{damage_type}' is covered under your policy."
        else:
            coverage_details = f"Damage type '{damage_type}' is NOT covered under your policy."
        
        return PolicyInfo(
            policy_id=policy_id,
            deductible=policy["deductible"],
            coverage_limit=policy["coverage_limit"],
            is_covered=is_covered,
            coverage_details=coverage_details
        )
