"""Tests for Vision Agent."""
import pytest
from app.agents.vision import VisionAgent
from io import BytesIO


@pytest.mark.asyncio
async def test_vision_agent_analyze_damage():
    """Test vision agent can analyze damage."""
    agent = VisionAgent()
    
    # Create a mock image file
    mock_image = BytesIO(b"fake image data")
    
    result = await agent.analyze_damage(mock_image)
    
    # Check that result has expected fields
    assert result.damage_type in ["Collision", "Hail", "Flood", "Fire", "Vandalism"]
    assert result.severity in ["minor", "moderate", "severe", "total_loss"]
    assert result.estimated_cost > 0
    assert 0 <= result.confidence <= 1


@pytest.mark.asyncio
async def test_vision_agent_cost_ranges():
    """Test that estimated costs are within expected ranges for severity."""
    agent = VisionAgent()
    mock_image = BytesIO(b"fake image data")
    
    # Run multiple times to test different severities
    results = []
    for _ in range(20):
        result = await agent.analyze_damage(mock_image)
        results.append(result)
    
    # Check that we got some variety in results
    severities = set(r.severity for r in results)
    assert len(severities) > 1  # Should have different severities
    
    # Check costs are reasonable
    for result in results:
        assert 500 <= result.estimated_cost <= 50000
