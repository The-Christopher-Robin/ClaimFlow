"""Tests for Finance Agent."""
import pytest
from app.agents.finance import FinanceAgent
from app.models import DamageAnalysis, PolicyInfo


@pytest.mark.asyncio
async def test_finance_agent_approved_payout():
    """Test finance agent approves payout when covered."""
    agent = FinanceAgent()
    
    damage = DamageAnalysis(
        damage_type="collision",
        severity="moderate",
        estimated_cost=5000.0,
        confidence=0.95
    )
    
    policy = PolicyInfo(
        policy_id="POL001",
        deductible=500.0,
        coverage_limit=50000.0,
        is_covered=True,
        coverage_details="Covered"
    )
    
    result = await agent.calculate_payout(damage, policy)
    
    assert result.estimated_cost == 5000.0
    assert result.deductible == 500.0
    assert result.payout_amount == 4500.0  # 5000 - 500
    assert result.status == "approved"


@pytest.mark.asyncio
async def test_finance_agent_denied_not_covered():
    """Test finance agent denies when not covered."""
    agent = FinanceAgent()
    
    damage = DamageAnalysis(
        damage_type="vandalism",
        severity="moderate",
        estimated_cost=5000.0,
        confidence=0.95
    )
    
    policy = PolicyInfo(
        policy_id="POL003",
        deductible=250.0,
        coverage_limit=25000.0,
        is_covered=False,
        coverage_details="Not covered"
    )
    
    result = await agent.calculate_payout(damage, policy)
    
    assert result.payout_amount == 0.0
    assert result.status == "denied_not_covered"


@pytest.mark.asyncio
async def test_finance_agent_below_deductible():
    """Test finance agent when cost is below deductible."""
    agent = FinanceAgent()
    
    damage = DamageAnalysis(
        damage_type="hail",
        severity="minor",
        estimated_cost=300.0,
        confidence=0.90
    )
    
    policy = PolicyInfo(
        policy_id="POL001",
        deductible=500.0,
        coverage_limit=50000.0,
        is_covered=True,
        coverage_details="Covered"
    )
    
    result = await agent.calculate_payout(damage, policy)
    
    assert result.payout_amount == 0.0
    assert result.status == "denied_below_deductible"


@pytest.mark.asyncio
async def test_finance_agent_exceeds_coverage_limit():
    """Test finance agent caps payout at coverage limit."""
    agent = FinanceAgent()
    
    damage = DamageAnalysis(
        damage_type="total_loss",
        severity="total_loss",
        estimated_cost=30000.0,
        confidence=0.98
    )
    
    policy = PolicyInfo(
        policy_id="POL003",
        deductible=250.0,
        coverage_limit=25000.0,
        is_covered=True,
        coverage_details="Covered"
    )
    
    result = await agent.calculate_payout(damage, policy)
    
    # Should be capped at coverage limit
    assert result.payout_amount == 25000.0
    assert result.status == "approved"
