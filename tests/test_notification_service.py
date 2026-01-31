"""Tests for Notification Service."""
import pytest
from app.services.notification_service import NotificationService
from app.models import ClaimResponse, DamageAnalysis, PolicyInfo, PayoutCalculation
from datetime import datetime


@pytest.mark.asyncio
async def test_notification_service_email_stub():
    """Test email notification stub."""
    service = NotificationService()
    
    claim = ClaimResponse(
        claim_id="test-claim-456",
        damage_analysis=DamageAnalysis(
            damage_type="hail",
            severity="minor",
            estimated_cost=1500.0,
            confidence=0.92
        ),
        policy_info=PolicyInfo(
            policy_id="POL002",
            deductible=1000.0,
            coverage_limit=100000.0,
            is_covered=True,
            coverage_details="Covered"
        ),
        payout_calculation=PayoutCalculation(
            estimated_cost=1500.0,
            deductible=1000.0,
            payout_amount=500.0,
            status="approved"
        ),
        created_at=datetime.now()
    )
    
    # Test email stub (should always return True)
    result = await service.send_email_notification(claim, "test@example.com")
    assert result is True


@pytest.mark.asyncio
async def test_notification_service_slack_no_webhook():
    """Test Slack notification without webhook configured."""
    service = NotificationService()
    
    claim = ClaimResponse(
        claim_id="test-claim-789",
        damage_analysis=DamageAnalysis(
            damage_type="flood",
            severity="severe",
            estimated_cost=12000.0,
            confidence=0.88
        ),
        policy_info=PolicyInfo(
            policy_id="POL001",
            deductible=500.0,
            coverage_limit=50000.0,
            is_covered=True,
            coverage_details="Covered"
        ),
        payout_calculation=PayoutCalculation(
            estimated_cost=12000.0,
            deductible=500.0,
            payout_amount=11500.0,
            status="approved"
        ),
        created_at=datetime.now()
    )
    
    # Without webhook URL, should return False
    result = await service.send_slack_notification(claim)
    assert result is False


@pytest.mark.asyncio
async def test_notification_service_notify_all():
    """Test notify_all method."""
    service = NotificationService()
    
    claim = ClaimResponse(
        claim_id="test-claim-all",
        damage_analysis=DamageAnalysis(
            damage_type="fire",
            severity="severe",
            estimated_cost=15000.0,
            confidence=0.97
        ),
        policy_info=PolicyInfo(
            policy_id="POL002",
            deductible=1000.0,
            coverage_limit=100000.0,
            is_covered=True,
            coverage_details="Covered"
        ),
        payout_calculation=PayoutCalculation(
            estimated_cost=15000.0,
            deductible=1000.0,
            payout_amount=14000.0,
            status="approved"
        ),
        created_at=datetime.now()
    )
    
    results = await service.notify_all(claim, "customer@example.com")
    
    assert "slack" in results
    assert "email" in results
    assert results["email"] is True  # Email stub always succeeds
