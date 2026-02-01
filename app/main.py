"""
ClaimFlow Micro-Skills API
Designed for IBM watsonx Orchestrate Integration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClaimFlow Tools",
    description="Micro-skills for IBM watsonx Agent",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("output", exist_ok=True)

# --- DATA MODELS (The Language of your Agent) ---

class DamageAnalysis(BaseModel):
    damage_type: str
    severity: str
    estimated_cost: float
    confidence: float

class PayoutRequest(BaseModel):
    repair_cost: float
    deductible: float
    policy_id: str

class PayoutResponse(BaseModel):
    final_payout: float
    status: str
    offer_letter_url: str

class PDFRequest(BaseModel):
    claim_id: str
    policy_id: str
    final_amount: float
    damage_type: str

# --- THE SKILLS (Endpoints for Watsonx) ---

@app.get("/")
def health_check():
    """Keep-alive endpoint for IBM Code Engine."""
    return {"status": "ClaimFlow Skills Active", "timestamp": datetime.now().isoformat()}

# SKILL 1: Vision (The Eyes)
@app.post("/tools/analyze-image", response_model=DamageAnalysis, summary="Analyze Car Damage")
async def analyze_image_tool(image_name: str = "crash.jpg"):
    """
    Simulates analyzing a car photo.
    Input: Image filename or URL.
    Output: Damage details and cost estimate.
    """
    logger.info(f"Analyzing image: {image_name}")
    
    # Hackathon Logic: Return different results based on keywords in the filename
    if "heavy" in image_name.lower() or "total" in image_name.lower():
        return {
            "damage_type": "Major Frontal Collision",
            "severity": "High",
            "estimated_cost": 4500.0,
            "confidence": 0.98
        }
    elif "scratch" in image_name.lower():
        return {
            "damage_type": "Paint Scratch",
            "severity": "Low",
            "estimated_cost": 350.0,
            "confidence": 0.85
        }
    else:
        # Default case (The Bumper Dent)
        return {
            "damage_type": "Front Bumper Dent",
            "severity": "Medium",
            "estimated_cost": 850.0,
            "confidence": 0.95
        }

# SKILL 2: Finance (The Calculator)
@app.post("/tools/calculate-payout", response_model=PayoutResponse, summary="Calculate Final Payout")
def calculate_payout_tool(data: PayoutRequest):
    """
    Calculates the final check amount.
    """
    logger.info(f"Calculating payout for Policy {data.policy_id}")
    
    amount = data.repair_cost - data.deductible
    
    # Logic: Cannot have negative payout
    if amount < 0:
        return {
            "final_payout": 0.0,
            "status": "Denied (Below Deductible)",
            "offer_letter_url": "N/A"
        }
    
    # In a real app, this URL would point to a generated PDF
    # For Hackathon, we return a mock URL or use the PDF tool
    return {
        "final_payout": amount,
        "status": "Approved",
        "offer_letter_url": f"https://claimflow.ibm.com/offers/{data.policy_id}_{uuid.uuid4().hex[:8]}.pdf"
    }

# SKILL 3: PDF Generator (The Paperwork)
@app.post("/tools/generate-pdf", summary="Generate Offer Letter")
def generate_pdf_tool(data: PDFRequest):
    """
    Generates the official PDF offer letter.
    """
    # Create a unique ID
    offer_id = uuid.uuid4().hex
    filename = f"claim_{offer_id}_offer.pdf"
    
    # Logic: We are mocking the file creation for speed, 
    # but in a real app, you would use reportlab here.
    return {
        "message": "PDF Generated Successfully",
        "filename": filename,
        "download_url": f"/api/claims/{offer_id}/pdf"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)