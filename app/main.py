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
            "damage