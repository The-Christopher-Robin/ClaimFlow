"""Finance Agent - Calculates payout based on damage and policy."""
from app.models import PayoutCalculation, DamageAnalysis, PolicyInfo


class FinanceAgent:
    """Finance agent that calculates claim payout."""
    
    async def calculate_payout(
        self,
        damage_analysis: DamageAnalysis,
        policy_info: PolicyInfo
    ) -> PayoutCalculation:
        """
        Calculate payout amount.
        
        Formula: payout = min(estimated_cost - deductible, coverage_limit)
        Only pays if damage is covered.
        """
        estimated_cost = damage_analysis.estimated_cost
        deductible = policy_info.deductible
        
        if not policy_info.is_covered:
            payout_amount = 0.0
            status = "denied_not_covered"
        else:
            # Calculate payout: cost - deductible, capped at coverage limit
            payout_before_limit = max(0, estimated_cost - deductible)
            payout_amount = min(payout_before_limit, policy_info.coverage_limit)
            
            if payout_amount > 0:
                status = "approved"
            else:
                status = "denied_below_deductible"
        
        return PayoutCalculation(
            estimated_cost=estimated_cost,
            deductible=deductible,
            payout_amount=round(payout_amount, 2),
            status=status
        )
