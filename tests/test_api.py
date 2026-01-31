"""Integration tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import io
from PIL import Image


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "ClaimFlow API is running"
    assert data["status"] == "healthy"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_process_claim_endpoint():
    """Test claim processing endpoint."""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Prepare request
    files = {"image": ("test_damage.png", img_bytes, "image/png")}
    data = {"policy_id": "POL001"}
    
    response = client.post("/api/claims/process", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    
    # Check response structure
    assert "claim_id" in result
    assert "damage_analysis" in result
    assert "policy_info" in result
    assert "payout_calculation" in result
    assert "pdf_path" in result
    
    # Check damage analysis
    assert result["damage_analysis"]["damage_type"] in ["collision", "hail", "flood", "fire", "vandalism"]
    assert result["damage_analysis"]["estimated_cost"] > 0
    
    # Check policy info
    assert result["policy_info"]["policy_id"] == "POL001"
    assert result["policy_info"]["deductible"] == 500.0
    
    # Check payout calculation
    assert "payout_amount" in result["payout_calculation"]
    assert "status" in result["payout_calculation"]


def test_process_claim_with_email():
    """Test claim processing with email."""
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    files = {"image": ("test_damage2.png", img_bytes, "image/png")}
    data = {
        "policy_id": "POL002",
        "email": "test@example.com"
    }
    
    response = client.post("/api/claims/process", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["policy_info"]["policy_id"] == "POL002"


def test_process_claim_missing_policy():
    """Test claim processing without policy ID."""
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    files = {"image": ("test.png", img_bytes, "image/png")}
    # Missing policy_id in data
    
    response = client.post("/api/claims/process", files=files)
    
    # Should get 422 Unprocessable Entity for missing required field
    assert response.status_code == 422
