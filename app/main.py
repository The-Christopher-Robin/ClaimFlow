"""
ClaimFlow Micro-Skills API
Designed for IBM watsonx Orchestrate Integration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
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

# --- CONFIGURATION (YOUR PUBLIC URL) ---
# This is the URL from your Code Engine screenshot
BASE_URL = "https://claimflow-backend.25rar0221uf4.us-south.codeengine.appdomain.cloud"

# --- DATA MODELS ---

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
    
    # Logic: Return different results based on keywords in the filename
    name_lower = image_name.lower()
    if "total" in name_lower or "heavy" in name_lower:
        return {
            "damage_type": "Major Frontal Collision",
            "severity": "High",
            "estimated_cost": 4500.0,
            "confidence": 0.98
        }
    elif "scratch" in name_lower:
        return {
            "damage_type": "Paint Scratch",
            "severity": "Low",
            "estimated_cost": 350.0,
            "confidence": 0.85
        }
    else:
        # Default case
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
    amount = data.repair_cost - data.deductible
    if amount < 0: 
        amount = 0.0
    
    # Generate a Mock Offer ID
    offer_id = uuid.uuid4().hex[:8].upper()
    
    return {
        "final_payout": amount,
        "status": "Approved" if amount > 0 else "Denied",
        # We point this URL to our new PDF generator endpoint below
        "offer_letter_url": f"{BASE_URL}/api/claims/{offer_id}/pdf"
    }

# SKILL 3: PDF Generator (The Paperwork)
@app.post("/tools/generate-pdf", summary="Generate Offer Letter")
def generate_pdf_tool(data: PDFRequest):
    """
    Generates the official PDF offer letter link.
    """
    # Create a unique ID
    offer_id = uuid.uuid4().hex[:8]
    
    # CRITICAL FIX: Return the Full Public URL
    download_link = f"{BASE_URL}/api/claims/{offer_id}/pdf"
    
    return {
        "message": "PDF Generated Successfully",
        "filename": f"claim_{offer_id}.pdf",
        "download_url": download_link
    }

# --- THE RECEIPT ENDPOINT (Makes the link work) ---
@app.get("/api/claims/{offer_id}/pdf")
def get_offer_pdf(offer_id: str):
    """
    Serves a text receipt that looks like a PDF for the demo.
    """
    content = f"""
    =========================================
          OFFICIAL CLAIMFLOW RECEIPT
    =========================================
    
    CLAIM ID: {offer_id}
    DATE:     {datetime.now().strftime("%Y-%m-%d")}
    STATUS:   APPROVED
    
    -----------------------------------------
    Thank you for using ClaimFlow. 
    Your payout assessment is complete.
    
    Please retain this document for your records.
    
    [Authorized Signature]
    IBM watsonx Orchestrate Agent
    =========================================
    """
    return PlainTextResponse(content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)