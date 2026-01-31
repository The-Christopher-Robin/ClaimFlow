"""Tests for Policy Agent."""
import pytest
from app.agents.policy import PolicyAgent


@pytest.mark.asyncio
async def test_policy_agent_known_policy():
    """Test policy agent with known policy."""
    agent = PolicyAgent()
    
    result = await agent.get_policy_info("POL001", "collision")
    
    assert result.policy_id == "POL001"
    assert result.deductible == 500.0
    assert result.coverage_limit == 50000.0
    assert result.is_covered is True
    assert "covered" in result.coverage_details.lower()


@pytest.mark.asyncio
async def test_policy_agent_not_covered():
    """Test policy agent with damage not covered."""
    agent = PolicyAgent()
    
    # POL003 doesn't cover vandalism
    result = await agent.get_policy_info("POL003", "vandalism")
    
    assert result.policy_id == "POL003"
    assert result.is_covered is False
    assert "NOT covered" in result.coverage_details


@pytest.mark.asyncio
async def test_policy_agent_unknown_policy():
    """Test policy agent with unknown policy ID."""
    agent = PolicyAgent()
    
    result = await agent.get_policy_info("POL999", "collision")
    
    # Should return default policy
    assert result.policy_id == "POL999"
    assert result.deductible == 500.0
    assert result.coverage_limit == 50000.0


@pytest.mark.asyncio
async def test_policy_agent_all_policies():
    """Test all known policies."""
    agent = PolicyAgent()
    
    policies = ["POL001", "POL002", "POL003"]
    
    for policy_id in policies:
        result = await agent.get_policy_info(policy_id, "collision")
        assert result.policy_id == policy_id
        assert result.deductible > 0
        assert result.coverage_limit > 0
