"""Tests for PDF Service."""
import pytest
import os
from datetime import datetime
from app.services.pdf_service import PDFService
from app.models import ClaimResponse, DamageAnalysis, PolicyInfo, PayoutCalculation


def test_pdf_service_generate_offer_letter(tmp_path):
    """Test PDF generation."""
    # Use temporary directory for output
    pdf_service = PDFService(output_dir=str(tmp_path))
    
    # Create a sample claim
    claim = ClaimResponse(
        claim_id="test-claim-123",
        damage_analysis=DamageAnalysis(
            damage_type="collision",
            severity="moderate",
            estimated_cost=5000.0,
            confidence=0.95
        ),
        policy_info=PolicyInfo(
            policy_id="POL001",
            deductible=500.0,
            coverage_limit=50000.0,
            is_covered=True,
            coverage_details="Damage is covered"
        ),
        payout_calculation=PayoutCalculation(
            estimated_cost=5000.0,
            deductible=500.0,
            payout_amount=4500.0,
            status="approved"
        ),
        created_at=datetime.now()
    )
    
    # Generate PDF
    pdf_path = pdf_service.generate_offer_letter(claim)
    
    # Check PDF was created
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")
    assert "test-claim-123" in pdf_path
    
    # Check file is not empty
    assert os.path.getsize(pdf_path) > 0
